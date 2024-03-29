#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi
import os
from mako.template import Template
import MySQLdb as mdb
import Cookie
import time
import sha

PORT_NUMBER = 8080

db = mdb.connect(host='localhost', user='root', passwd='', db='MotiGroup')

cursor = db.cursor(mdb.cursors.DictCursor)
#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
	def do_GET(self):
		if self.path=="/":
			self.path="/index.html"


			#Open the static file requested and send it
			f = open(curdir + sep + self.path) 
			self.send_response(200)
			self.send_header('Content-type:','text/html')
			self.end_headers()
			self.wfile.write(f.read())
			f.close()
			return

	#Handler for the POST requests
	def do_POST(self):
		form = cgi.FieldStorage(
			fp=self.rfile,
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
		               'CONTENT_TYPE':self.headers['Content-Type'],
		})


		if self.path=="/welcome.html":
			username = form["your_name"].value
			password = form["your_password"].value

			if not self.check_password(username, password):
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				txt = Template(filename = 'user_not_found.html').render()
				return
				
			else:
				session_id = sha.new(repr(time.time())).hexdigest()
				cookie = Cookie.SimpleCookie()
				cookie['username'] = username
				cookie['sid'] = session_id
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.send_header('Set-Cookie',cookie.output())

			items = self.get_companies_list(username)
			people = self.get_user_list(username)
			grade = self.get_prev_grades(username)
			total = 0
			self.end_headers()
			txt = Template(filename = 'welcome.html').render(name=username, items = items, people = people, grade = grade, total = total)
			print total

			self.wfile.write(txt)
			return

		if self.headers.has_key('cookie'):
			cookie = Cookie.SimpleCookie(self.headers.getheader("cookie"))
			username = cookie["username"].value

		if self.path == "/grade.html":
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			person = form["person"].value
			grade = int(form["grade"].value)
			print "From: To: Grade", username, person, grade
			if self.validate_grade(username, person, grade) == True: 
				html_txt = "You have successfully graded the following person"
			else:
				html_txt = "This would exceed your quota this month"
			txt = Template(filename = 'grade.html').render(html_txt = html_txt, person = person, grade = grade)
			self.wfile.write(txt)
			return

	def check_password(self, username, password):
		cursor.execute("SELECT * FROM Users WHERE username  = %s", username)
		row = cursor.fetchall()
		if len(row) == 1 and row[0]['password'] == password: # Password is correct
			return True
		else:
			return False

	def get_companies_list(self, username): 
		cursor.execute("SELECT Users.username, Companies.company_name, UserCompany.is_admin, Companies.company_id FROM Users, UserCompany, Companies WHERE Users.username = %s  AND Users.username = UserCompany.username AND Companies.company_id = UserCompany.company_id", username) 
		return cursor.fetchall()

	def get_prev_grades(self, username):
		query = "SELECT * FROM Grades WHERE Timestamp > DATE_SUB(NOW(), INTERVAL DAYOFMONTH(NOW()) DAY) AND Grades.From = \'" + username + "\'"
		cursor.execute(query)
		return cursor.fetchall()

	def get_user_list(self, username):
		query = 'SELECT Users.username, Users.firstName, Users.lastName FROM Users, UserCompany WHERE UserCompany.company_id IN (SELECT Companies.company_id FROM Users, UserCompany, Companies WHERE Users.username = \'' + username + '\'AND Users.username = UserCompany.username AND Companies.company_id = UserCompany.company_id) AND Users.username = UserCompany.username ORDER BY lastName'
		cursor.execute(query)
		rows = cursor.fetchall()
		return rows
		self.msg = "{0:25}{1:25}{2:25}\n".format('Username', 'Last Name', 'First Name')

	# Make sure grade is valid and user is eligible to grade
	# Username is the person inputing the data
	# Person is the person receiving the grade
	def validate_grade(self, username, person, grade):
		query = "SELECT SUM(Grade) FROM Grades WHERE Timestamp > DATE_SUB(NOW(), INTERVAL DAYOFMONTH(NOW()) DAY) AND Grades.From = \'" + username + "\'"
		cursor.execute(query)
		rows = cursor.fetchall()
		total = rows[0]['SUM(Grade)']

		if total == None:
			total = grade
		else:
			total += grade

		if total > 100:
			return False
		else: 
			try: 
				query = "INSERT INTO Grades (`From`, `To`, `Timestamp`, `Grade`, `Comment`) VALUES ('" + username + "', '" + person + "', CURRENT_TIMESTAMP, '"+ str(grade) +"', '')"
				cursor.execute(query)
				db.commit()
				self.msg = "Grade assigned properly.\nWelcome back to main menu"
			except: 
				print "Error processing query"
				return False
			return True

	# Get a confirmation of a message
	def get_confirmation(self, ):
		yes = set(['Yes', 'yes', 'y', 'YES', 'Y'])
		confirmation = self.send_recv()

try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print 'Started httpserver on port ' , PORT_NUMBER
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()
