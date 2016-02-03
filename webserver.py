from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind=engine
DBsession = sessionmaker(bind=engine)
session= DBsession() 

class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				output = ""
				output += "<html><body>"
				output +="<h1> New Restaurant </h1>"
				output += "<form method = 'POST' enctype='multipart/form-data' action ='/restaurants/new'>"
				output += "<h2>Create a new restaurant</h2><input name='name' type='text'>"
				output += "<input type ='submit' value = 'Create'></form>"
				output += "</body></html>"
				self.wfile.write(output)
				return

			if self.path.endswith("/restaurants"):
				result=session.query(Restaurant).all()
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				output=""
				output+="<html><body>"
				output += "<a href = '/restaurants/new' > Make a New Restaurant Here </a></br></br>"
				output+="<br>"
				for res in result:
					output+="<br>"
					output+=res.name
					output+="<br>"
					output+="<a href='restaurants/%s/edit' >Edit</a>"%res.id
					output+="<br>"
					output+="<a href='restaurants/%s/delete'>Delete</a>"%res.id
					output+="<br>"
				output+=""
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return
			if self.path.endswith("/edit"):
				idnumber = self.path.split("/")[2]
				editrestaurant=session.query(Restaurant).filter_by(id=idnumber).one()
				if editrestaurant:
					self.send_response(200)
					self.send_header('Content-type','text/html')
					self.end_headers()
					output = ""
					output += "<html><body>"
					output += "<form method = 'POST' enctype='multipart/form-data' action ='/restaurants/%s/edit'>"%idnumber
					output += "<h2>Edit %s</h2>"%editrestaurant.name
					output += "<input name='name' type='text' placeholder='%s'>"%editrestaurant.name
					output += "<input type ='submit' value = 'Edit' ></form>"
					output += "</body></html>"
					self.wfile.write(output)
					
			if self.path.endswith("/delete"):
				idnumber = self.path.split("/")[2]
				deleterestaurant=session.query(Restaurant).filter_by(id=idnumber).one()
				if deleterestaurant:
					self.send_response(200)
					self.send_header('Content-type','text/html')
					self.end_headers()
					output = ""
					output += "<html><body>"
					output += "<form method = 'POST' enctype='multipart/form-data' action ='/restaurants/%s/delete'>"%idnumber
					output += "<h2>Are you sure you wanna delete %s ?</h2>"%deleterestaurant.name
					output += "<input type ='submit' value = 'Delete!' ></form>"
					output += "</body></html>"
					self.wfile.write(output)

		except IOError:
			self.send_error(404,"File Not Found %s"%self.path)

	def do_POST(self):
		try:
			
			if self.path.endswith("/restaurants/new"):
				ctype,pdict =cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields=cgi.parse_multipart(self.rfile,pdict)
					name1 = fields.get('name')


					#new restaurant object
					session.add(Restaurant(name=name1[0]))
					session.commit()

					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location','/restaurants')
					self.end_headers()

			if self.path.endswith("/edit"):
				ctype,pdict =cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields=cgi.parse_multipart(self.rfile,pdict)
					name1 = fields.get('name')
					idnumber = self.path.split("/")[2]

					editrestaurant = session.query(Restaurant).filter_by(id = idnumber).one()
					if (editrestaurant != []):
						editrestaurant.name=name1[0]
						session.add(editrestaurant)
						session.commit()

						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						self.send_header('Location','/restaurants')
						self.end_headers()

			if self.path.endswith("/delete"):
				ctype,pdict =cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					
					idnumber = self.path.split("/")[2]

					deleterestaurant = session.query(Restaurant).filter_by(id = idnumber).one()
					if (deleterestaurant != []):
						
						session.delete(deleterestaurant)
						session.commit()

						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						self.send_header('Location','/restaurants')
						self.end_headers()
					
		except:
			pass


def main():		

	try:
		port= 8080
		server = HTTPServer(('',port), webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()

	except KeyboardInterrupt:
		print "^C entered, Stopping the webserver.."
		server.socket.close()
if __name__ == '__main__':
		main()