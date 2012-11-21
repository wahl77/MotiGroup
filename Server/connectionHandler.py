import socket
import threading
import MySQLdb as mdb
import sys
import math

SIZE = 4

db = mdb.connect(host='localhost', user='root', passwd='', db='MotiGroup')

class ConnectionHandler(threading.Thread):
	def __init__(self, client_socket):
		self.socket = client_socket
		threading.Thread.__init__(self)
		self.username = ""
		self.user_browsing = ""
		with db:
			self.cursor = db.cursor(mdb.cursors.DictCursor)

	def message_recv(self):
		data = self.socket.recv(SIZE)
		self.socket.send('OK') # Send a ready to receive signal
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
		self.login("Welcome to MotiGroup\nPlease enter you login")
		print "Socket closing" 
		self.message_send('EOF')
		self.socket.close()
	
# ----------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------

	

	# def find_user(self, username):
	# 	self.cursor.execute("SELECT * FROM Users")
	# 	row = self.cursor.fetchall()
	# 	if len(row) == 0:
	# 		return "Sorry, username not found\nPlease enter your username"
	# 	else:
	# 		print "Here are the options for..."
	# 		print "Sorry user ... does not work for your company"
	# 	return "ABC"

# ---------------------------

		
	# Returns True if user is in the whole database
	def user_exist(self, username):
		self.cursor.execute("SELECT * FROM Users WHERE username = %s", username)
		row = self.cursor.fetchall()
		if len(row) == 0:        # Username does not exist
			return False
		else:
			return True
		
		
	# Get username at login
	def login(self, msg):
		self.message_send(msg)
		self.username = self.message_recv()
		if self.user_exist(self.username):        # Username is invalid
