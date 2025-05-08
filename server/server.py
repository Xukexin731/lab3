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