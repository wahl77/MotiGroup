import socket
import threading
import MySQLdb as mdb
import sys

SIZE = 4

window = {'login': '0', 'password': '1', 'end': '2', 'welcome' : '3', 'companies': '4'}

db = mdb.connect(host='localhost', user='root', passwd='', db='MotiGroup')

class ConnectionHandler(threading.Thread):
	def __init__(self, client_socket):
		self.socket = client_socket
		threading.Thread.__init__(self)
		self.username = ""
		self.current_window = window['login']
		with db:
			self.cursor = db.cursor(mdb.cursors.DictCursor)

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
	
	def run(self):
		msg = "Welcome to MotiGroup\nPlease enter your username: "
		self.message_send(self.socket, msg)
		while 1:
			client_msg = self.message_recv(self.socket)
			if client_msg == 'q':
				self.message_send(socket, 'EOF')
				break
			else:
				msg = self.handle_message(client_msg)
				self.message_send(socket, msg)
				print "\nYour replied to: " + self.socket.getsockname()[0] + str(self.socket.getsockname()[1]) + self.socket.getpeername()[0]  + str(self.socket.getpeername()[1]) + "\n " + msg
		print "Socket closing" 
		self.socket.close()
	
	# Return a string with the list of options for the welcome page
	def welcome_options(self):
		options = {0: 'What would  you like to do?', 1: 'View my profile', 2:'View somebody\'s profile', 3:'Reward someone)',}
		options_admin = {0: 'Add a user', 1: 'Remove a user',}
		is_admin = True
		msg = options[0]
		for i in range(1, len(options)):
			msg += "\n\t" + str(i) + ") " + options[i]
		if is_admin:
			for i in range(0, len(options_admin)):
				msg += "\n\t" + str(i+len(options)) + ") " + options_admin[i]
		return msg
	
	# Profile Page, returns a list of companies you belong to
	def my_profiles(self): 
		msg = "You belong to the following companies: \n"
		self.cursor.execute("SELECT Users.username, Companies.company_name FROM Users, UserCompany, Companies WHERE Users.username = %s  AND Users.username = UserCompany.username AND Companies.company_id = UserCompany.company_id", self.username) 
		rows = self.cursor.fetchall()
		for i in range(0, len(rows)):
			msg += "\t" + rows[i]['company_name'] + "\n"
		return msg

	def handle_message(self, client_msg):

		# Login window
		if self.current_window == window['login']:
			self.cursor.execute("SELECT * FROM Users WHERE username = %s", client_msg)
			row = self.cursor.fetchall()
			if len(row) == 0:
				return "Sorry, username not found\nPlease enter your username"
			else:
				self.username = row[0]['username']
				self.current_window = window['password']
				msg = "Please enter your password " + row[0]['firstName']
				return msg

		# Password window
		if self.current_window == window['password']:
			self.cursor.execute("SELECT * FROM Users WHERE username  = %s", self.username)
			row = self.cursor.fetchall()
			if row[0]['password'] == client_msg:
				self.current_window = window['welcome']
				return self.welcome_options()
			else:
				msg = "Sorry, password incorrect, please try again"
				return msg

		# Companies page
		if self.current_window == window['welcome']:
			if client_msg == '1':
				return self.my_profiles()
			else: 
				return "Not a valid option " + client_msg + "\n" + self.welcome_options()

		else:
			print "dude, this is window " + str(self.current_window) + " and client message was " + client_msg
			return "dude, this is window " + str(self.current_window) + " and client message was " + client_msg
			
