from datetime import date
from imp import C_EXTENSION
from turtle import color
from flask import Flask, flash, redirect, request, url_for, session
from flask import render_template
from flask import current_app as app
from .database import db
from application.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import matplotlib.pyplot as plt
import numpy as np

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'
login_manager.needs_refresh_message = (u"Session timedout, please re-login")

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
        session.permanent=True
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

    for c in Card.query.all():
        if   (c.completed!=1 or c.completed!=3) and (date.today().strftime("%Y-%m-%d") > c.deadline):
            c.completed = 2
    db.session.commit()
    
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


@app.route("/delete_list/<int:l_id>",methods=["GET"])
@login_required
def delete_list(l_id):
    x = db.session.query(Card).filter(Card.l_id==l_id).delete()
    lists = List.query.filter_by(l_id= l_id).first()
    db.session.delete(lists)
    db.session.commit()
    flash("list deleted Successfuly")
    return redirect('/dashboard')

@app.route("/edit_list/<int:lid>", methods=["GET", "POST"])
@login_required
def edit_list(lid):
    if request.method=="GET":
        user = User.query.filter_by(u_id=current_user.u_id).first()
        ulist = List.query.filter_by(l_id=lid).first() 
        return render_template("edit_list.html",user=user,ulist=ulist)
    else:
        list_name = request.form["name"]
        print(list_name)       
        list_desc = request.form["desc"]
        print(list_desc)
        lists = List.query.filter_by(l_id=lid).first()
        lists.name = list_name
        lists.description = list_desc
        db.session.commit()
        flash("List Updated")
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


@app.route("/edit_card/<int:id>", methods=["GET", "POST"])
@login_required
def edit_card(id):
    if request.method =="GET":
        ucard= Card.query.filter_by(c_id=id).first()
        user= User.query.filter_by(u_id=current_user.u_id).first()
        ulist = List.query.filter_by(u_id=current_user.u_id).all()
        return render_template("edit_card.html",user=user,ulist=ulist,ucard=ucard)
    else:
        card= Card.query.filter_by(c_id=id).first()
        card.l_id=request.form["lid"]
        card.name=request.form["name"]
        card.description=request.form["description"]
        card.deadline=request.form["deadline"]
        db.session.commit()
        flash("Card Updated Successfuly")
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
    card.date_of_submission = date.today().strftime("%Y-%m-%d")
    if card.date_of_submission > card.deadline:
        flash("Card was overdue")
        card.completed = 3
    else:
        card.completed = 1
    
    db.session.commit()
    flash("Card Completed Successfuly")
    return redirect('/dashboard')


@app.route("/summary" , methods=["GET"])
@login_required
def summary():
    user = User.query.filter_by(u_id=current_user.u_id).first()
    user_list = List.query.filter_by(u_id=user.u_id).all()
    tc,cc,pc,oc,data=0,0,0,0,{}
    for ulist in user_list:
        tc= Card.query.filter_by(l_id=ulist.l_id).count()
        cc= Card.query.filter_by(l_id=ulist.l_id).filter_by(completed=1).count()
        pc= Card.query.filter_by(l_id=ulist.l_id).filter_by(completed=0).count()
        dc= Card.query.filter_by(l_id=ulist.l_id).filter_by(completed=2).count()
        oc= Card.query.filter_by(l_id=ulist.l_id).filter_by(completed=3).count()
        fig = plt.figure(figsize=(5,4))
        plt.bar("Total Cards",tc,color='b',width=0.4)
        plt.bar("Completed",cc,color='g',width=0.4)
        plt.bar("Pending",pc,color='y',width=0.4)
        plt.bar("Late Submit",oc,color='r',width=0.4)
        plt.bar("Overdue",dc,color='brown',width=0.4)
        g = ["Total","Completed","Pending","Late","Over"]
        plt.legend(g)
        plt.savefig('./static/img/'+str(ulist.l_id)+'.png')
        plt.close()
        print( data)
    return render_template("summary.html",user=user,ulist=user_list,ldata=data)


@app.route("/logout", methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    flash("You have been loged out")
    return redirect('/')