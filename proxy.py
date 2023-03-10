from socket import *

proxyClientSocket = socket(AF_INET,SOCK_STREAM)
# set up dictionary cache in proxy using filename as key
cache = {}

# set port of proxy server to 8888
proxyPort = 8888
proxyClientSocket.bind(("",proxyPort)) # bind port to socket
proxyClientSocket.listen(1) # listen for any incoming connections

while True:
    print("Proxy running...")
    connectionSocket, addr = proxyClientSocket.accept() # accept connection made by client
    try:
        clientMessage = connectionSocket.recv(4096 * 4096) # recieve data from client
        orgMessage = str(clientMessage).split() # parse client message to get filename and origin server port
        serverAndFilename = orgMessage[1]
        try:
            _,serverPort,filename = serverAndFilename.split("/") 
            print(serverAndFilename.split("/"))
            print("Values unpacked correctly")
        except ValueError:
            print(serverAndFilename.split("/"))
            print("Npot enough values to unpack")
        # check if request is cached already
        # set up dictionary cache using filename as key
        # if not cached, send http GET request to server
        if filename not in cache:
            proxyServerSocket = socket(AF_INET,SOCK_STREAM) # create socket between proxy and server
            proxyServerSocket.connect((serverPort.split(":")[0], int(serverPort.split(":")[1])))
            # connect to origin server
            orgMessage[1] = "/" + filename
            proxyServerSocket.send(" ".join(orgMessage).encode()) # send message to server for file
            serverMessage = proxyServerSocket.recv(4096) # recieve data 
            if serverMessage[:12].decode()== "HTTP/1.1 404": # check if file is found or not
                raise IOError # raise exception if so
            oldLenOfMessage = 0
            while len(serverMessage) != oldLenOfMessage: # recieve data until server does not send anymore
                oldLenOfMessage = len(serverMessage)
                serverMessage += proxyServerSocket.recv(4096)

            # add file data to cache
            cache[filename] = serverMessage
            print("retrieve file from server")
            proxyServerSocket.close() # close socket between proxy and server

        # get file data from cache if already stored
        else:
            serverMessage = cache[filename]
            print("retrieve file from cache")
        
        # Fill in end
        # Send the content of the requested file to the connection socket

        # send file data backet to client
        startIndex = 0
        while startIndex <= len(serverMessage):
            connectionSocket.send(serverMessage[startIndex:min(startIndex+4096,len(serverMessage))])
            startIndex+=4096
        print("sent")

        # Close the client connection socket
        connectionSocket.close()
    except IOError: # if IOerror is raised, the file was not found
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n".encode())
        connectionSocket.close() # Close the client connection socket
proxyClientSocket.close()