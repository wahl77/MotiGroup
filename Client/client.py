import socket
import sys
import getopt

SIZE = 4
HOST = "127.0.0.1"
PORT = 5432

def message_recv(socket):
	data = socket.recv(SIZE)
	socket.send("OK")
	msg =  socket.recv(int(data)) # Return the string
	return msg

def message_send(socket, msg):   # For sending a message on a specific connection
	if len(msg) <= 999 and len(msg) > 0:
		socket.send(str(len(msg)))
		if socket.recv(2) == 'OK': # Server is ready to receive
			socket.send(msg)
	else:
		socket.send(str(999))
		if socket.recv(2) == 'OK':
			socket.send(msg[:999])
			message_send(socket, msg[1000:])				#call recursively with the following bytes



def main(argv):
	HOST = "127.0.0.1"
	PORT = 5432

	try:
		opts, args = getopt.getopt(argv, "hp:s:", ["help", "port=", "server="])
	except getopt.GetoptError:
		print 'Error: Usage is ' + sys.argv[0] + ' -p <port> -s <server> '
		print "Default is: -s " + str(HOST) + " -p " + str(PORT)
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print 'Usage is ' + sys.argv[0] + ' -p <port> -s <server>'
			print "Default is: -s " + str(HOST) + " -p " + str(PORT) 
			sys.exit()
		elif opt in ("-p", "--port"):
			PORT = int(arg)
		elif opt in ("-s", "--server"):
			HOST = arg

	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	soc.connect((HOST,PORT))
	
	while 1:
		msg = message_recv(soc)
		print 'Received -->\n' + msg 
		if msg == 'EOF':
			print "Connection Ended"
			break;
		else:
			message_send(soc, raw_input())
	
	print 'Socket Closing'
	soc.close()

			
if __name__ == "__main__":
	main(sys.argv[1:])


