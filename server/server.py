import socket
import threading
import json
import logging
import time
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Server Config
HOST = '0.0.0.0'
PORT = 5000
BUFFER_SIZE = 4096

class RaceState:
    WAITING = "WAITING"
    COUNTDOWN = "COUNTDOWN"
    RACING = "RACING"
    FINISHED = "FINISHED"

class CourseRoom:
    def __init__(self, course_id, server):
        self.course_id = course_id
        self.server = server
        self.state = RaceState.WAITING
        self.players = {} # {client_id: {"ready": False, "lap": 0, ...}}
        self.countdown_start_time = 0
        self.start_time = 0
        self.countdown_duration = 4
        self.lock = threading.Lock()
        
        # Start game loop thread for this room
        threading.Thread(target=self.game_loop, daemon=True).start()

    def add_player(self, client_id, otete_index=0):
        with self.lock:
            self.players[client_id] = {
                "ready": False,
                "lap": 0,
                "finished": False,
                "time": 0,
                "otete_index": otete_index
            }
            logging.info(f"Room {self.course_id}: Added player {client_id}. Total players: {len(self.players)}")
            if self.state != RaceState.WAITING:
                 logging.info(f"Room {self.course_id}: Player {client_id} joined while state is {self.state}")

    def remove_player(self, client_id):
        with self.lock:
            if client_id in self.players:
                del self.players[client_id]
                logging.info(f"Room {self.course_id}: Removed player {client_id}. Remaining: {len(self.players)}")
                if len(self.players) == 0:
                    self.reset_race()

    def set_ready(self, client_id, status=True):
        with self.lock:
            if client_id in self.players:
                self.players[client_id]["ready"] = status
                logging.info(f"Room {self.course_id}: Player {client_id} ready={status}. Players: {[(k, v['ready']) for k, v in self.players.items()]}")
                self.check_start_condition()
            else:
                logging.warning(f"Room {self.course_id}: set_ready for unknown player {client_id}")

    def update_lap(self, client_id, lap, finished=False, finish_time=0):
        with self.lock:
            if client_id in self.players:
                self.players[client_id]["lap"] = lap
                if finished:
                    self.players[client_id]["finished"] = True
                    self.players[client_id]["time"] = finish_time
                    self.check_finish_condition()

    def check_start_condition(self):
        if self.state == RaceState.WAITING:
            ready_count = sum(1 for p in self.players.values() if p["ready"])
            total = len(self.players)
            logging.info(f"Room {self.course_id}: check_start: {ready_count}/{total} ready")
            # VS Race (rooms 0-9): need >= 2 all ready
            if self.course_id < 10:
                if total >= 2 and ready_count == total:
                    self.start_countdown()
            else:
                # Time Attack rooms (10+)
                if total > 0 and ready_count == total:
                    self.start_countdown()

    def start_countdown(self):
        logging.info(f"Room {self.course_id}: Starting countdown!")
        self.state = RaceState.COUNTDOWN
        self.countdown_start_time = time.time()

    def start_race(self):
        self.state = RaceState.RACING
        self.start_time = time.time()

    def check_finish_condition(self):
        finished_count = sum(1 for p in self.players.values() if p["finished"])
        if len(self.players) > 0 and finished_count == len(self.players):
            self.state = RaceState.FINISHED
            threading.Timer(10.0, self.reset_race).start()

    def reset_race(self):
        self.state = RaceState.WAITING
        with self.lock:
            for p in self.players.values():
                p["ready"] = False
                p["lap"] = 0
                p["finished"] = False
                p["time"] = 0

    def get_leaderboard(self):
        with self.lock:
            p_list = []
            for pid, data in self.players.items():
                p_list.append({"id": pid, **data})
            
            def sort_key(p):
                if p["finished"]:
                    return (0, p["time"])
                else:
                    return (1, -p["lap"])
            
            p_list.sort(key=sort_key)
            return p_list

    def broadcast(self, msg, exclude_id=None):
        """Broadcast to only players in this room."""
        encoded = (json.dumps(msg) + "\n").encode('utf-8')
        with self.lock:
            target_ids = [cid for cid in self.players.keys() if cid != exclude_id]
        
        if target_ids:
            self.server.broadcast_to_list(target_ids, encoded)

    def game_loop(self):
        while True:
            time.sleep(0.1)
            
            if self.state == RaceState.COUNTDOWN:
                elapsed = time.time() - self.countdown_start_time
                remaining = self.countdown_duration - elapsed
                if remaining <= 0:
                    self.start_race()
            
            msg = {
                "type": "gamestate",
                "course": self.course_id,
                "state": self.state,
                "countdown": max(0, int(self.countdown_duration - (time.time() - self.countdown_start_time))) if self.state == RaceState.COUNTDOWN else 0,
                "leaderboard": self.get_leaderboard()
            }
            self.broadcast(msg)


class GameServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen()
        
        # client_id (UUID) -> client_socket
        self.id_to_socket = {}
        # client_socket -> client_id
        self.socket_to_id = {}
        
        self.lock = threading.Lock()
        
        # Rooms: 0 to 9 (VS Race), 10 to 19 (Time Attack)
        self.rooms = {i: CourseRoom(i, self) for i in range(20)}
        
        # Track which room a player is in: client_id -> course_id
        self.player_rooms = {} 
        

        
        logging.info(f"Server started on {HOST}:{PORT}")

    def generate_client_id(self):
        """Generate a unique client ID using UUID for persistence."""
        return f"User_{uuid.uuid4().hex[:6]}"



    def send_to_socket(self, sock, data):
        try:
            sock.sendall((json.dumps(data) + "\n").encode('utf-8'))
        except:
            pass


    def broadcast_to_list(self, id_list, message_bytes):
        with self.lock:
            for cid in id_list:
                if cid in self.id_to_socket:
                    try:
                        self.id_to_socket[cid].sendall(message_bytes)
                    except:
                        pass

    def remove_client(self, client_socket):
        with self.lock:
            if client_socket in self.socket_to_id:
                client_id = self.socket_to_id[client_socket]
                del self.socket_to_id[client_socket]
                if client_id in self.id_to_socket:
                    del self.id_to_socket[client_id]
                
                # Remove from room
                if client_id in self.player_rooms:
                    room_id = self.player_rooms[client_id]
                    self.rooms[room_id].remove_player(client_id)
                    del self.player_rooms[client_id]
                    
                    # Broadcast disconnect to room
                    disconnect_msg = {"type": "disconnect", "id": client_id}
                    self.rooms[room_id].broadcast(disconnect_msg)
                    
                try:
                    client_socket.close()
                except:
                    pass
                logging.info(f"Client {client_id} disconnected.")

    def handle_client(self, client_socket, addr):
        addr_str = f"{addr[0]}:{addr[1]}"
        
        # Generate unique ID for this connection
        client_id = self.generate_client_id()
        logging.info(f"New connection from {addr_str} -> assigned ID: {client_id}")
        
        with self.lock:
            self.socket_to_id[client_socket] = client_id
            self.id_to_socket[client_id] = client_socket
            
        # Welcome Protocol: Tell the client its unique ID
        welcome_msg = {"type": "welcome", "id": client_id}
        try:
            client_socket.sendall((json.dumps(welcome_msg) + "\n").encode('utf-8'))
            logging.info(f"Sent welcome to {client_id} ({addr_str})")
        except:
            pass
            
        try:
            buffer = ""
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                
                buffer += data.decode('utf-8')
                
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip():
                        continue
                        
                    try:
                        msg_data = json.loads(line)
                        msg_type = msg_data.get("type")
                        
                        # Debug: Log all typed messages
                        if msg_type:
                            logging.info(f"[{client_id}] type={msg_type}")
                        
                        # --- Lobby / Room Logic ---
                        
                        if msg_type == "get_rooms":
                            counts = {}
                            for cid, room in self.rooms.items():
                                counts[cid] = len(room.players)
                            
                            resp = {"type": "room_counts", "counts": counts}
                            client_socket.sendall((json.dumps(resp) + "\n").encode('utf-8'))
                            
                        elif msg_type == "join":
                            course_id = msg_data.get("course", 0)
                            otete_index = msg_data.get("otete_index", 0)
                            
                            # Leave old room if any
                            if client_id in self.player_rooms:
                                old_room = self.player_rooms[client_id]
                                self.rooms[old_room].remove_player(client_id)
                                del self.player_rooms[client_id]
                            
                            # Join new room
                            self.player_rooms[client_id] = course_id
                            self.rooms[course_id].add_player(client_id, otete_index)
                            logging.info(f"[{client_id}] joined room {course_id}")

                        elif msg_type == "leave":
                            if client_id in self.player_rooms:
                                old_room = self.player_rooms[client_id]
                                self.rooms[old_room].remove_player(client_id)
                                del self.player_rooms[client_id]
                                logging.info(f"[{client_id}] left room {old_room}")
                            
                        # --- In-Game Logic (must be in a room) ---
                        
                        elif client_id in self.player_rooms:
                            room_id = self.player_rooms[client_id]
                            room = self.rooms[room_id]
                            
                            if msg_type == "ready":
                                room.set_ready(client_id, True)
                            elif msg_type == "lap_update":
                                room.update_lap(client_id, msg_data.get("lap", 0))
                            elif msg_type == "finished":
                                room.update_lap(client_id, 3, True, msg_data.get("time", 0))

                            elif "x" in msg_data:
                                # Position update -> broadcast to room
                                broadcast_data = {
                                    "id": client_id,
                                    "course": room_id,
                                    "data": msg_data
                                }
                                room.broadcast(broadcast_data, exclude_id=client_id)
                                
                    except json.JSONDecodeError:
                        logging.warning(f"Invalid JSON from {client_id}: {line}")
                        
        except ConnectionResetError:
            logging.info(f"Connection reset by {client_id}")
        except Exception as e:
            logging.error(f"Error handling client {client_id}: {e}")
        finally:
            self.remove_client(client_socket)

    def start(self):
        logging.info("Waiting for connections...")
        while True:
            client_socket, addr = self.server_socket.accept()
            thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
            thread.daemon = True
            thread.start()

if __name__ == "__main__":
    game_server = GameServer()
    try:
        game_server.start()
    except KeyboardInterrupt:
        logging.info("Server stopping...")
