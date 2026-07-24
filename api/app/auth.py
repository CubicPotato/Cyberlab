from .extension import auth
from .errors import unauthorized
from .models import User
from flask import g



@auth.verify_password
def verify_password(email_or_token, password):
    '''
    email_or_token est le login
    password est le mot de passe 
    
    cette fonction vérifie la conformité des deux
    '''
    if email_or_token == '':
        return False
    user = User.query.filter_by(email = email_or_token).first()
    if not user:
        return False
    g.current_user = user
    return user.verify_password(password)

@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

