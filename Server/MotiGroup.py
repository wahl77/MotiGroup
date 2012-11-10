import socket # for Sockets
import sys

try: 
	# Create an AF_INET (this is IPv4) STREAM (this is connection oriented TCP protocol )socket (TCP)
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
	#serversocket.bind((socket.gethostname(), 880))
	serversocket.bind(('localhost', 880))
	serversocket.listen(5)

except socket.error , msg:
		print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
		sys.exit()

print "Socket Created"


while (1):
	# accept connections from outside
	(clinetsocket, address) = serversocket.accept()
	data = raw_input ( "SEND( TYPE q or Q to Quit):" )
	if (data == 'Q' or data == 'q'):
		client_socket.send (data)
		client_socket.close()
		break;
	else:
		client_socket.send(data)
 
	data = client_socket.recv(512)
	if ( data == 'q' or data == 'Q'):
		client_socket.close()
		break;
	else:
		print "RECIEVED:" , data
	#ct = client_thread(clientsocket)
	#ct.run()
