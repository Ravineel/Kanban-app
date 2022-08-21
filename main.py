import os
from flask import Flask
from flask_restful import Resource, Api
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db

app = None
api = None


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    if os.getenv('ENV', "development") == "production":
      raise Exception("Currently no production config is setup.")
    else:
      print("Staring Local Development")
      app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api = Api(app)
    app.app_context().push()  
    return app, api

app, api = create_app()

# @app.route("/docs")
# def documentation():
#   return render_template("Swagger.yml")

# Import all the controllers so they are loaded
from application.controllers import *

# Add all restful controllers
from application.api import *

api.add_resource(UserAPI, '/api/user/<int:u_id>','/api/user/create')
api.add_resource(LoginApi, '/api/login')
api.add_resource(ListApi, '/api/list/<int:u_id>','/api/list/create','/api/list/delete/<int:l_id>','/api/list/edit/<int:l_id>')
api.add_resource(CardApi,  '/api/card/<int:c_id>','/api/card/create/<int:l_id>','/api/card/edit/<int:c_id>','/api/card/delete/<int:c_id>')
api.add_resource(CardApiC,'/api/card/all/<int:u_id>','/api/card/complete/<int:c_id>')
api.add_resource(SummaryApi, '/api/summary/<int:u_id>')


if __name__ == '__main__':
  # Run the Flask app
  app.run(host='0.0.0.0',port=5000)
