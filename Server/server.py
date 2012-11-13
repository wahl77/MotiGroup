import socket
import threading
import time
import MySQLdb as mdb
import sys

SIZE = 4
HOST = "127.0.0.1"
PORT = 5432

window = {'login': '0', 'password': '1', 'end': '2'}

db = mdb.connect(host='localhost', user='root', passwd='', db='MotiGroup')

def message_recv(socket):
	data = socket.recv(SIZE)
	socket.send('OK') # Send a ready to receive signal
	msg = socket.recv(int(data))
	print 'Received --> ', msg
	return msg

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


def handle_message(client_msg, client_window):
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

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind((HOST,PORT))
soc.listen(5)

(client_socket, address) = soc.accept() # The incoming/outgoing socket


msg1 = "Welcome to MotiGroup\n\tPlease enter your username"
msg2 = window['login']
message_send(client_socket, msg1)
message_send(client_socket, msg2)

while 1:
	client_msg = message_recv(client_socket)
	client_window = message_recv(client_socket)
	if client_msg == 'q':
		message_send(client_socket, 'EOF')
		message_send(client_socket, 'EOF')
		break
	else:
		(msg1, msg2) = handle_message(client_msg, client_window)
		message_send(client_socket, msg1)
		message_send(client_socket, msg2)
		print "Your replied"

print "Socket closing" 
soc.close()
