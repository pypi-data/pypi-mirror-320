import unittest
import socket
import tempfile
import os
import threading
import time
from unittest.mock import Mock, patch
from wmk.messenger import Messenger

class TestServer:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.running = False
        self.shutdown_event = threading.Event()
    
    def start(self):
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        self.sock.bind(self.socket_path)
        self.sock.settimeout(1)  # Add timeout
        self.running = True
        self.thread = threading.Thread(target=self._accept_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        self.running = False
        self.shutdown_event.set()
        if self.sock:
            self.sock.close()
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1.0)
    
    def _accept_loop(self):
        while self.running and not self.shutdown_event.is_set():
            try:
                data, client_addr = self.sock.recvfrom(4096)
                print("Server: received data:", data)
                if not data:
                    break
                self.sock.sendto(data, client_addr)
            except socket.timeout:
                continue
            except Exception as e:
                print("Server: error:", str(e))
                break

class TestMessenger(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.server_socket = os.path.join(self.temp_dir, "test_server.sock")
        self.client_socket = os.path.join(self.temp_dir, "test_client.sock")
        self.received_messages = []
        self.server = TestServer(self.server_socket)
        self.server.start()
        time.sleep(0.1)  # Allow server to start
        
        self.messenger = Messenger(
            socket_server=self.server_socket,
            socket_client=self.client_socket,
            connection_retry_interval=0.1
        )
        if not self.server.running:
            self.fail("Server failed to start")

    def tearDown(self):
        if hasattr(self, 'messenger'):
            self.messenger.stop()
        if hasattr(self, 'server'):
            self.server.stop()
        for socket_file in [self.server_socket, self.client_socket]:
            if os.path.exists(socket_file):
                try:
                    os.unlink(socket_file)
                except:
                    pass
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            try:
                os.rmdir(self.temp_dir)
            except:
                pass

    def test_connection(self):
        """Test real socket connection"""
        result = self.messenger._wait_for_socket()
        self.assertTrue(result)
        self.assertIsNotNone(self.messenger.sock)

    def test_send_receive_message(self):
        """Test sending and receiving real messages"""
        self.messenger.start()
        received_messages = []
        
        def test_callback(message):
            received_messages.append(message)
            
        self.messenger.add_listener("test_type", test_callback)
        test_message = {"type": "test_type", "data": "test_data"}
        self.messenger.send_message(test_message)
        
        time.sleep(0.5)
        
        self.assertEqual(len(received_messages), 1)
        self.assertEqual(received_messages[0], test_message)

    def test_multiple_listeners(self):
        """Test multiple listeners for same message type"""
        self.messenger.start()
        messages_1 = []
        messages_2 = []
        
        def callback_1(message):
            messages_1.append(message)
            
        def callback_2(message):
            messages_2.append(message)
            
        self.messenger.add_listener("test_type", callback_1)
        self.messenger.add_listener("test_type", callback_2)
        
        test_message = {"type": "test_type", "data": "test"}
        self.messenger.send_message(test_message)
        
        time.sleep(0.5)
        
        self.assertEqual(len(messages_1), 1)
        self.assertEqual(len(messages_2), 1)
        self.assertEqual(messages_1[0], test_message)
        self.assertEqual(messages_2[0], test_message)

    def test_remove_listener(self):
        """Test removing a listener"""
        self.messenger.start()
        received_messages = []
        
        def test_callback(message):
            received_messages.append(message)
            
        self.messenger.add_listener("test_type", test_callback)
        test_message = {"type": "test_type", "data": "test"}
        
        # Send message with listener
        self.messenger.send_message(test_message)
        time.sleep(0.5)
        self.assertEqual(len(received_messages), 1)
        
        # Remove listener and send again
        self.messenger.remove_listener("test_type", test_callback)
        self.messenger.send_message(test_message)
        time.sleep(0.5)
        self.assertEqual(len(received_messages), 1)  # Count shouldn't change

    def test_multiple_message_types(self):
        """Test handling different message types"""
        self.messenger.start()
        type1_messages = []
        type2_messages = []
        
        def type1_callback(message):
            type1_messages.append(message)
            
        def type2_callback(message):
            type2_messages.append(message)
            
        self.messenger.add_listener("type1", type1_callback)
        self.messenger.add_listener("type2", type2_callback)
        
        msg1 = {"type": "type1", "data": "test1"}
        msg2 = {"type": "type2", "data": "test2"}
        
        self.messenger.send_message(msg1)
        self.messenger.send_message(msg2)
        
        time.sleep(0.5)
        
        self.assertEqual(len(type1_messages), 1)
        self.assertEqual(len(type2_messages), 1)
        self.assertEqual(type1_messages[0], msg1)
        self.assertEqual(type2_messages[0], msg2)

    def test_unknown_message_type(self):
        """Test handling messages with unknown type"""
        self.messenger.start()
        received_messages = []
        
        def test_callback(message):
            received_messages.append(message)
            
        self.messenger.add_listener("known_type", test_callback)
        unknown_message = {"type": "unknown_type", "data": "test"}
        self.messenger.send_message(unknown_message)
        
        time.sleep(0.5)
        self.assertEqual(len(received_messages), 0)

    def test_message_with_newlines(self):
        """Test handling messages containing newlines"""
        self.messenger.start()
        received_messages = []
        
        def test_callback(message):
            received_messages.append(message)
        self.messenger.add_listener("test_type", test_callback)

        test_message = {"type": "test_type", "test": "data\nwith\nnewlines"}
        self.messenger.send_message(test_message)
        time.sleep(0.5)
        
        self.assertEqual(received_messages[0], test_message)

    def test_connection_timeout(self):
        """Test connection timeout with non-existent socket"""
        messenger = Messenger(
            socket_server="/tmp/nonexistent_server.sock",
            socket_client="/tmp/nonexistent_client.sock",
            connection_timeout=0.1
        )
        result = messenger._wait_for_socket()
        self.assertFalse(result)

    def test_context_manager(self):
        """Test context manager with real socket"""
        with Messenger(self.server_socket, self.client_socket) as messenger:
            self.assertTrue(messenger.running)
            messenger.send_message({"test": "context"})
            time.sleep(0.1)
        self.assertFalse(messenger.running)

if __name__ == '__main__':
    unittest.main()