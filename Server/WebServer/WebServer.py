#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi
from mako.template import Template
import MySQLdb as mdb

PORT_NUMBER = 8080

db = mdb.connect(host='localhost', user='root', passwd='', db='MotiGroup')
cursor = db.cursor(mdb.cursors.DictCursor)
#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
	username = ""
	
	#Handler for the GET requests
	def do_GET(self):
		if self.path=="/":
			self.path="/index.html"

		try:
			#Check the file extension required and
			#set the right mime type

			sendReply = False
			if self.path.endswith(".html"):
				mimetype='text/html'
				sendReply = True
			if self.path.endswith(".jpg"):
				mimetype='image/jpg'
				sendReply = True
			if self.path.endswith(".gif"):
				mimetype='image/gif'
				sendReply = True
			if self.path.endswith(".js"):
				mimetype='application/javascript'
				sendReply = True
			if self.path.endswith(".css"):
				mimetype='text/css'
				sendReply = True

			if sendReply == True:
				#Open the static file requested and send it
				f = open(curdir + sep + self.path) 
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return


		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	#Handler for the POST requests
	def do_POST(self):
		form = cgi.FieldStorage(
			fp=self.rfile,
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
		               'CONTENT_TYPE':self.headers['Content-Type'],
		})
		if self.path=="/welcome.html":
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.username = form["your_name"].value
			password = form["your_password"].value
			if not self.check_password(password):
				txt = Template(filename = 'user_not_found.html').render()
			else:
				items = self.get_companies_list()
				txt = Template(filename = 'welcome.html').render(name=self.username, password="abc", items = items)

			self.wfile.write(txt)
			return
		if self.path == "/grades.html":
			print self.username
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			print self.username
			rows = self.get_prev_grades()
			txt = Template(filename = 'grades.html').render(rows = rows)
			self.wfile.write(txt)



	def get_user_list(self):
		query = 'SELECT Users.username, Users.firstName, Users.lastName FROM Users, UserCompany WHERE UserCompany.company_id IN (SELECT Companies.company_id FROM Users, UserCompany, Companies WHERE Users.username = \'' + self.username + '\'AND Users.username = UserCompany.username AND Companies.company_id = UserCompany.company_id) AND Users.username = UserCompany.username ORDER BY lastName'
		cursor.execute(query)
		return cursor.fetchall()

	# Previously graded table, returns a string
	def get_prev_grades(self):
		query = "SELECT * FROM Grades WHERE Timestamp > DATE_SUB(NOW(), INTERVAL DAYOFMONTH(NOW()) DAY) AND Grades.From = \'" + self.username + "\'"
		cursor.execute(query)
		return cursor.fetchall()

	def check_password(self, password):
		cursor.execute("SELECT * FROM Users WHERE username  = %s", self.username)
		row = cursor.fetchall()
		if len(row) == 1 and row[0]['password'] == password: # Password is correct
			return True
		else:
			return False

	def get_companies_list(self): 
		cursor.execute("SELECT Users.username, Companies.company_name, UserCompany.is_admin, Companies.company_id FROM Users, UserCompany, Companies WHERE Users.username = %s  AND Users.username = UserCompany.username AND Companies.company_id = UserCompany.company_id", self.username) 
		return cursor.fetchall()


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
	
