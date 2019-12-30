#from flask import render_template
from app import app, db
from app.models import User,Service

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User,'service':Service}


if __name__ == '__main__':
    app.debug=True
    app.run(host='127.0.0.1', port=5000)
    