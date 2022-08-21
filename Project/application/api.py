from flask_restful import Resource, Api
from flask_restful import fields, marshal_with
from flask_restful import reqparse
from application.validation import BusinessValidationError, NotFoundError
from application.models import *
from application.database import db
from flask import current_app as app
import werkzeug
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np

usr ={
    "u_id": fields.Integer,
    "fname": fields.String,
    "lname": fields.String,
    "mail": fields.String,
    "dob": fields.String,
}



create_usr = reqparse.RequestParser()
create_usr.add_argument('fname', type=str, required=True, help='No first name was given!')
create_usr.add_argument('lname', type=str, required=False, help='No last name was given!')
create_usr.add_argument('mail', type=str, required=True, help='No email was given!')
create_usr.add_argument('dob', type=str, required=True, help='No date of birth was given!')
create_usr.add_argument("username", type=str, required=True, help="No username was given!")
create_usr.add_argument("password", type=str, required=True, help="No password was given!")


class UserAPI(Resource):

    @marshal_with(usr)
    def get(self,u_id):
        user = User.query.filter_by(u_id=u_id).first()
        if user is None:
            raise NotFoundError("User not found",404)
        return user 
    
    def post(self):
        args = create_usr.parse_args()
        fname= args.get('fname',None)
        lname= args.get('lname',None)
        mail= args.get('mail',None)
        dob= args.get('dob',None)
        username= args.get('username',None)
        password= args.get('password',None)

        if fname is None or fname.isnumeric():
            msg = "No first name was given! or first name is not valid"
            code=400
            error="USR001"
            raise BusinessValidationError(code,error,msg)

        if lname is not None and  lname.isnumeric():
            msg = "last name is not valid"
            code=400
            error="USR002"
            raise BusinessValidationError(code,error,msg)    

        if mail is None:
            msg = "No email was given!"
            code=400
            error="USR003"
            raise BusinessValidationError(code,error,msg)


        if dob is None:
            msg = "No date of birth was given!"
            code=400
            error="USR004"
            raise BusinessValidationError(code,error,msg)

        
        user = User.query.filter_by(mail=mail).first()
        if user is None:

            log = Login.query.filter_by(username=username).first()
                
            if log is None:    
                try:
                    user = User(fname=fname,lname=lname,mail=mail,dob=dob)
                    db.session.add(user)
                    db.session.commit()
                    pwd = generate_password_hash(password)
                    new_log = Login(u_id=user.u_id,username=username,password_hash=pwd)
                    db.session.add(new_log)
                    db.session.commit()
                    return {"message":"User created successfully"},201  
            
                except:
                    db.session.rollback()
                    return {"message":"User not created"},400
            else:
                msg = "Username already exists!"
                code=400
                error="USR005"
                raise BusinessValidationError(code,error,msg)
        else:
            msg = "User already exists with same mail id"
            code=400
            error="USR006"
            raise BusinessValidationError(code,error,msg)


log_user = reqparse.RequestParser()
log_user.add_argument('username', type=str, required=True, help='No username was given!')
log_user.add_argument('password', type=str, required=True, help='No password was given!')
class LoginApi(Resource):
    
    def post(self):
        args = log_user.parse_args()
        username= args.get('username',None)
        passwd= args.get('password',None)
        if username is None or passwd is None:
            msg = "No username or password was given!"
            code=400
            error="LR001"
            raise BusinessValidationError(code,error,msg)
        else:
            log = Login.query.filter_by(username=username).first()
            if log is None:
                msg = "Username does not exists!"
                code=400
                error="LR002"
                raise BusinessValidationError(code,error,msg)
            else:
                try:
                    if check_password_hash(log.password_hash,passwd):
                        return {"message":"Login Successful"},200
                    else:
                        msg = "Invalid password!"
                        code=400
                        error="LR003"
                        raise BusinessValidationError(code,error,msg)
                except:
                    msg = "Someting Went Wrong!"
                    code=500
                    error="LR004"
                    raise BusinessValidationError(code,error,msg)

lst={
    "l_id": fields.Integer,
    "u_id": fields.Integer,
    "name": fields.String,
    "description": fields.String
}

create_list = reqparse.RequestParser()
create_list.add_argument('name', type=str, required=True, help='No name was given!')
create_list.add_argument('description', type=str, required=False, help='No description was given!')
create_list.add_argument("u_id", type=int, required=True, help="No user id was given!")

update_lst = reqparse.RequestParser()
update_lst.add_argument('name', type=str, required=False, help='No name was given!')
update_lst.add_argument('description', type=str, required=False, help='No description was given!')

