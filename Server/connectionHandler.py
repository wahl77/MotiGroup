import socket
import threading
import MySQLdb as mdb
import sys

SIZE = 4

window = {'connection_established': '-1', 'login_username': '0', 'login_password': '1', 'welcome_menu': '2', 'find_user' : '3', 'my_companies': '4', 'list_user':'5'}

db = mdb.connect(host='localhost', user='root', passwd='', db='MotiGroup')

class ConnectionHandler(threading.Thread):
	def __init__(self, client_socket):
		self.socket = client_socket
		threading.Thread.__init__(self)
		self.username = ""
		self.current_window = window['connection_established']
		with db:
			self.cursor = db.cursor(mdb.cursors.DictCursor)

	def message_recv(self, socket):
		data = self.socket.recv(SIZE)
		socket.send('OK') # Send a ready to receive signal
		msg = self.socket.recv(int(data))
		print 'Received --> ', msg
		return msg
	
	def message_send(self, msg):
		if len(msg) <= 999 and len(msg) > 0:
			self.socket.send(str(len(msg)))
			if self.socket.recv(2) == 'OK':
				self.socket.send(msg)
		else:
			conn.send(str(999))
			if self.socket.recv(2) == 'OK':
				self.socket.send(msg[:999])
				self.message_send(msg[1000:])
	
	def run(self):
		client_msg = ""
		while 1:
			if client_msg == 'q':
				self.message_send('EOF')
				break
			else:
				self.handle_message(client_msg)
				client_msg = self.message_recv(self.socket)
		print "Socket closing" 
		self.socket.close()
	
# ----------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------


	# Return a string with the list of options for the welcome page
	# def welcome_options(self):
	# 	options = {0: 'What would  you like to do?', 1: 'View my profile', 2:'View somebody\'s profile', 3:'Reward someone)',}
	# 	options_admin = {0: 'Add a user', 1: 'Remove a user',}
	# 	is_admin = True
	# 	msg = options[0]
	# 	for i in range(1, len(options)):
	# 		msg += "\n\t" + str(i) + ") " + options[i]
	# 	if is_admin:
	# 		for i in range(0, len(options_admin)):
	# 			msg += "\n\t" + str(i+len(options)) + ") " + options_admin[i]
	# 	return msg
	
	# My companies, returns a list of companies you belong to

	# def find_user(self, username):
	# 	self.cursor.execute("SELECT * FROM Users")
	# 	row = self.cursor.fetchall()
	# 	if len(row) == 0:
	# 		return "Sorry, username not found\nPlease enter your username"
	# 	else:
	# 		print "Here are the options for..."
	# 		print "Sorry user ... does not work for your company"
	# 	return "ABC"


	# This returns a string that is a list of users which are reachable by a person
	def get_user_list(self):
		self.cursor.execute("SELECT Users.username, Users.firstName, Users.lastName FROM Users, UserCompany WHERE UserCompany.company_id IN (SELECT Companies.company_id FROM Users, UserCompany, Companies WHERE Users.username = %s AND Users.username = UserCompany.username AND Companies.company_id = UserCompany.company_id) AND Users.username = UserCompany.username", self.username)
		row = self.cursor.fetchall()
		msg = "Users are \n"
		for i in range(0, len(row)):	
			if row[i]['username'] != self.username:
				msg += row[i]['username'] + row[i]['firstName'] + row[i]['lastName'] + "\n"
		return msg
			

	# This returns a string with all companies you belong to
	def my_companies(self): 
		msg = "You belong to the following companies: \n"
		self.cursor.execute("SELECT Users.username, Companies.company_name FROM Users, UserCompany, Companies WHERE Users.username = %s  AND Users.username = UserCompany.username AND Companies.company_id = UserCompany.company_id", self.username) 
		rows = self.cursor.fetchall()
		for i in range(0, len(rows)):
			msg += "\t" + rows[i]['company_name'] + "\n"
		return msg

	# This is the first menu that shows up when a user logged in
	def welcome_menu(self):
		options = {0: 'Please enter a username (UUN) or type:', 1: 'Account Status', 2: 'List of usernames', 3: 'Manage company', 4: 'View my companies'}
		msg = options[0]
		for i in range(1, len(options)):
			msg += "\n\t" + str(i) + ") " + options[i]
		return msg


	def request_login_username(self):
		msg = "Please enter your username"
		self.current_window = window['login_username']
		return msg

	def validate_login_username(self, username):
		self.cursor.execute("SELECT * FROM Users WHERE username = %s", username)
		row = self.cursor.fetchall()
		if len(row) == 0:        # Username is invalid
			msg = "Sorry, username not found\nPlease enter your username"
		else:                    # Username is valid
			self.username = row[0]['username']
			self.current_window = window['login_password']
			msg = "Please enter your password " + row[0]['firstName']
			self.current_window = window['login_password']
		return msg

	def validate_login_password(self, password):
		self.cursor.execute("SELECT * FROM Users WHERE username  = %s", self.username)
		row = self.cursor.fetchall()
		if row[0]['password'] == password: # Password is correct
			self.current_window = window['welcome_menu']
			msg = self.welcome_menu()
		else:
			msg = "Sorry, password incorrect, please try again"
		return msg


	def handle_message(self, client_msg):

		# Connection established, send request for uun
		if self.current_window == window['connection_established']:
			msg = self.request_login_username()

		# Login window
		elif self.current_window == window['login_username']:
			msg = self.validate_login_username(client_msg)

		# Validate password
		elif self.current_window == window['login_password']:
			msg = self.validate_login_password(client_msg)

		# Welcome page
		elif self.current_window == window['welcome_menu']:
			if client_msg ==  '2':
				user_list = self.get_user_list()
				msg = user_list + "OK"
			elif client_msg == '4':
				msg = self.my_companies()
			msg += self.welcome_menu()

		else:
			print "dude, this is window " + str(self.current_window) + " and client message was " + client_msg
			
		self.message_send(msg)
		print "\nYour replied to: " + self.socket.getsockname()[0] + str(self.socket.getsockname()[1]) + self.socket.getpeername()[0]  + str(self.socket.getpeername()[1]) + "\n " + msg

