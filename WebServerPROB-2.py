# Import socket module
from socket import *

# Create a TCP server socket
# (AF_INET is used for IPv4 protocols)
# (SOCK_STREAM is used for TCP)
serverPort = 6789
proxyPort = 8888

serverSocket = socket(AF_INET, SOCK_STREAM)

# Bind the socket to a specific address and port
serverSocket.bind(('', 6789))

# Listen for incoming connections
serverSocket.listen(1)

# Server should be up and running and listening to the incoming connections
while True:
    print('Ready to serve...')

    # Set up a new connection from the client
    connectionSocket, addr = serverSocket.accept()

    try:
        # Receive the HTTP request from the client
        message = connectionSocket.recv(5120).decode()

        # Extract the filename from the request
        filename = message.split()[1]

        # Open the file and read its contents
        with open(filename[1:], 'rb') as f:
            outputdata = f.read()

        # Set the content type based on the file extension
        if filename.endswith('.html'):
            content_type = 'text/html'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif filename.endswith('.png'):
            content_type = 'image/png'
        else:
            content_type = 'application/octet-stream'

        # Set the HTTP response status and headers
        response_headers = 'HTTP/1.1 200 OK\r\n'
        response_headers += 'Content-Type: {}\r\n'.format(content_type)
        response_headers += 'Content-Length: {}\r\n'.format(len(outputdata))
        response_headers += 'Connection: close\r\n\r\n'

        # Send the HTTP response headers and file contents to the client
        try:
            connectionSocket.send(response_headers.encode())
            connectionSocket.sendall(outputdata)
        except BrokenPipeError:
            pass  # Client closed the connection prematurely

    except IOError:
        # Send HTTP response message for file not found
        response_headers = 'HTTP/1.1 404 Not Found\r\n'
        response_headers += 'Content-Type: text/html\r\n'
        response_headers += 'Connection: close\r\n\r\n'
        response_body = '<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n'
        try:
            connectionSocket.send(response_headers.encode())
            connectionSocket.send(response_body.encode())
        except BrokenPipeError:
            pass  # Client closed the connection prematurely

    # Close the client connection socket
    connectionSocket.close()

# Close the server socket
serverSocket.close()
