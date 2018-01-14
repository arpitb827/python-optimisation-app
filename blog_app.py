from flask import Flask, render_template
app = Flask(__name__, template_folder='templates')


@app.route("/")
def index():
   return render_template("blog.html")


@app.route("/sign_in")
def open_login():
	return render_template("login_activity.html")

@app.route("/create_account")
def create_login():	
	return render_template("create_account.html")

@app.route("/password_reset")
def forgot_password():
	return render_template("forgot_password.html")
if __name__ == '__main__':
   app.run(debug=True)
