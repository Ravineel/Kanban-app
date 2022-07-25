from datetime import date
from flask import Flask, flash, redirect, request, url_for
from flask import render_template
from flask import current_app as app
from .database import db
from application.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'


@login_manager.user_loader
def load_user(id):
    user  = Login.query.get(int(id))
    return user

@app.route("/", methods=["GET"])
def home():   
    return render_template("home.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("home.html")
    else:
        user = Login.query.filter_by(username=request.form["username"]).first()
        if user:
            if check_password_hash(user.password_hash,request.form["password"]):
                login_user(user)
                flash("Login Successful")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Credentials")
        else:
            flash("No user Exist")
        
        return render_template('home.html')


@app.route("/signup",methods=["GET", "POST"])
def signup():
    if request.method=="GET":
        return render_template("signup.html")
    else:
        
        email=request.form["email"]
        first_name=request.form["fname"]

        if first_name is None or email is None:
            flash("No input was given!")
            return redirect('/signup')
        else:
            user = User.query.filter_by(mail=email).first()
            if user is None:
                uname = Login.query.filter_by(username=request.form["username"]).first()
                if uname is None:
                    try:
                        new_user = User(fname=first_name,lname=request.form["lname"],mail=request.form["email"],dob=request.form["dob"])
                        db.session.add(new_user)
                        db.session.commit()
                        pwd = generate_password_hash(request.form["password"]) 
                        new_login=Login(u_id=new_user.u_id, username=request.form["username"],password_hash=pwd)
                        db.session.add(new_login)
                        db.session.commit()
                        flash("User signed up Successfuly! please log in now")
                        return redirect('/')
                    except:
                        flash("something went wrong")
                        db.session.rollback()
                        return redirect("/signup")
                else:
                    flash("username already exists")
                    return redirect("/signup")
            else:
                flash("Email already exists!")
                return redirect('/signup')       


@app.route("/dashboard",methods=["GET"])
@login_required
def dashboard():
    user = User.query.filter_by(u_id=current_user.u_id).first()
    
    user_list = List.query.filter_by(u_id=user.u_id).all()

    user_card = Card.query.join(List, Card.l_id==List.l_id)\
                .add_columns(Card.c_id, Card.l_id, Card.name, Card.description, Card.deadline, Card.completed,Card.date_of_submission)\
                .filter(Card.l_id==List.l_id)\
                .filter(List.u_id==user.u_id).all()  
    return render_template("kanban.html",user=user,ulist=user_list,ucard=user_card)


@app.route("/create_list", methods=["GET", "POST"])
@login_required
def create_list():
    if request.method =="GET":
        user = User.query.filter_by(u_id=current_user.u_id).first()
        return render_template("create_list.html",user=user)
    else:
        new_list = List(u_id=current_user.u_id, name=request.form["name"],description=request.form["desc"])
        db.session.add(new_list)
        db.session.commit()
        flash("List Added")
        return redirect('/dashboard')

@app.route("/create_card/<int:l_id>", methods=["GET", "POST"])
@login_required
def create_card(l_id):
    if request.method =="GET":
        ulist = List.query.filter_by(l_id=l_id).first()
        user= User.query.filter_by(u_id=current_user.u_id).first()
        return render_template("create_card.html",user=user,ulist=ulist)
    else:
        new_card = Card(l_id=l_id, name=request.form["name"],description=request.form["description"], deadline=request.form["deadline"])
        db.session.add(new_card)
        db.session.commit()
        flash("Card Added")
        return redirect('/dashboard')

@app.route("/delete_list/<int:l_id>",methods=["GET"])
@login_required
def delete_list(l_id):
    x = db.session.query(Card).filter(Card.l_id==l_id).delete()
    lists = List.query.filter_by(l_id= l_id).first()
    db.session.delete(lists)
    db.session.commit()
    flash("list deleted Successfuly")
    return redirect('/dashboard')

@app.route("/delete_card/<int:c_id>",methods=["GET"])
@login_required
def delete_card(c_id):
    card = Card.query.filter_by(c_id= c_id).first()
    db.session.delete(card)
    db.session.commit()
    flash("Card deleted Successfuly")
    return redirect('/dashboard')

@app.route("/complete_card/<int:c_id>",methods=["GET"])
@login_required
def complete_card(c_id):
    card = Card.query.filter_by(c_id= c_id).first()
    card.completed=1
    card.date_of_submission = date.today().strftime("%Y-%m-%d")
    db.session.commit()
    flash("Card Completed Successfuly")
    return redirect('/dashboard')


@app.route("/logout", methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    flash("You have been loged out")
    return redirect('/')