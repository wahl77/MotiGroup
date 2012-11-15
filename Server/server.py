import socket
import threading
import time
import MySQLdb as mdb
import sys
from connectionHandler import ConnectionHandler
import thread

SIZE = 4
HOST = "127.0.0.1"
PORT = 5432
MAX_NUMBER_OF_CONNECTIONS = 5


soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind((HOST,PORT))
soc.listen(5)



i = 0
while i < MAX_NUMBER_OF_CONNECTIONS:
	(client_socket, address) = soc.accept() # The incoming/outgoing socket
	thr = ConnectionHandler(client_socket)
	thr.start()
	i += 1
