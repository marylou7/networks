import socket

botSock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

serverName = 'localHost IPv6'
port = 6667
server_address = ("::1", port)
print(socket.gethostname())
nick = 'Ludovic'

botSock.connect(("::1", port))

"""
try:

    message = 'Hello'
    print('sending {!r}'.format(message))
    botSock.sendall(message)
finally:
    print('closing socket')
    botSock.close()
"""