class ListApi(Resource):
    
    @marshal_with(lst)
    def get(self,u_id):
        ulist = List.query.filter_by(u_id=u_id).all()
        if ulist is None or ulist==[]:
            raise NotFoundError("List not found",404)
        return ulist,200
        

    def post(self):
        args = create_list.parse_args()
        name= args.get('name',None)
        description= args.get('description',None)
        u_id= args.get('u_id',None)

        if name is None:
            msg = "No name was given!"
            code=400
            error="LT001"
            raise BusinessValidationError(code,error,msg)
        

        if List.query.filter_by(u_id=u_id).count() <=4: 
            try:
                new_list = List(name=name,description=description,u_id=u_id)
                db.session.add(new_list)
                db.session.commit()
                return {"message":"List created successfully"},200
            except:
                db.session.rollback()
                return {"message":"List not created"},400
        else:
            msg = "You can create only 4 lists!"
            code=400
            error="LT002"
            raise BusinessValidationError(code,error,msg)
    
    
    
    def delete(self,l_id):
        if List.query.filter_by(l_id=l_id).count() == 1:
            try:
                x = db.session.query(Card).filter(Card.l_id==l_id).delete()
                lists = List.query.filter_by(l_id= l_id).first()
                db.session.delete(lists)
                db.session.commit()
                return {"message":"List deleted successfully"},200
            except:
                db.session.rollback()
                return {"message":"List not deleted"},400    
        else:
            msg = "List not found!"
            code=400
            error="LT003"
            raise BusinessValidationError(code,error,msg)
        
    
    def put(self,l_id):
        args= update_lst.parse_args()
        name= args.get('name',None)
        description= args.get('description',None)
        if name is None:
            msg = "No name was given!"
            code=400
            error="LT001"
            raise BusinessValidationError(code,error,msg)

        if List.query.filter_by(l_id=l_id).count() == 1:
            try:
                lists = List.query.filter_by(l_id=l_id).first()
                lists.name=name
                lists.description=description
                db.session.commit()
                return {"message":"List updated successfully"},200
            except:
                db.session.rollback()
                return {"message":"List not updated"},400
        else:
            msg = "List not found!"
            code=400
            error="LT003"
            raise BusinessValidationError(code,error,msg)


get_card = reqparse.RequestParser()
get_card.add_argument("u_id", type=int, required=True, help="No user id was given!")

create_card = reqparse.RequestParser()
create_card.add_argument('name', type=str, required=True, help='No name was given!')
create_card.add_argument('description', type=str, required=False, help='No description was given!')
create_card.add_argument("deadline", type=str, required=True, help="No deadline was given!")

update_card = reqparse.RequestParser()
update_card.add_argument('name', type=str, required=True, help='No name was given!')
update_card.add_argument('description', type=str, required=False, help='No description was given!')
update_card.add_argument("deadline", type=str, required=False, help="No deadline was given!")
update_card.add_argument("l_id", type=int, required=True, help="No list id was given!")

cards={
    "c_id": fields.Integer,
    "l_id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "deadline":fields.String,
    "completed":fields.Integer,
    "date_of_submission":fields.String
}
class CardApi(Resource):

    @marshal_with(cards)
    def get(self,c_id):
        if Card.query.filter_by(c_id=c_id).count() == 1:
            try:
                card = Card.query.filter_by(c_id=c_id).first()
                return card,200
            except:
                msg = "Something went wrong!"
                code=500
                error="CD001"
                raise BusinessValidationError(code,error,msg)
        else:
            msg ="Card not found!"
            code=400
            error="CD002"
            raise BusinessValidationError(code,error,msg)
    

    def post(self,l_id):
        args = create_card.parse_args()
        name= args.get('name',None)
        description= args.get('description',None)
        deadline= args.get('deadline',None)
        completed=0
        date_of_submission=None
        if name is None:
            msg = "No name was given!"
            code=400
            error="CD003"
            raise BusinessValidationError(code,error,msg)
        try:
            new_card = Card(name=name,description=description,deadline=deadline,completed=completed,date_of_submission=date_of_submission,l_id=l_id,created_at=date.today().strftime("%Y-%m-%d"))
            db.session.add(new_card)
            db.session.commit()
            return {"message":"Card created successfully"},200
        except:
            db.session.rollback()
            return {"message":"Card not created"},400     
    
    
    def delete(self,c_id):
        card = Card.query.filter_by(c_id=c_id).first()
        if card is not None:
            try:
                db.session.delete(card)
                db.session.commit()
                return {"message":"Card deleted successfully"},200
            except:
                db.session.rollback()
                return {"message":"Card not deleted"},400
        else:
            msg = "Card not found!"
            code=400
            error="CD002"
            raise BusinessValidationError(code,error,msg)
    
        
    
    def put(self,c_id):
        args= update_card.parse_args()
        name= args.get('name',None)
        description= args.get('description',None)
        deadline= args.get('deadline',None)
        l_id= args.get('l_id',None)

        if Card.query.filter_by(c_id=c_id).count() == 1:
            try:
                card = Card.query.filter_by(c_id=c_id).first()
                card.name=name
                card.description=description
                card.deadline=deadline
                card.updated_at=date.today().strftime("%Y-%m-%d")
                card.l_id=l_id
                db.session.commit()
                return {"message":"Card updated successfully"},200
            except:
                db.session.rollback()
                return {"message":"Card not updated"},400
        else:
            msg = "Card not found!"
            code=400
            error="CD002"
            raise BusinessValidationError(code,error,msg)
    
