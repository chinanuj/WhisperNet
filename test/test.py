import socket
import threading
import time

def start_server(port, stop_event):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"[SERVER] Listening on port {port}")
    
    try:
        while not stop_event.is_set():
            try:
                client_socket, addr = server_socket.accept()
                print(f"[SERVER] Connection from {addr}")
                threading.Thread(
                    target=handle_client, 
                    args=(client_socket,),
                    daemon=True
                ).start()
            except OSError:
                break  # Graceful Shut Down
    finally:
        server_socket.close()

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"[SERVER] Received: {data.decode()}")
            client_socket.send(f"ACK: {data.decode()}".encode())
    except ConnectionResetError:
        print("[SERVER] Client disconnected abruptly")
    finally:
        client_socket.close()

def start_client(server_port, num_messages=5):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', server_port))
            print(f"[CLIENT] Connected to server on port {server_port}")
            
            for i in range(num_messages):
                msg = f"Test {i+1}"
                s.send(msg.encode())
                response = s.recv(1024).decode()
                print(f"[CLIENT] Received: {response}")
                time.sleep(1)
    except ConnectionResetError:
        print("[CLIENT] Server closed connection")

if __name__ == "__main__":
    stop_event = threading.Event()
    ports = [9999, 10000]
    servers = []

    for port in ports:
        server_thread = threading.Thread(
            target=start_server, 
            args=(port, stop_event),
            daemon=True
        )
        server_thread.start()
        servers.append(server_thread)
        time.sleep(0.5)

    clients = []
    for port in ports:
        client_thread = threading.Thread(
            target=start_client, 
            args=(port,)
        )
        client_thread.start()
        clients.append(client_thread)

    for client in clients:
        client.join()

    # Graceful shutdown sequence
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        stop_event.set()
        time.sleep(1)  # Allow servers to close
