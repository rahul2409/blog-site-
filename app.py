from flask import Flask , render_template
from data import Articles


app= Flask(__name__)
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

if __name__ == '__main__' :
	app.run(debug=True)