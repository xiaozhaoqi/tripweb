from app import create_app, db
from app.models import User, Role, Permission
from flask_script import Manager, Shell, Server

app = create_app()
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("runserver", Server(host = '0.0.0.0'))

if __name__ == '__main__':
    manager.run()
