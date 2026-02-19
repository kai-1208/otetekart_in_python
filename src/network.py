import socket
import threading
import json
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NetworkManager:
    def __init__(self):
        self.host = 'localhost'
        self.port = 5000
        self.socket = None
        self.connected = False
        
        # SEPARATE LOCKS: data_lock for player data, send_lock for socket writes
        self.data_lock = threading.Lock()
        self.send_lock = threading.Lock()
        
        self.other_players = {}
        self.race_state = "WAITING"
        self.countdown = 0
        self.leaderboard = []
        self.room_counts = {}
        self.client_id = None
        
        # Room tracking for auto-rejoin
        self.last_course = None
        self.last_otete = None

        # Start persistent thread
        threading.Thread(target=self.network_loop, daemon=True).start()

    def network_loop(self):
        """Persistent loop that handles connection and receiving."""
        while True:
            if not self.connected:
                self.connect_to_server()
                if not self.connected:
                    time.sleep(2)
                    continue

            try:
                self.receive_data_loop()
            except Exception as e:
                logging.error(f"Network loop error: {e}")
                self.close_socket_internal()
                time.sleep(1)

    def connect_to_server(self):
        try:
            if self.socket:
                try: self.socket.close()
                except: pass
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.socket.settimeout(60.0)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logging.info(f"Connected to server at {self.host}:{self.port}")
            
            # Auto-rejoin if we were previously in a room
            if self.last_course is not None:
                time.sleep(0.3)
                self.join_room(self.last_course, self.last_otete)
                    
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            self.connected = False

    def receive_data_loop(self):
        buffer = ""
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    logging.info("Server closed connection")
                    self.connected = False
                    break
                
                buffer += data.decode('utf-8')
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip(): continue
                    
                    try:
                        msg_data = json.loads(line)
                        msg_type = msg_data.get("type")
                        
                        # Only lock briefly for data writes
                        if msg_type == "welcome":
                            with self.data_lock:
                                self.client_id = msg_data.get("id")
                            logging.info(f"My Client ID: {self.client_id}")
                                
                        elif msg_type == "gamestate":
                            with self.data_lock:
                                self.race_state = msg_data.get("state", "WAITING")
                                self.countdown = msg_data.get("countdown", 0)
                                self.leaderboard = msg_data.get("leaderboard", [])
                                
                        elif msg_type == "room_counts":
                            with self.data_lock:
                                self.room_counts = msg_data.get("counts", {})
                                
                        elif msg_type == "disconnect":
                            pid = msg_data.get("id")
                            with self.data_lock:
                                if pid in self.other_players:
                                    del self.other_players[pid]
                                    
                        elif "id" in msg_data and "data" in msg_data:
                            pid = msg_data["id"]
                            # Filter out self
                            if pid != self.client_id:
                                with self.data_lock:
                                    self.other_players[pid] = msg_data["data"]
                                    
                    except json.JSONDecodeError:
                        logging.warning(f"Bad JSON: {line}")
            except socket.timeout:
                continue
            except Exception as e:
                logging.error(f"Receive error: {e}")
                self.connected = False
                break

    def send(self, data):
        """Send data using a SEPARATE lock from receive, preventing contention."""
        if not self.connected: 
            return False
        try:
            encoded = (json.dumps(data) + "\n").encode('utf-8')
            with self.send_lock:
                if self.socket:
                    self.socket.sendall(encoded)
                    return True
        except Exception as e:
            logging.error(f"Send error: {e}")
            self.connected = False
        return False

    def join_room(self, course_id, otete_index):
        self.last_course = course_id
        self.last_otete = otete_index
        result = self.send({"type": "join", "course": course_id, "otete_index": otete_index})
        logging.info(f"join_room(course={course_id}) -> sent={result}")

    def leave_room(self):
        self.last_course = None
        self.send({"type": "leave"})
        self.reset_state()

    def get_gamestate(self):
        with self.data_lock:
            return self.race_state, self.countdown, self.leaderboard

    def get_room_counts(self):
        self.send({"type": "get_rooms"})

    def get_others(self):
        with self.data_lock:
            return self.other_players.copy()

    def reset_state(self):
        with self.data_lock:
            self.other_players = {}
            self.race_state = "WAITING"
            self.countdown = 0
            self.countdown = 0
            self.leaderboard = []

    def close(self):
        self.connected = False
        self.close_socket_internal()

    def close_socket_internal(self):
        if self.socket:
            try: self.socket.close()
            except: pass
            self.socket = None
