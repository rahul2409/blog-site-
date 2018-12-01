from flask import Flask , render_template, flash, redirect, url_for, session, logging, request 
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt 


app= Flask(__name__)

#configure mysql 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'blog_site'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


# initialize sql 
mysql = MySQL(app)


articles = Articles()


@app.route('/')
def index():
	return render_template('home.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/posts')
def posts():
	return render_template('posts.html', articles=Articles())

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
		result = cursor.execute("select * from users where username =%s ",(username))

		#check the result 
		if (result > 0):
			data = cursor.fetchone()
			password = data['password']

			#comparing the passwords 
			if (sha256_crypt.verify(candidate_password,password)):
				app.logger.info('password matched ')
			else :
				app.logger.info('password not matched ')
		else :
			app.logger.info('no username')
	return render_template('login.html')

if __name__ == '__main__' :
	app.secret_key='mrrobo123'
	app.run(debug=True)