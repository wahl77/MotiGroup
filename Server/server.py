import socket
import threading
import time
import MySQLdb as mdb
import sys
from connectionHandler import ConnectionHandler
import thread
import getopt

SIZE = 4


def main(argv):
	HOST = "127.0.0.1"
	PORT = 5432
	MAX_NUMBER_OF_CONNECTIONS = 1

	try:
		opts, args = getopt.getopt(argv, "hp:x:s:", ["help", "port=", "max-connections=", "server="])
	except getopt.GetoptError:
		print 'Error: Usage is ' + sys.argv[0] + ' -p <port> -s <server> -x <maximum_number_of_connection>'
		print "Default is: -s " + str(HOST) + " -p " + str(PORT) + " -x " + str(MAX_NUMBER_OF_CONNECTIONS)
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print 'Usage is ' + sys.argv[0] + ' -p <port> -s <server> -x <maximum_number_of_connection>'
			print "Default is: -s " + str(HOST) + " -p " + str(PORT) + " -x " + str(MAX_NUMBER_OF_CONNECTIONS)
			sys.exit()
		elif opt in ("-p", "--port"):
			PORT = int(arg)
		elif opt in ("-s", "--server"):
			HOST = arg
		elif opt in ("-x", --max-connections):
			MAX_NUMBER_OF_CONNECTIONS = int(arg)
			
	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	soc.bind((HOST,PORT))
	soc.listen(5)



	i = 0
	while i < MAX_NUMBER_OF_CONNECTIONS:
		(client_socket, address) = soc.accept() # The incoming/outgoing socket
		thr = ConnectionHandler(client_socket)
		thr.start()
		i += 1
	

if __name__ == "__main__":
	main(sys.argv[1:])


