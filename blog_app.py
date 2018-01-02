from flask import Flask, render_template
app = Flask(__name__, template_folder='templates')


@app.route("/")
def index():
   return render_template("blog.html")


@app.route("/sign_in")
def open_login():
	return render_template("login_activity.html")
if __name__ == '__main__':
   app.run(debug=True)
