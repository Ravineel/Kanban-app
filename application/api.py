from flask_restful import Resource, Api
from flask_restful import fields, marshal_with
from flask_restful import reqparse
from application.validation import BusinessValidationError, NotFoundError
from application.models import *
from application.database import db
from flask import current_app as app
import werkzeug
from flask import abort
from werkzeug.security import generate_password_hash, check_password_hash


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
    
    
    
    def delete():
        pass
    
    def put():
        pass


class CardApi(Resource):
    def get():
        pass
    
    def post():
        pass

    def delete():
        pass
    
    def put():
        pass

    

                  