import socket
import threading

SIZE = 4
HOST = "127.0.0.1"
PORT = 5432


# Identify which socket is for sending or which socket is for receiving. This is based on the first message (Will Send or Will Recv) that is broadcast at start from the client when connecting. 
def setConn(socket_1, socket_2):
	dict = {}
	state = socket_1.recv(9) 
	socket_2.recv(9)

	if state == 'Will Recv':
		dict['send'] = socket_1
		dict['recv'] = socket_2 
	else: 
		dict['send'] = socket_2
		dict['recv'] = socket_1

	return dict
		
class server_receiving_thread(threading.Thread):
	def __init__(self, socket):
		threading.Thread.__init__(self)
		self.socket = socket
		self.stopIt = False

	def message_recv(self):
		data = self.socket.recv(SIZE)
		self.socket.send('OK') # Send a ready to receive signal
		msg = self.socket.recv(int(data))
		return msg

	def run(self):
		while not self.stopIt:
			msg = self.message_recv()
			print 'Received --> ', msg
			if msg == 'STOP':
				self.stopIt = True


def message_send(socket, msg):
	if len(msg) <= 999 and len(msg) > 0:
		socket.send(str(len(msg)))
		if socket.recv(2) == 'OK':
			socket.send(msg)
	else:
		conn.send(str(999))
		if socket.recv(2) == 'OK':
			socket.send(msg[:999])
			message_send(socket, msg[1000:])
	
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind((HOST,PORT))
soc.listen(5)

(client_socket1, address1) = soc.accept() # The incoming/outgoing socket
(client_socket2, address2) = soc.accept()

dict = setConn(client_socket1, client_socket2) # Define which socket is for which

thr = server_receiving_thread(dict['recv'])
thr.start()
try:
	while True:
		text = raw_input()
		message_send(dict['send'], text)
except:
	print 'closing'

print "exit while loop" 
thr.stopIt=True
thr.socket.close()
soc.close()
print "done" 

