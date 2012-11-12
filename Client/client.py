import socket
import threading

SIZE = 4
HOST = "127.0.0.1"
PORT = 5432

class client_receiving_thread(threading.Thread):
	def __init__(self, socket):
		threading.Thread.__init__(self)
		self.socket = socket
		self.stopIt = False

	def message_recv(self):
		data = self.socket.recv(SIZE)
		self.socket.send("OK")
		return self.socket.recv(int(data)) # Return the string
	
	def run(self):
		while not self.stopIt:
			msg = self.message_recv()
			print 'Received -->', msg

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



# Always create two sockets, one for sending the other one for receiving data
soc1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc1.connect((HOST,PORT))
soc1.send('Will Send') # indicating this socket is for sending data

soc2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc2.connect((HOST,PORT))
soc2.send('Will Recv') # indicating this socket is for receiving data

thr = client_receiving_thread(soc2)
thr.start()
try:
	while True:
		message_send(soc1, raw_input())
except:
	print 'closing'

thr.stopIt = True
thr.conn.close() # Close the thread

soc1.close() # Close sending socket
soc2.close() # Close receiving socket
