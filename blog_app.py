from flask import Flask, render_template, request, flash,redirect, url_for, session
from forms import LoginForm, RegisterForm,PasswordResetForm, EditUserForm
from flask_sqlalchemy import SQLAlchemy
import datetime

#adding password security using werkzug
from werkzeug.security import generate_password_hash, check_password_hash

#adding flask login to resrict user to do first sign in 
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

import operator

app = Flask(__name__, template_folder='templates')

app.config["SECRET_KEY"]="Thisisascretkey"
app.config['SQLALCHEMY_DATABASE_URI']='postgresql+psycopg2://arpit:honey@localhost/smartblog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'open_login'

class Blog(db.Model):
	__searchable__=['title','content']
	
	id = db.Column('id', db.Integer, primary_key=True)
	title = db.Column(db.String(100))
	content = db.Column(db.Text())
	created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
	# image_name = db.Column(db.String(3000))
	# image_data = db.Column(db.LargeBinary)

class User(UserMixin,db.Model):

	__tablename__ = 'users'
	
	id = db.Column('id', db.Integer, db.Sequence('user_id_seq',start=1), primary_key=True,)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(80))
	email = db.Column(db.String(80), unique=True)
	created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
	is_admin = db.Column(db.Boolean, unique=False, default=False)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route("/")
def index():
   new_c_data = [(each.id,each.title,each.content) for each in Blog.query.all()]
   new_c_data.sort(key=operator.itemgetter(0),reverse=False)
   return render_template("blog.html",blog_data = new_c_data)

@app.route("/manage_blog")
@login_required
def manage_blog():
	data = User.query.all()
	new_c_data = [(each.id,each.title,each.content,each.created_date) for each in Blog.query.all()]
   	new_c_data.sort(key=operator.itemgetter(0),reverse=False) 
	# return render_template("manage_blog.html", name=current_user.username,form=form, datas=data)
	return render_template("manage_blog.html", name=current_user.username,user_obj = current_user, users=data,blog_data = new_c_data)

@app.route("/add",methods=['GET', 'POST'])
def add_easy_blog():
	if request.method=='POST':
		post =Blog(title=request.form['title'],content=request.form['content'])
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('blog_history'))
	return render_template("manage_blog.html")

@app.route("/blog_history",methods=['GET', 'POST'])
def blog_history():
	new_c_data = [(each.id,each.title,each.content,each.created_date) for each in Blog.query.all()]
   	new_c_data.sort(key=operator.itemgetter(0),reverse=False)
	return render_template("manage_blog.html", name=current_user.username,user_obj = current_user,users=User.query.all(),blog_data = new_c_data)

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

	return render_template("add_blog.html")

@app.route("/about_us", methods=["GET","POST"])
def about_us():

	return render_template("about.html")

@app.route("/contact", methods=["GET","POST"])
def contact_us():

	return render_template("contact.html")

@app.route('/edit_blog/<int:blog_id>',methods=['GET', 'POST'])
def edit_blog(blog_id=False):
	search_result = Blog.query.filter_by(id=int(blog_id)).first()
	if search_result:
		# exist_data.update({'title':search_result.title,'content':search_result.content})
		if request.method == 'POST':
			if not request.form['title'] and not request.form['content']:
				flash('Please enter all the fields', 'error')
			else:
				Flag = False
				# if request.form['title']!= search_result.title:
				# 	search_result.title = request.form['title']
				# 	db.session.add(search_result)
				# 	db.session.commit()
				# 	Flag=True
				if request.form['content']=='':
					flash('Please Enter some description!')	
				elif request.form['content']!= search_result.content:
					search_result.content = request.form['content']
					db.session.add(search_result)
					db.session.commit()
					Flag=True
				else:
					Flag=False

				if Flag:
					flash('Blog Edit sucessfully!')
					return redirect(url_for('blog_history'))
	return render_template('edit_blog.html',name=current_user.username, search_result=search_result)
    # return "Edit Blog "+str(blog_id)

@app.route('/delete_blog/<int:blog_id>',methods=['GET', 'POST'])
def delete_blog(blog_id=False):
	search_result = Blog.query.filter_by(id=int(blog_id)).first()
	if search_result:
	    message = ""
	    message+=str(search_result.title)
	    db.session.delete(search_result)
	    db.session.commit()
	    flash(message+" "+"Deleted Sucessfully.")
	    return redirect(url_for('blog_history'))
	return render_template('edit_blog.html',name=current_user.username, search_result=search_result)

@app.route('/edit_users/<int:user_id>',methods=['GET', 'POST'])
def edit_users(user_id=False):
	form = EditUserForm()
	search_result = User.query.filter_by(id=int(user_id)).first()
	print "search_result====",request.method,search_result.is_admin,form.validate_on_submit()
	if form.validate_on_submit() and request.method=='POST':
		if not request.form['username'] and not request.form['email']:
			flash('Please enter all the fields', 'error')
		else:
			Flag = False
			email = ''
			username = ''
			print "request",request.form.keys()
			all_dict = request.form.keys()
			print "request.form['username']==request.form['email']",type(request.form['username']),request.form['email']
			
			if 'is_admin' in all_dict and request.form['is_admin']==True:
				#admin users
				admin_users = User.query.filter_by(is_admin=True).all()
				print "admin_users=====",admin_users
				if len(admin_users):
					flash('You can not make duplicate Admin!')
					Flag=False
				else:
					search_result.is_admin = True
					db.session.add(search_result)
					db.session.commit()
					Flag=True
			if 'username' in all_dict:
				username = str(request.form['username'])
			if 'email' in all_dict:
				email = str(request.form['email'])
			print "username==email==",username,email
			
			# if username and email:
			search_result.username = username
			search_result.email = email
			db.session.add(search_result)
			db.session.commit()
			Flag=True
			
			print "Flag=====",Flag
			if Flag:
				flash('User Edit sucessfully!')
				return redirect(url_for('blog_history'))
	return render_template('edit_users.html',form= form,name=current_user.username, search_result=search_result)

@app.route('/delete_users/<int:user_id>',methods=['GET', 'POST'])
def delete_users(user_id=False):
	search_result = User.query.filter_by(id=int(user_id)).first()
	if search_result:
	    message = ""
	    message+=str(search_result.username)
	    db.session.delete(search_result)
	    db.session.commit()
	    flash(message+" "+"Deleted Sucessfully.")
	    return redirect(url_for('blog_history'))
	return "Delete User"

if __name__ == '__main__':
	db.create_all()
  	app.run(host='0.0.0.0',port=5002,debug=True)
