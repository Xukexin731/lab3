import socket
import sys
def process_requests(server_host, server_port, request_file):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_host, server_port))
        with open(request_file, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(' ')
                command = parts[0]
                key = parts[1]
                value = parts[2] if len(parts) == 3 else ''
                message_size = len(line) + 3
                request = f"{message_size:03d} {command[0]} {key} {value}" if command == 'PUT' else f"{message_size:03d} {command[0]} {key}"
                client_socket.send(request.encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                print(f"{line}: {response[3:]}")
