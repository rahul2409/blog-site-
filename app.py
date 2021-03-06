from flask import Flask , render_template, flash, redirect, url_for, session, logging, request 
#from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt 
from functools import wraps


app= Flask(__name__)

#configure mysql 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'blog_site'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


# initialize sql 
mysql = MySQL(app)


#articles = Articles()


@app.route('/')
def index():
	return render_template('home.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/posts')
def posts():
	# create a cursor 
	cur = mysql.connection.cursor()

	#get articles 
	result = cur.execute("Select * from acrticles")

	#fecth all 
	arcticles = cur.fetchall()

	if result>0:
		return render_template('posts.html',arcticles=arcticles)
	else :
		message='no available articles'
		return render_template('posts.html',message=message)
	return render_template('posts.html')

class Registration(Form):
	name =StringField('Name', [validators.Length(min=1,max=50)])
	username = StringField('Username',[validators.Length(min=4,max=25)])
	email= StringField('Email',[validators.Length(min=6,max=50)])
	password =PasswordField('Password',[ 
		validators.DataRequired(),
		validators.EqualTo('confirm',message='password do not match')]
	)
	confirm = PasswordField('Confirm password')
@app.route('/register', methods= ['GET', 'POST'])
def register():
	form = Registration(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email=form.email.data
		username = form.username.data 
		password = sha256_crypt.encrypt(str(form.password.data))

		#initializing server 
		cursor = mysql.connection.cursor()

		#execute query 
		cursor.execute("insert into users (name,email,username,password) values(%s,%s,%s,%s)",(name,email,username,password))

		# commiting to db 
		mysql.connection.commit()

		# close connection 
		cursor.close()

		flash('you are now registered and can login ','success')

		return redirect(url_for('index'))
	return render_template('register.html',form=form)
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		candidate_password = request.form['password']

		#create cursor 
		cursor = mysql.connection.cursor()

		#fire query
		result = cursor.execute("select * from users where username =%s ",[username])

		#check the result 
		if (result > 0):
			data = cursor.fetchone()
			password = data['password']

			#comparing the passwords 
			if (sha256_crypt.verify(candidate_password,password)):
				session['logged_in']=True
				session['username'] = username 

				flash('you are now logged in ','success')
				return redirect(url_for('dashboard'))
			else :
				error = 'Invalid Login '
				return render_template('login.html',error=error)
			#close the connection 
			cursor.close()
		else :
			error = 'User not found ! '
			return render_template('login.html',error=error)
	return render_template('login.html')

def is_logged_out(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else :
			flash('Unauthorized, Please login.','danger')
			return redirect(url_for('login'))
	return wrap
	
@app.route('/logout')
@is_logged_out
def logout():
	session.clear()
	flash('you are now logged out','success')
	return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_out
def dashboard ():
	# create a cursor 
	cur = mysql.connection.cursor()

	#get articles 
	result = cur.execute("Select * from acrticles where author = '%s'"% session['username'])

	#fecth all 
	arcticles = cur.fetchall()

	if result>0:
		return render_template('dashboard.html',arcticles=arcticles)
	else :
		message='no available articles'
		return render_template('dashboard.html',message=message)
	return render_template('dashboard.html')

class ArticleForm (Form):
	title = StringField('title', [validators.Length(min=1,max=200)])
	body = StringField('body',[validators.Length(min=30)])
	
@app.route('/add_article', methods =['GET','POST'])
@is_logged_out
def add_articles():
	form = ArticleForm(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body  = form.body.data


		cur= mysql.connection.cursor()

		cur.execute("insert into acrticles (title,body,author) values(%s,%s,%s)",(title,body,session['username']))

		mysql.connection.commit()

		cur.close()

		flash('Article created successfully ','success')

		return redirect(url_for('dashboard'))
	return render_template('add_article.html',form=form)
	
if __name__ == '__main__' :
	app.secret_key='mrrobo123'
	app.run(debug=True)