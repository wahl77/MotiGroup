import socket
import threading
import time
import MySQLdb as mdb
import sys
import connectionHandler
import thread

SIZE = 4
HOST = "127.0.0.1"
PORT = 5432


soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind((HOST,PORT))
soc.listen(5)

while 1:
	(client_socket, address) = soc.accept() # The incoming/outgoing socket
	Thread(connectionHandler.ConnectionHandler.run, (client_socket, 1)).start()
