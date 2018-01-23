from flask import Flask, render_template, request, flash,redirect, url_for, session
from forms import LoginForm, RegisterForm,PasswordResetForm
from flask_sqlalchemy import SQLAlchemy
import datetime

#adding password security using werkzug
from werkzeug.security import generate_password_hash, check_password_hash

#adding flask login to resrict user to do first sign in 
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user


app = Flask(__name__, template_folder='templates')

app.config["SECRET_KEY"]="Thisisascretkey"
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://localhost/smartblog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'open_login'


class User(UserMixin,db.Model):

	__tablename__ = 'users'
	
	id = db.Column('id', db.Integer, db.Sequence('user_id_seq',start=1), primary_key=True,)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(80))
	email = db.Column(db.String(80), unique=True)
	created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route("/")
def index():
   return render_template("blog.html")

@app.route("/manage_blog")
@login_required
def manage_blog():
	data = User.query.all() 
	# return render_template("manage_blog.html", name=current_user.username,form=form, datas=data)
	return render_template("manage_blog.html", name=current_user.username, users=data)

@app.route("/sign_in", methods=["GET","POST"])
def open_login():
	form = LoginForm()
	if form.validate_on_submit():
		# return '<h1>'+form.username.data +' ' +form.password.data+ '</h1>'
		user = User.query.filter_by(username=form.username.data).first()
		try:
			if user:
				if check_password_hash(user.password,form.password.data) :
					login_user(user, remember=form.remember.data)
					return redirect(url_for('manage_blog'))
				else:
					flash("Password does not match.Forgot password ?")

		except Exception as e:
			flash("User does not exist ! Please signup first.")
 
	return render_template("login_activity.html",form=form)
	# return render_template("login_activity.html")

@app.route("/create_account", methods=["GET","POST"])
def create_login():
	form = RegisterForm()
	if form.validate_on_submit():
		hash_password = generate_password_hash(form.password.data,method='sha256')
		try :
			new_user = User(username=form.username.data, email=form.email.data, password= hash_password)
			db.session.add(new_user)
			db.session.commit()
			flash("User created sucessfully! now login.")
		except Exception as inst:
			flash("Email is already created!.")


		# return "New User Has been created!"
		# return '<h1>'+form.username.data +' ' +form.password.data+ '</h1>'

	return render_template("create_account.html", form=form)
	# return render_template("create_account.html")

@app.route("/logout")
@login_required
def log_out():
	logout_user()
	return redirect(url_for('open_login'))

@app.route("/password_reset", methods=["GET","POST"])
def forgot_password():
	form = PasswordResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		try:
			if user:
				#when both password are same
				if form.new_password.data == form.confirm_password.data:
					hash_password = generate_password_hash(form.confirm_password.data,method='sha256')
					user.password = hash_password
					db.session.commit()
					flash("Password reset sucessfully!.")
					# return '<h1>'+ 'Password is reset' +'</h1>'
				else:
					flash("Password not match!.")
		except Exception as e:
			flash("There is no user for this Email.")
		

	return render_template("forgot_password.html",form=form)
	# return render_template("forgot_password.html")

@app.route("/add_blog", methods=["GET","POST"])
def add_blog():

	render_template("add_blog.html")

if __name__ == '__main__':
	db.create_all()
   	app.run(debug=True)
