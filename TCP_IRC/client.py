import socket
import threading
import datetime

nickname = input("[Server] Choose a nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 12400))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == "NICK":
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            print("[Server] Error occurred")
            client.close()
            break

def write():
    while True:
        t = datetime.datetime.now()
        time = t.strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{time}] ({nickname}): {input('')}"
        client.send(message.encode('ascii'))
    
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()