#			self.check_password("Please enter your password\n")
			self.welcome_menu("Welcom\n")
		else:
		  login("Sorry, username not found\nPlease enter your username")

		
	# Validate for password
	def check_password(self, msg):
		self.message_send(msg)
		password = self.message_recv()
		self.cursor.execute("SELECT * FROM Users WHERE username  = %s", self.username)
		row = self.cursor.fetchall()
		if row[0]['password'] == password: # Password is correct
			self.welcome_menu("Welcome to MotiGroup\n")
		else:
			self.check_password("Sorry, password incorrect, please try again")


	# This is the first menu that shows up when a user logged in
	def welcome_menu(self, msg):
		options = {0: 'Please enter a username (UUN) or type:', 1: 'Account Status', 2: 'List of usernames', 3: 'Manage company', 4: 'View my companies', 5: 'Assigned Grades'}
		msg += options[0]
		for i in range(1, len(options)):
			msg += "\n\t" + str(i) + ") " + options[i]
		self.message_send(msg)
		response = self.message_recv()
		if response == '2':
			msg = self.get_user_list()
			self.welcome_menu(msg)
		elif response == '4':
			msg = self.my_companies()
			self.welcome_menu(msg)
		elif response == '5':
			self.welcome_menu(self.get_prev_grades())
		elif response == 'q':
			return
		else:
			self.get_user(response)
			

	# My companies, returns a list of companies you belong to
	def my_companies(self): 
		msg = "You belong to the following companies: \n"
		self.cursor.execute("SELECT Users.username, Companies.company_name FROM Users, UserCompany, Companies WHERE Users.username = %s  AND Users.username = UserCompany.username AND Companies.company_id = UserCompany.company_id", self.username) 
		rows = self.cursor.fetchall()
		for i in range(0, len(rows)):
			msg += "\t" + rows[i]['company_name'] + "\n"
		return msg


	# This returns a string that is a list of users which are reachable by a person
	def get_user_list(self):
		query = 'SELECT Users.username, Users.firstName, Users.lastName FROM Users, UserCompany WHERE UserCompany.company_id IN (SELECT Companies.company_id FROM Users, UserCompany, Companies WHERE Users.username = \'' + self.username + '\'AND Users.username = UserCompany.username AND Companies.company_id = UserCompany.company_id) AND Users.username = UserCompany.username ORDER BY lastName'
		self.cursor.execute(query)
		rows = self.cursor.fetchall()
		msg = "{0:25}{1:25}{2:25}\n".format('Username', 'Last Name', 'First Name')
		msg += '-------------------------------------------------------------------------------------\n'
		for i in range(0, len(rows)):	
			if rows[i]['username'] != self.username:
				msg += '{0:25}{1:25}{2:25}\n'.format(rows[i]['username'], rows[i]['lastName'], rows[i]['firstName'])
		msg += '-------------------------------------------------------------------------------------\n'
		return msg

	# Find a user related to us
	def get_user(self, username):
		query = 'SELECT * FROM Users WHERE Users.username IN (SELECT Users.username FROM Users, UserCompany WHERE UserCompany.company_id IN (SELECT Companies.company_id FROM Users, UserCompany, Companies WHERE Users.username = \'' + self.username + '\' AND Users.username = UserCompany.username AND Companies.company_id = UserCompany.company_id) AND Users.username = UserCompany.username) and Users.username = \'' +  username + '\''
		self.cursor.execute(query)
		row = self.cursor.fetchall()
		if len(row) != 1:
			self.welcome_menu("Sorry, no match found\n")
		else:
			self.user_browsing = row[0]['username']
			choice = "Your choice is to grade " + row[0]['username'] + ": " + row[0]['firstName'] + " " + row[0]['lastName'] + "? [y/n]"
			if self.get_confirmation(choice):
				self.grade_user()
			else:
				self.welcome_menu("You abandoned inputing data\n")

	def grade_user(self):
		can_grade = self.can_grade()
		if can_grade[0] == 0:
			grade = self.request_grade(can_grade[1])
			self.welcome_menu("You have successfully graded " + self.user_browsing + "\n")
		else:
			self.welcome_menu(can_grade[1])

	# Previously graded
	def get_prev_grades(self):
		query = "SELECT * FROM Grades WHERE Timestamp > DATE_SUB(NOW(), INTERVAL DAYOFMONTH(NOW()) DAY) AND Grades.From = \'" + self.username + "\'"
		self.cursor.execute(query)
		total = 0
		rows = self.cursor.fetchall()
		msg = "Current Grading : \n{0:25}{1:10}\n".format("Username", "Grade")
		msg += "--------------------------------------------------------------\n"
		for i in range(0, len(rows)):
			msg += "{0:25}{1:3}\n".format(rows[i]['To'], rows[i]['Grade'])
			total += rows[i]['Grade']
		msg += "You now have " + str(100-total) + " points to give out\n"
		return msg



	# Verify user is still eligible to grade someone
	def can_grade(self):
		query = "SELECT SUM(Grade) FROM Grades WHERE Timestamp > DATE_SUB(NOW(), INTERVAL DAYOFMONTH(NOW()) DAY) AND Grades.From = \'" + self.username + "\'"
		self.cursor.execute(query)
		rows = self.cursor.fetchall()
		total = rows[0]['SUM(Grade)']

		if self.username == self.user_browsing:
			msg = "You cannot give yourself a grade\n"
			return (1,msg)
		elif total >= 100 and total != None:
			print type(total)
			msg = "You have already reached your quota this month\n" + self.get_prev_grades()
			return (2,msg)
		else: 
			msg = self.get_prev_grades() + "You can now grade\n" 
			return (0,msg)

		
	# Get a confirmation of a message
	def get_confirmation(self, string):
		yes = set(['Yes', 'yes', 'y', 'YES', 'Y'])
		self.message_send(string)
		confirmation = self.message_recv()
		if confirmation in yes:
			return True
		else:
			return False


	def request_grade(self, msg):
		msg += "Please enter a valid grade\n"
		self.message_send(msg)
		try: 
			grade = int(self.message_recv())
		except:
			self.request_grade(msg)
			return

		if grade > 100 or grade < 0:
			self.request_grade(msg)
		else:
			if self.get_confirmation("You have attributed " + str(grade) + " to " + self.user_browsing + "?[yes/no]"):
				try: 
					query = "INSERT INTO Grades (`From`, `To`, `Timestamp`, `Grade`, `Comment`) VALUES ('" + self.username + "', '" + self.user_browsing + "', CURRENT_TIMESTAMP, '"+ str(grade) +"', '')"
					self.cursor.execute(query)
					db.commit()
				except: 
					print "Error processing query"
					db.rollback()

