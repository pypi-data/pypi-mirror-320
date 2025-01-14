"""
Core implementation of the Kradle Minecraft agent.
Provides agent functionality with clean tunnel integration.
"""
from typing import Optional, List, Dict, Any, Tuple, Union
import threading
import time
import logging
import os
import sys
import socket
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import signal
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from werkzeug.serving import WSGIRequestHandler, make_server
from kradle.models import Observation
from kradle.ssh_tunnel import create_tunnel
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable Flask logging for cleaner output
logging.getLogger('werkzeug').disabled = True
logging.getLogger('flask.app').disabled = True
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

class ServerStartupError(Exception):
    """Raised when server fails to start properly."""
    pass

class TunnelError(Exception):
    """Raised when tunnel creation fails."""
    pass

class KradleMinecraftAgent:
    """Base class for Kradle Minecraft agents"""
    
    def __init__(self, slug: str, action_delay: int = 5000):
        # Basic configuration
        self.slug = slug
        self.action_delay = action_delay
        self.console = Console()
        
        # State management
        self.task: Optional[str] = None
        self.docs: Optional[Dict] = None
        self.skills: Optional[Dict] = None
        self.port: Optional[int] = None
        self.url: Optional[str] = None
        
        # Thread synchronization
        self._shutdown_event = threading.Event()
        self._server_ready = threading.Event()
        
        # Server and tunnel management
        self._server = None
        self._server_thread: Optional[threading.Thread] = None
        self._tunnel = None
        
        # Create Flask app
        self._app = self._create_app()
        
        # Styling
        self._agent_colors = ["cyan", "magenta", "green", "yellow", "blue", "red", "white"]
        self.color = self._agent_colors[hash(slug) % len(self._agent_colors)]
        
    def _create_app(self) -> Flask:
        """Create and configure Flask application."""
        app = Flask(__name__)
        app.logger.disabled = True
        CORS(app)
        
        @app.route('/ping')
        def health_check():
            return 'pong'
        
        @app.route('/init', methods=['POST'])
        def initialize_agent():
            try:
                data = request.get_json()
                self.task = data.get('task')
                self.docs = data.get('docs')
                self.skills = data.get('skills')
                events = self.on_init()
                self.console.print(Panel(f"[green]Agent initialized with task: {self.task}[/green]"))
                return jsonify({"choices": events})
            except Exception as e:
                logger.error(f"Initialization error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @app.route('/event', methods=['POST'])
        def handle_event():
            try:
                data = request.get_json()
                state = Observation.from_event(data)
                self._display_state(state)
                
                result = self.on_event(state)
                self.console.print("\n[bold green]Action:[/bold green]")
                self.console.print(f"[yellow]{result}[/yellow]")
                
                if isinstance(result, str) and "```javascript" in result:
                    return jsonify({"code": result, "delay": self.action_delay})
                return jsonify({"command": result, "delay": self.action_delay})
            except Exception as e:
                logger.error(f"Event handling error: {e}")
                return jsonify({"error": str(e)}), 500
        
        return app
    
    def _display_state(self, state: Observation) -> None:
        """Display current agent state in console with distinct agent styling."""
        header = f"[bold {self.color}]{'='*20} Agent: {self.slug} {'='*20}[/bold {self.color}]"
        timestamp = time.strftime('%H:%M:%S')
        
        table = Table(
            box=box.ROUNDED, 
            show_header=False, 
            padding=(0, 1),
            border_style=self.color
        )
        table.add_column("Category", style=self.color)
        table.add_column("Value", style="bright_" + self.color)
        
        self.console.print("\n")
        self.console.print(header)
        self.console.print(f"[{self.color}]Event Received at {timestamp} (Port: {self.port})[/{self.color}]")
        
        table.add_row("Position", f"x: {state.x:.2f}, y: {state.y:.2f}, z: {state.z:.2f}")
        table.add_row("Inventory", ", ".join(state.inventory) if state.inventory else "empty")
        table.add_row("Equipped", state.equipped if state.equipped else "nothing")
        table.add_row("Entities", ", ".join(state.entities) if state.entities else "none")
        table.add_row("Blocks", ", ".join(state.blocks) if state.blocks else "none")
        table.add_row("Craftable", ", ".join(state.craftable) if state.craftable else "none")
        
        self.console.print(table)
    
    def _handle_tunnel_status(self, url: str) -> None:
        """Display local and tunnel URLs with agent-specific styling."""
        self.console.print(f"\n[bold {self.color}]=== {self.slug} Connection Info ===[/bold {self.color}]")
        self.console.print(f"[{self.color}]Local URL: http://localhost:{self.port}[/{self.color}]")
        self.console.print(f"[{self.color}]Public URL: {url}[/{self.color}]")
    
    def _is_port_available(self, port: Optional[int] = None) -> bool:
        """Check if a specific port is available."""
        check_port = port if port is not None else self.port
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', check_port))
                return True
        except OSError:
            return False

    def _find_free_port(self, start_port: int = 1500, end_port: int = 1549) -> int:
        """Find a free port within the specified range."""
        for port in range(start_port, end_port + 1):
            if self._is_port_available(port):
                return port
        raise RuntimeError(f"No free ports available in range {start_port}-{end_port}")

    def _run_server(self):
        """Run the Flask server in a separate thread."""
        try:
            self._server = make_server('localhost', self.port, self._app)
            self.console.print("[cyan]Launching Agent![/cyan]")
            self._server_ready.set()
            self._server.serve_forever()
        except Exception as e:
            logger.error(f"Server error: {e}")
            self._shutdown_event.set()
            raise

    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def handle_shutdown(signum, frame):
            logger.info("Received shutdown signal")
            self.shutdown()
        
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

    def shutdown(self):
        """Graceful shutdown sequence."""
        logger.info("Starting graceful shutdown")
        self._shutdown_event.set()
        
        if self._server:
            try:
                self._server.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down server: {e}")
        
        if self._tunnel:
            try:
                self._tunnel.stop()
            except Exception as e:
                logger.error(f"Error stopping tunnel: {e}")
        
        # Give threads a moment to clean up
        time.sleep(0.5)
        sys.exit(0)

    @contextmanager
    def _server_lifecycle(self):
        """Context manager for server lifecycle."""
        try:
            self._server_thread = threading.Thread(target=self._run_server, daemon=True)
            self._server_thread.start()
            
            if not self._server_ready.wait(timeout=5.0):
                raise ServerStartupError("Server failed to start within timeout")
            
            yield
        finally:
            if not self._shutdown_event.is_set():
                self.shutdown()

    def start(self, port: Optional[int] = None) -> Optional[str]:
        """Start the agent server and tunnel with proper thread management."""
        try:
            # Initialize port
            self.port = port if port is not None else self._find_free_port()
            if not self._is_port_available():
                self.console.print(f"\n[red]Error: Port {self.port} is not available[/red]")
                return None

            # Set up signal handlers
            self._setup_signal_handlers()
            
            # Start server thread
            self._server_thread = threading.Thread(target=self._run_server, daemon=True)
            self._server_thread.start()
            
            # Wait for server to be ready
            if not self._server_ready.wait(timeout=5.0):
                raise ServerStartupError("Server failed to start within timeout")
            
            # Create tunnel once server is ready
            self._tunnel, url = create_tunnel(self.port)
            if not self._tunnel:
                raise TunnelError("Failed to establish tunnel")
            
            self.url = url
            self._handle_tunnel_status(url)
            self.console.print("\nServer is running. Keep this window open while the agent is active.")
            self.console.print("Press Ctrl+C to stop the agent.\n")
            
            # Start a keep-alive thread instead of blocking
            def keep_alive():
                try:
                    self._shutdown_event.wait()
                finally:
                    if not self._shutdown_event.is_set():
                        self.shutdown()

            self._main_thread = threading.Thread(target=keep_alive, daemon=False)
            self._main_thread.start()
            
            return url

        except Exception as e:
            logger.error(f"Startup error: {e}")
            self.console.print(f"[red]Error: {str(e)}[/red]")
            self.shutdown()
            return None
    
    def on_init(self) -> List[str]:
        """Called when agent is initialized. Override in subclass."""
        return []
    
    def on_event(self, state: Observation) -> str:
        """Process the current state and return an action. Must be implemented by subclasses."""
        raise NotImplementedError("Agents must implement on_event() method")
    
def create_session(api_key: str, challenge_slug: str, agents: Union[KradleMinecraftAgent, List[KradleMinecraftAgent]]) -> Optional[str]:
    """Create a new challenge session for one or more agents."""
    console = Console()
    logger = logging.getLogger(__name__)
    
    # Environment-specific URLs
    KRADLE_APP_URL = (
        "http://localhost:3000" 
        if os.getenv("KRADLE_DEV") 
        else "https://mckradleai.vercel.app"
    )
    KRADLE_APP_LIVE_SESSION_URL = "https://mckradleai-git-jt-session-map-kradle-f5bad6db.vercel.app/session-map"
    
    try:
        # Normalize agents to list
        agent_list = [agents] if not isinstance(agents, list) else agents
        
        # Validate agents
        for agent in agent_list:
            if not agent.url:
                raise ValueError(f"Agent {agent.slug} is not properly started")
            if not hasattr(agent, 'slug'):
                raise ValueError("Agent has no slug defined")
        
        # Prepare session data
        agent_data = [
            {
                'agentSlug': agent.slug,
                'agentUrl': agent.url
            }
            for agent in agent_list
        ]
        
        console.print("Launching session...")
        
        # Make API request
        response = requests.post(
            f'{KRADLE_APP_URL}/api/createSession',
            headers={
                'Content-Type': 'application/json',
                'kradle-api-key': api_key
            },
            json={
                'challengeSlug': challenge_slug,
                'agents': agent_data
            },
            timeout=30
        )
        
        if response.status_code in (200, 201):
            session_id = response.json()['sessionId']
            console.print("\nSession launched successfully!", style="bold green")
            session_url = f"{KRADLE_APP_LIVE_SESSION_URL}/{session_id}?_vercel_share=9GXlpNbfQWUP6jjM3VZ3RL9WRMT4qJVx"
            console.print(f"\nView it live: {session_url}")
            return session_id
            
        response.raise_for_status()
        
    except Exception as e:
        logger.error(f"Session creation failed: {e}")
        # Shutdown all agents
        for agent in agent_list:
            try:
                agent.shutdown()
            except:
                pass
        
        if isinstance(e, requests.RequestException):
            console.print(
                f"\n[yellow]Unable to reach Kradle Workbench at {KRADLE_APP_URL}\n"
                "Please try again in a few minutes.[/yellow]"
            )
        else:
            console.print(f"[red]Error: {str(e)}[/red]")
        
        sys.exit(1)
    
    return None