import socket
import select
import json
import logging
import threading
import queue
import time
from typing import Optional, Callable, Dict, Any, List

class Messenger:
    def __init__(
        self,
        socket_server: str,
        socket_client: str,
        connection_retry_interval: float = 1.0,
        connection_timeout: float = 30.0
    ):
        """
        Initialize asynchronous Unix domain socket client.
       
        Args:
            socket_server: Path to the server Unix domain socket
            socket_client: Path to the client Unix domain socket
            connection_retry_interval: Time between connection attempts in seconds
            connection_timeout: Maximum time to wait for connection in seconds
        """
        self.socket_server = socket_server
        self.socket_client = socket_client
        self.connection_retry_interval = connection_retry_interval
        self.connection_timeout = connection_timeout
        self.listeners: Dict[str, List[Callable[[dict], None]]] = {}
        self.sock: Optional[socket.socket] = None
        self.running = False
        self.send_queue = queue.Queue()
       
        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
       
        # Buffer for incoming data
        self.recv_buffer = b''
       
    def wait_for_socket(self) -> bool:
        """
        Wait for the socket to become available.
       
        Returns:
            bool: True if socket becomes available, False if timeout reached
        """
        start_time = time.time()
        attempt = 1
       
        while True:
            self.logger.info(f"Connection attempt {attempt}")
            try:
                if self.connect():
                    return True
                   
            except socket.error as e:
                elapsed_time = time.time() - start_time
                if elapsed_time >= self.connection_timeout:
                    self.logger.error("Connection timeout reached")
                    return False
                   
                self.logger.warning(
                    f"Socket not available, retrying in {self.connection_retry_interval} seconds. "
                    f"Error: {e}"
                )
                time.sleep(self.connection_retry_interval)
                attempt += 1
       
    def connect(self) -> bool:
        """
        Establish connection to the Unix domain socket.
       
        Returns:
            bool: True if connection successful, False otherwise
        """
        if self.sock is not None:
            self.sock.close()
            
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.sock.bind(self.socket_client)
        self.sock.setblocking(False)

        # Try sending a test message to verify connection
        self.sock.sendto(b'', self.socket_server)
        self.logger.info(f"Connected to socket at {self.socket_server}")

        return True

    def start(self):
        """
        Start the async I/O handling thread.
       
        Raises:
            ConnectionError: If unable to establish connection within timeout period
        """
        if self.running:
            return
           
        if not self.wait_for_socket():
            raise ConnectionError(
                f"Failed to connect to socket after {self.connection_timeout} seconds"
            )
           
        self.running = True
        self.io_thread = threading.Thread(target=self._io_loop)
        self.io_thread.daemon = True
        self.io_thread.start()
       
    def stop(self):
        """Stop the async I/O handling thread."""
        self.running = False
        if hasattr(self, 'io_thread') and self.io_thread:
            self.io_thread.join()
        if self.sock:
            self.sock.close()
            self.sock = None
           
    def send_message(self, message: Dict[str, Any]):
        """
        Queue a message to be sent.
       
        Args:
            message: Dictionary to be sent as JSON
        """
        self.send_queue.put(message)
       
    def _io_loop(self):
        """Main I/O loop handling both sending and receiving."""
        while self.running:
            try:
                readable, writable, _ = select.select(
                    [self.sock],
                    [self.sock] if not self.send_queue.empty() else [],
                    [],
                    0.1  # Small timeout to prevent busy waiting
                )
               
                # Handle incoming messages
                if readable:
                    try:
                        data, _ = self.sock.recvfrom(4096)
                        if not data:  # Connection closed
                            self.logger.warning("Server closed connection")
                            break

                        self.handle_received_data(data)
                           
                    except socket.error as e:
                        self.logger.error(f"Error receiving data: {e}")
                        break
                       
                # Handle outgoing messages
                if writable:
                    try:
                        message = self.send_queue.get_nowait()
                        data = json.dumps(message).encode('utf-8') + b'\n' # Use newline as message delimiter
                        self.sock.sendto(data, self.socket_client)
                    except queue.Empty:
                        pass
                    except socket.error as e:
                        self.logger.error(f"Error sending data: {e}")
                        break
                       
            except Exception as e:
                self.logger.error(f"Error in I/O loop: {e}")
                break
               
        self.running = False
        self.sock.close()
        self.sock = None
       
    def parse_buffer(self) -> list[dict]:
        """
        Parse buffer for complete JSON messages.
        
        Returns:
            list[dict]: List of parsed JSON messages
        """
        messages = []
        try:
            # Convert buffer to string
            data = self.recv_buffer.decode('utf-8')
            # Find complete messages
            while True:
                try:
                    # Try to decode a complete JSON object
                    message, index = json.JSONDecoder().raw_decode(data)
                    messages.append(message)
                    # Remove processed data from buffer
                    data = data[index:].lstrip()
                    if not data:
                        break
                except json.JSONDecodeError:
                    break
                    
            # Update buffer with remaining incomplete data
            self.recv_buffer = data.encode('utf-8')
            
        except UnicodeDecodeError:
            # Keep buffer unchanged if decode fails
            pass
            
        return messages

    def handle_received_data(self, data: bytes) -> None:
        """
        Handle received socket data.
        
        Args:
            data: Raw bytes received from socket
        """
        self.recv_buffer = self.recv_buffer + data
        
        # Process all complete messages in buffer
        for message in self.parse_buffer():
            try:
                # Extract message type from the message
                message_type = message.get('type')
                if message_type and message_type in self.listeners:
                    for callback in self.listeners[message_type]:
                        try:
                            callback(message)
                        except Exception as e:
                            self.logger.error(f"Error in listener callback: {e}")
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
               
    def add_listener(self, message_type: str, callback: Callable[[dict], None]) -> None:
        """
        Add a listener for a specific message type.
        
        Args:
            message_type: Type of message to listen for
            callback: Function to call when message is received
        """
        if message_type not in self.listeners:
            self.listeners[message_type] = []
        self.listeners[message_type].append(callback)

    def remove_listener(self, message_type: str, callback: Callable[[dict], None]) -> bool:
        """
        Remove a listener for a specific message type.
        
        Args:
            message_type: Type of message to remove listener from
            callback: Callback function to remove
            
        Returns:
            bool: True if listener was removed, False if not found
        """
        if message_type in self.listeners and callback in self.listeners[message_type]:
            self.listeners[message_type].remove(callback)
            if not self.listeners[message_type]:
                del self.listeners[message_type]
            return True
        return False
               
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
       
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
