from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = '12345mnbvc'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'dataDB'

mysql = MySQL(app)

def listAllTodos(username):
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT id FROM users WHERE username = % s', (username, ))
		user_id = cursor.fetchone()
		a = (list(user_id.values()))[0]
		cursor.execute('SELECT * FROM todos where user_id = % s', (a, ))
		allTodo = cursor.fetchall()
		return allTodo

@app.route('/login', methods =['GET', 'POST'])
@app.route('/addTodo', methods =['GET', 'POST'])
def login():
	msg = ''

	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		global username
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE username = % s AND password = % s', (username, password, ))
		account = cursor.fetchone()
		
		if account:
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			msg = 'Logged in successfully !'
			return render_template('todo.html', allTodo = listAllTodos(username))
		else:
			msg = 'Incorrect username / password !'

	if request.method == 'POST' and 'title' in request.form and 'description' in request.form:
		title = request.form['title']
		description = request.form['description']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT id FROM users WHERE username = % s', (username, ))
		user_id = cursor.fetchone()
		a = list(user_id.values())[0]	
		now = datetime.now()
		cursor.execute('INSERT INTO todos VALUES (NULL, %s, %s, %s, %s)', (a, title, description, now.strftime('%Y-%m-%d %H:%M:%S')))
		mysql.connection.commit()
		msg = 'Todo added successfully !'
		return render_template('todo.html', allTodo = listAllTodos(username), msg = msg)
	return render_template('login.html', msg = msg)

@app.route('/')
def index():
	return render_template('about.html')

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
	if request.method=='POST' and ('title' in request.form or 'description' in request.form):
		title = request.form['title']
		description = request.form['description']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		now = datetime.now()
		cursor.execute('UPDATE todos set title = %s, description = %s, date_created = %s WHERE id = %s', (title, description, now.strftime('%Y-%m-%d %H:%M:%S'), id))
		mysql.connection.commit()
		return render_template('todo.html', allTodo = listAllTodos(username))
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT title, description from todos where id = %s ',(id, ))
	rec = cursor.fetchall()
	return render_template('update.html', rec = rec[0], id = id)

@app.route("/delete/<int:id>")
def delete(id):
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('DELETE FROM todos where id = %s', (id, ))
	mysql.connection.commit()
	return render_template('todo.html', allTodo = listAllTodos(username))

if __name__ == '__main__':
    app.run(debug=True)