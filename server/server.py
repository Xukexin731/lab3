import socket
import threading
import time
tuple_space = {}
client_count = 0
operation_count = 0
read_count = 0
get_count = 0
put_count = 0
error_count = 0
def handle_client(client_socket, client_address):
    global client_count, operation_count, read_count, get_count, put_count, error_count
    client_count += 1
    while True:
        try:
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                break
            message_size = int(request[:3])
            command = request[3]
            key = request[4:message_size - 1] if command != 'P' else request[4:message_size - len(request.split(' ')[-1]) - 2]
            value = request.split(' ')[-1] if command == 'P' else ''

            response = ''
            if command == 'R':
                operation_count += 1
                read_count += 1
                if key in tuple_space:
                    response = f"{len(f'OK ({key}, {tuple_space[key]}) read'):03d} OK ({key}, {tuple_space[key]}) read"
                else:
                    response = f"{len('ERR k does not exist'):03d} ERR k does not exist"
                    error_count += 1

            elif command == 'G':
                operation_count += 1
                get_count += 1
                if key in tuple_space:
                    value = tuple_space.pop(key)
                    response = f"{len(f'OK ({key}, {value}) removed'):03d} OK ({key}, {value}) removed"
                else:
                    response = f"{len('ERR k does not exist'):03d} ERR k does not exist"
                    error_count += 1
            
            elif command == 'P':
                operation_count += 1
                put_count += 1
                if key in tuple_space:
                    response = f"{len('ERR k already exists'):03d} ERR k already exists"
                    error_count += 1
                else:
                    tuple_space[key] = value
                    response = f"{len(f'OK ({key}, {value}) added'):03d} OK ({key}, {value}) added"
                client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
            break
    client_socket.close()
def print_statistics():
    global tuple_space, client_count, operation_count, read_count, get_count, put_count, error_count
    while True:
        time.sleep(10)
        tuple_count = len(tuple_space)
        if tuple_count > 0:
            total_tuple_size = sum(len(key) + len(value) for key, value in tuple_space.items())
            total_key_size = sum(len(key) for key in tuple_space.keys())
            total_value_size = sum(len(value) for value in tuple_space.values())
            avg_tuple_size = total_tuple_size / tuple_count
            avg_key_size = total_key_size / tuple_count
            avg_value_size = total_value_size / tuple_count
        else:
            avg_tuple_size = 0
            avg_key_size = 0
            avg_value_size = 0
        print(f"Tuple Space Statistics:")
        print(f"Number of tuples: {tuple_count}")
        print(f"Average tuple size: {avg_tuple_size}")
        print(f"Average key size: {avg_key_size}")
        print(f"Average value size: {avg_value_size}")
        print(f"Total number of clients: {client_count}")
        print(f"Total number of operations: {operation_count}")
        print(f"Total READs: {read_count}")
        print(f"Total GETs: {get_count}")
        print(f"Total PUTs: {put_count}")
        print(f"Total errors: {error_count}")
def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"Server listening on port {port}...")
    stats_thread = threading.Thread(target=print_statistics)
    stats_thread.daemon = True
    stats_thread.start()
    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)
    port = int(sys.argv[1])
    start_server(port)