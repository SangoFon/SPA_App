MIYE- SPA 
=====
The web application is build with python Flask framwork along with SQLite3 database. 

## Requirements
1. Python 3.6, 
2. SQLite3 


## Setup
1. Install flask
$ pip install flask
$ pip install flask-wtf
$ pip install flask-sqlalchemy
$ pip install flask-migrate
$ pip install flask-login

2. Define the project
$ export FLASK_APP=database.py


3. Init the database

$ flask db init
$ flask db upgrade

4. Populate the database with dummy data(if weren't populated after migration)
$ python populate.py

5. Running

$ flask run

6. Open the app in browser: [localhost](http://127.0.0.1:5000/)

7. username:admin password:123456
   username:employee password:123456
