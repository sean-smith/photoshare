######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################
from PIL import Image
from cStringIO import StringIO
from resizeimage import resizeimage
import os, base64
from image import resize

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login

#for image uploading
from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'newpassword'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = '0.0.0.0'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users") 
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users") 
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd 
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out') 

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')  

@app.route("/register", methods=['POST'])
def register_user():
	try:
		fname=request.form.get('fname')
		lname=request.form.get('lname')
		dob=request.form.get('dob')
		email=request.form.get('email')
		password=request.form.get('password')
	except:
		print "couldn't find all tokens" #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	unique =  isEmailUnique(email)
	if unique:
		print cursor.execute("INSERT INTO Users (email, password, fname, lname, dob) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')".format(email, password, fname, lname, dob))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print "Email taken."
		return render_template('hello.html', message="Email already taken. Perhaps login?")

@app.route('/friends', methods=['GET', 'POST'])
@flask_login.login_required
def friends():
	if flask.request.method == 'GET':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		friends = getFriends(uid)
		return render_template('hello.html', friends=friends) 
	else:
		try:
			friend_email=request.form.get('email')
		except:
			print "couldn't find all tokens" #this prints to shell, end users will not see this (all print statements go to shell)
			return flask.redirect(flask.url_for('friends'))
		
		cursor = conn.cursor()
		yours = getUserIdFromEmail(flask_login.current_user.id)
		friends = getUserIdFromEmail(friend_email)
		try:
			cursor.execute("INSERT INTO Friends (to_who, from_who) VALUES ('{0}', '{1}')".format(friends, yours))
		except:
			return flask.redirect(flask.url_for('friends'))
		conn.commit()

		return flask.redirect(flask.url_for('friends'))




# Fetches a list of photos [(img_thumb, name)]
@app.route('/album/<int:id>', methods=['GET'])
def getPictures(id):
	cursor = conn.cursor()
	cursor.execute("SELECT thumbnail, caption FROM Photos p WHERE album_id = '{0}'".format(id))
	data = cursor.fetchall()
	return render_template('photos.html', type="Album", photos=data)

@app.route('/albums', methods=['GET'])
def albums():
	cursor = conn.cursor()
	cursor.execute("SELECT thumbnail, name FROM Albums")
	data = cursor.fetchall()
	return render_template('photos.html', type="Albums", photos=data)


def getAlbums():
	cursor = conn.cursor()
	cursor.execute("SELECT name, thumbnail FROM Albums")
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getFriends(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT s.fname, s.lname FROM Friends f, Users s WHERE from_who = '{0}' and s.user_id = f.to_who".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Photos WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		print caption
		photo_data = base64.standard_b64encode(imgfile.read())
		thumbnail = resize(photo_data, 200, 200)
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Photos (imgdata, thumbnail, user_id, caption) VALUES ('{0}', '{1}', '{2}', '{3}')".format(photo_data, thumbnail, uid, caption))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid) )
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code 

# resizes if greater than (x,y) else returns original
def resize(img, x,y):
	image_string = StringIO(img.decode('base64'))
	with Image.open(image_string) as image:
		if image.size[0] > 200 and image.size[1] > 200:
			cover = resizeimage.resize_cover(image, [x,y])
			buffer = StringIO()
			cover.save(buffer, format="JPEG")
			return base64.b64encode(buffer.getvalue())
		else:
			return img
#default page  
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welcome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run 
	#$ python app.py 
	app.run(port=5000, debug=True)
