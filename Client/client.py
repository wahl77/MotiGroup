import socket

SIZE = 4
HOST = "127.0.0.1"
PORT = 5432

def message_recv(socket):
	data = socket.recv(SIZE)
	socket.send("OK")
	msg =  socket.recv(int(data)) # Return the string
	print 'Received --> ', msg
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



soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect((HOST,PORT))

while 1:
	msg = message_recv(soc)
	window = message_recv(soc)
	if msg == 'EOF':
		print "Connection Ended"
		break;
	else:
		message_send(soc, raw_input())
		message_send(soc, window)
	



print 'Socket Closing'
soc.close()
