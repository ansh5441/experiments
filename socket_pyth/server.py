import socket
 
def Main():
    host = "127.0.0.1"
    port = 5000
     
    mySocket = socket.socket()
    print(socket.gethostname())
    mySocket.bind((socket.gethostname(),port))
     
    mySocket.listen(1)
    conn, addr = mySocket.accept()
    print ("Connection from: " + str(addr))
    while True:
        data = conn.recv(1024).decode()
        if not data:
                break
        print ("from connected  user: " + str(data))
         
        data = str(data).upper()
        print ("sending: " + str(data))
        conn.send(data.encode())
             
    conn.close()

def main_2():
    # create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    serversocket.bind((socket.gethostname(), 80))
    # become a server socket
    serversocket.listen(5)
    conn, addr = serversocket.accept()
    while True:
        data = conn.recv(1024).decode()
        if not data:
                break
        print ("from connected  user: " + str(data))
         
        data = str(data).upper()
        print ("sending: " + str(data))
        conn.send(data.encode())


if __name__ == '__main__':
    main_2()




