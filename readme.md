# Photoshare
### Sean Smith
### swsmith@bu.edu

This is my implementation of the photoshare project. It's a simple Flikr/Google Photos application that allows you to post photos to albums, like and tag photos.

To run:
	
	git clone https://github.com/sean-smith/photoshare
	cd photoshare
	pip install -r requirements.txt
	python app.py
	
Then go to https://localhost:5000 to check it out!

Note, you'll need a mysql db instance running for this to work.

	sudo apt-get install mysql-server
	
Then change lines 31 - 34 in `app.py`:

	app.config['MYSQL_DATABASE_USER'] = 'root' 
	app.config['MYSQL_DATABASE_PASSWORD'] = 'newpassword'	# your password
	app.config['MYSQL_DATABASE_DB'] = 'photoshare'		# need to create db
	app.config['MYSQL_DATABASE_HOST'] = '0.0.0.0'		# host running mysql
