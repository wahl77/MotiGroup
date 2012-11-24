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
		self.msg = ""
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
		self.msg = "Welcome to MotiGroup\nPlease enter you login"
		self.login()
		print "Socket closing" 
		self.message_send('EOF')
		self.socket.close()
	

	def send_recv(self):
		self.message_send(self.msg)
		return self.message_recv()
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
	def login(self):
		self.username = self.send_recv()
		if self.user_exist(self.username):        # Username is invalid
			#self.check_password()
			self.welcome_menu()
		else:
			self.msg = "Sorry, username not found\nPlease enter your username"
			self.login()

		
	# Validate for password
	def check_password(self):
		self.msg="Please enter your password\n"
		password = self.send_recv()
		self.cursor.execute("SELECT * FROM Users WHERE username  = %s", self.username)
		row = self.cursor.fetchall()
		if row[0]['password'] == password: # Password is correct
			self.msg = "Welcome to MotiGroup\n"
			return
		else:
			self.msg = "Sorry, password incorrect, please try again"
			self.check_password()


	# This is the first menu that shows up when a user logged in
	def welcome_menu(self):
		while True:
			options = {0: 'Please enter a username (UUN) or type:', 1: 'Account Status', 2: 'List of usernames', 3: 'Manage company', 4: 'View my companies', 5: 'Assigned Grades'}
			self.msg += options[0]
			for i in range(1, len(options)):
				self.msg += "\n\t" + str(i) + ") " + options[i]
			response = self.send_recv()
			if response == '2':
				self.get_user_list()
			elif response == '3':
				self.manage_companies_list()
			elif response == '4':
				self.print_companies(self.username)
			elif response == '5':
				self.get_prev_grades()
			elif response == 'q':
				break
			else:
				self.get_user(response)
		
			


	# Returns a list of companies manageable by a user
	def manage_companies_list(self):
		rows = self.get_companies_list(self.username)
		has_admin = False
		self.msg = "You can administer the following companies\n"
		counter = 0
		company_under_management = []
		for i in range(0, len(rows)):
				if rows[i]['is_admin'] == 1:
					has_admin = True
					counter += 1
					self.msg += "{0:3}){1:20}\n".format(counter, rows[i]['company_name'])
					company_under_management.append(rows[i]['company_id'])
		if has_admin == False:
			self.msg = "Sorry, you cannot administer a company"
			return
		else: 
			self.manage_company(company_under_management)
			return
	
	def manage_company(self, companies):
		self.msg += "Please select a company to manage"
		company = self.send_recv()
		self.msg = "You chose to administer company with id :" + str(companies[int(company)-1])
		return

	def print_companies(self, user):
		self.msg = "You belong to the following companies:\n"
		rows = self.get_companies_list(user)
		self.msg +="{0:20}{1:5}\n".format("Company Name", "Administrator")
		for i in range(0, len(rows)):
			if rows[i]['is_admin'] == 1:
				self.msg += "{0:20}{1:5}\n".format(rows[i]['company_name'], "Yes")
			else:
				self.msg += "{0:20}{1:5}\n".format(rows[i]['company_name'], "No")
			
	# My companies, returns a list of companies you belong to
	def get_companies_list(self, user): 
		self.cursor.execute("SELECT Users.username, Companies.company_name, UserCompany.is_admin, Companies.company_id FROM Users, UserCompany, Companies WHERE Users.username = %s  AND Users.username = UserCompany.username AND Companies.company_id = UserCompany.company_id", user) 
		return self.cursor.fetchall()

	# This returns a string that is a list of users which are reachable by a person
	def get_user_list(self):
		query = 'SELECT Users.username, Users.firstName, Users.lastName FROM Users, UserCompany WHERE UserCompany.company_id IN (SELECT Companies.company_id FROM Users, UserCompany, Companies WHERE Users.username = \'' + self.username + '\'AND Users.username = UserCompany.username AND Companies.company_id = UserCompany.company_id) AND Users.username = UserCompany.username ORDER BY lastName'
		self.cursor.execute(query)
		rows = self.cursor.fetchall()
		self.msg = "{0:25}{1:25}{2:25}\n".format('Username', 'Last Name', 'First Name')
		self.msg += '-------------------------------------------------------------------------------------\n'
		for i in range(0, len(rows)):	
			if rows[i]['username'] != self.username:
				self.msg += '{0:25}{1:25}{2:25}\n'.format(rows[i]['username'], rows[i]['lastName'], rows[i]['firstName'])
		self.msg += '-------------------------------------------------------------------------------------\n'

	# Find a user related to us
	def get_user(self, username):
		query = 'SELECT * FROM Users WHERE Users.username IN (SELECT Users.username FROM Users, UserCompany WHERE UserCompany.company_id IN (SELECT Companies.company_id FROM Users, UserCompany, Companies WHERE Users.username = \'' + self.username + '\' AND Users.username = UserCompany.username AND Companies.company_id = UserCompany.company_id) AND Users.username = UserCompany.username) and Users.username = \'' +  username + '\''
		self.cursor.execute(query)
		row = self.cursor.fetchall()
		if len(row) != 1:
			self.msg = "Sorry, no match found\n"
			return
		else:
			self.user_browsing = row[0]['username']
			choice = "Your choice is to grade " + row[0]['username'] + ": " + row[0]['firstName'] + " " + row[0]['lastName'] + "? [y/n]"
			self.msg = choice
			if self.get_confirmation():
				self.request_grade()
			else:
				self.msg = "You abandonned inputing data\n"
				return

	# Previously graded table, returns a string
	def get_prev_grades(self):
		query = "SELECT * FROM Grades WHERE Timestamp > DATE_SUB(NOW(), INTERVAL DAYOFMONTH(NOW()) DAY) AND Grades.From = \'" + self.username + "\'"
		self.cursor.execute(query)
		total = 0
		rows = self.cursor.fetchall()
		self.msg = "Current Grading : \n{0:25}{1:10}\n".format("Username", "Grade")
		self.msg += "--------------------------------------------------------------\n"
		for i in range(0, len(rows)):
			self.msg += "{0:25}{1:3}\n".format(rows[i]['To'], rows[i]['Grade'])
			total += rows[i]['Grade']
		self.msg += "You now have " + str(100-total) + " points to give out\n"


	# Make sure grade is valid and user is eligible to grade
	def validate_grade(self, grade):
		query = "SELECT SUM(Grade) FROM Grades WHERE Timestamp > DATE_SUB(NOW(), INTERVAL DAYOFMONTH(NOW()) DAY) AND Grades.From = \'" + self.username + "\'"
		self.cursor.execute(query)
		rows = self.cursor.fetchall()
		total = rows[0]['SUM(Grade)']

		if total == None:
			total = grade
		else:
			total += grade

		if self.username == self.user_browsing or grade == 0:
			self.msg = "You cannot give yourself a grade nor can you give a 0 grade\n"
			return False
		if total > 100:
			self.msg = "This would exceeded your quota this month\n"
			return False
		else: 
			return True

	# Get a confirmation of a message
	def get_confirmation(self, ):
		yes = set(['Yes', 'yes', 'y', 'YES', 'Y'])
		confirmation = self.send_recv()
		if confirmation in yes:
			return True
		else:
			return False
	

	# Get a grade from user
	def request_grade(self):
		self.msg = "Please enter a valid grade or hit q for main menu\n"
		value = self.send_recv()
		try: 
			grade = int(value)
		except:
			self.msg = "Welcome back to main menu\n"
			return

		if not self.validate_grade(grade):
			return	
		else:
			self.msg = "You have attributed " + str(grade) + " to " + self.user_browsing + "?[yes/no]"
			if self.get_confirmation():
				try: 
					query = "INSERT INTO Grades (`From`, `To`, `Timestamp`, `Grade`, `Comment`) VALUES ('" + self.username + "', '" + self.user_browsing + "', CURRENT_TIMESTAMP, '"+ str(grade) +"', '')"
					self.cursor.execute(query)
					db.commit()
					self.msg = "Grade assigned properly.\nWelcome back to main menu"
				except: 
					print "Error processing query"
					db.rollback()
