import os
import sqlalchemy
import flask_login
from yaml import load, Loader
from flask import Flask

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass

def init_connect_engine():
    if os.environ.get('GAE_ENV') != 'standard':
        variables = load(open("app.yaml"), Loader=Loader)
        env_variables = variables['env_variables']
        for var in env_variables:
            os.environ[var] = env_variables[var]

        pool = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL(
                drivername="mysql+pymysql",
                username=os.environ.get('MYSQL_USER'),
                password=os.environ.get('MYSQL_PASSWORD'),
                database=os.environ.get('MYSQL_DB'),
                host=os.environ.get('MYSQL_HOST')
            )
        )
        return pool
    
    else:
        db_user = os.environ["MYSQL_USER"]
        db_pass = os.environ["MYSQL_PASSWORD"]
        db_name = os.environ["MYSQL_DB"]
        db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
        cloud_sql_connection_name = os.environ["MYSQL_CONN_NAME"]

        pool = sqlalchemy.create_engine(
            # Equivalent URL:
            # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=<socket_path>/<cloud_sql_instance_name>
            sqlalchemy.engine.url.URL(
                drivername="mysql+pymysql",
                username=db_user,  # e.g. "my-database-user"
                password=db_pass,  # e.g. "my-database-password"
                database=db_name,  # e.g. "my-database-name"
                query={
                    "unix_socket": "{}/{}".format(
                        db_socket_dir,  # e.g. "/cloudsql"
                        cloud_sql_connection_name)  # i.e "<PROJECT-NAME>:<INSTANCE-REGION>:<INSTANCE-NAME>"
                }
            )
        ) 
        return pool

db = init_connect_engine()

from app import routes