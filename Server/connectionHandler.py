import socket
import threading
import MySQLdb as mdb
import sys

SIZE = 4
HOST = "127.0.0.1"
PORT = 5432

window = {'login': '0', 'password': '1', 'end': '2'}

db = mdb.connect(host='localhost', user='root', passwd='', db='MotiGroup')

class ConnectionHandler(threading.Thread):
	def __init__(self, client_socket):
		self.socket = client_socket
		threading.Thread.__init__(self)

	def message_recv(self, socket):
		data = self.socket.recv(SIZE)
		socket.send('OK') # Send a ready to receive signal
		msg = self.socket.recv(int(data))
		print 'Received --> ', msg
		return msg
	
	def message_send(self, socket, msg):
		if len(msg) <= 999 and len(msg) > 0:
			self.socket.send(str(len(msg)))
			if self.socket.recv(2) == 'OK':
				self.socket.send(msg)
		else:
			conn.send(str(999))
			if self.socket.recv(2) == 'OK':
				self.socket.send(msg[:999])
				self.message_send(self.socket, msg[1000:])
	
	
	def handle_message(self, client_msg, client_window):
		with db: 
			cur = db.cursor(mdb.cursors.DictCursor)
			if client_window == window['login']:
				cur.execute("SELECT * FROM Users WHERE username  = %s", client_msg)
				row = cur.fetchall()
				if len(row) == 0:
					return ("Sorry, username not found\nPlease enter your username", window['login'])
				else:
					msg = "Please enter your password " + row[0]['firstName']
					return (msg, window['password'])
			else:
						print "dude"
			return ("test", "abc")

	def run(self):
		msg0 = "Welcome to MotiGroup\n\tPlease enter your username"
		msg2 = window['login']
		self.message_send(self.socket, msg0)
		self.message_send(self.socket, msg2)
		while 1:
			client_msg = self.message_recv(self.socket)
			client_window = self.message_recv(self.socket)
			if client_msg == 'q':
				self.message_send(socket, 'EOF')
				self.message_send(socket, 'EOF')
				break
			else:
				(msg1, msg2) = self.handle_message(client_msg, client_window)
				self.message_send(socket, msg1)
				self.message_send(socket, msg2)
				print "Your replied " + msg1 + " to: " + self.socket.getsockname()[0] + str(self.socket.getsockname()[1]) + self.socket.getpeername()[0]  + str(self.socket.getpeername()[1])
		print "Socket closing" 
		self.socket.close()