class CardApiC(Resource):
    
    @marshal_with(cards)
    def get(self, u_id):
        if User.query.filter_by(u_id=u_id).count() == 1:
            if List.query.filter_by(u_id=u_id).count() >0:
                try:
                    ucard = Card.query.join(List, Card.l_id==List.l_id)\
                    .add_columns(Card.c_id, Card.l_id, Card.name, Card.description, Card.deadline, Card.completed,Card.date_of_submission)\
                    .filter(Card.l_id==List.l_id)\
                    .filter(List.u_id==u_id).all()
                    return ucard,200 
                except:
                    msg = "Something went wrong!"
                    code=500
                    error="CD001"
                    raise BusinessValidationError(code,error,msg)

  
            else:
                msg ="No list for the user  found!"
                code=400
                error="LT003"
                raise BusinessValidationError(code,error,msg)

        else:
            msg ="User not found!"
            code=400
            error="U003"
            raise BusinessValidationError(code,error,msg)

    def put(self,c_id):
        card = Card.query.filter_by(c_id=c_id).first()
        if card is not None:
            try:
                card.date_of_submission = date.today().strftime("%Y-%m-%d")
                if card.date_of_submission > card.deadline:
                    card.completed = 3
                    msg = "Card is late completed!"
        
                else:
                    card.completed = 1
                    msg = "Card completed successfully"

                db.session.commit()
                return {"message":msg},200
            except:
                db.session.rollback()
                return {"message":"Card not completed"},400

# sdata  ={
#     "tc": fields.Integer,
#     "cc":fields.Integer,
#     "pc":fields.Integer,
#     "oc":fields.Integer,
#     "dc":fields.Integer,
#     "ac":fields.Integer,
#     "ap":fields.Integer
# }


class SummaryApi(Resource):
 
    def get(self,u_id):

        user = User.query.filter_by(u_id=u_id).first()
        if user:
            ulist = List.query.filter_by(u_id=u_id).all()
            data={}
            for l in ulist:
                tc= Card.query.filter_by(l_id=l.l_id).count()
                if tc > 0:    
                    cc= Card.query.filter_by(l_id=l.l_id).filter_by(completed=1).count()#complete card on time
                    pc= Card.query.filter_by(l_id=l.l_id).filter_by(completed=0).count()#pending  card on time
                    dc= Card.query.filter_by(l_id=l.l_id).filter_by(completed=2).count()#not completed but deadline passed
                    oc= Card.query.filter_by(l_id=l.l_id).filter_by(completed=3).count()#late submission
                    fig = plt.figure(figsize=(6,5))
                    plt.bar("Total Cards",tc,color='b',width=0.4)
                    plt.bar("Completed",cc,color='g',width=0.4)
                    plt.bar("Late Submit",oc,color='r',width=0.4)
                    plt.bar("Pending",pc,color='y',width=0.4)
                    plt.bar("Overdue",dc,color='brown',width=0.4)
                    g = ["Total","Completed","Late","Pending","Over"]
                    plt.legend(g)
                    plt.savefig('./static/img/'+str(l.l_id)+'.png')
                    plt.close()
                    ac = cc+oc #total compelted cards
                    ap = pc+dc #total pending cards
                    data[l.l_id]={"tc":tc,"cc":cc,"pc":pc,"oc":oc,"dc":dc,"ac":ac,"ap":ap}
                    
                else:
                    data[l.l_id]={"tc":0,"cc":0,"pc":0,"oc":0,"dc":0,"ac":0,"ap":0}       
            return data,200
        else:
            msg ="User not found!"
            code=400
            error="U003"
            raise BusinessValidationError(code,error,msg)