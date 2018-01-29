import socket
 
def Main():
    host = '127.0.0.1'
    port = 8888
     
    mySocket = socket.socket()
    mySocket.connect((host,port))
     
    message = input(" -> ")
     
    while message != 'q':
        print(message)
        mySocket.send(message.encode())
        data = mySocket.recv(1024).decode()
         
        print ('Received from server: ' + data)
         
        message = input(" -> ")
             
    mySocket.close()
def main_2():
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # now connect to the web server on port 80 - the normal http port
    s.connect(("anshp.ml", 80))
    message = input(" -> ")
     
    while message != 'q':
        print(message)
        s.send(message.encode())
        data = s.recv(1024).decode()
         
        print ('Received from server: ' + data)
         
        message = input(" -> ")




if __name__ == '__main__':
    Main()
    # main_2()