from .extension import auth
from .models import User
from flask import g

@auth.verify_password
def verify_password(login, password):
    '''
    email_or_token est le login
    password est le mot de passe 
    
    cette fonction vérifie la conformité des deux
    '''
    if not login:
        return False
    user = User.query.filter_by(login=login).first()
    if not user:
        return False
    g.current_user = user
    return user.bdcheck(password)

