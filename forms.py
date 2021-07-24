from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email

class addUser(FlaskForm):
    """form for registering new user"""

    username = StringField("Username", validators=[InputRequired(message="Please enter a valid username")])
    password = PasswordField("Password", validators=[InputRequired(message="Please enter a password")])
    email = StringField("Email", validators=[Email(message="Please enter a valid email"), InputRequired(message="Please enter your email")])
    first_name = StringField("First name", validators=[InputRequired(message="Please enter your first name")])
    last_name = StringField("Last name", validators=[InputRequired(message="Please enter your last name")])

class loginUser(FlaskForm):
    """form for logging in user"""

    username = StringField("Username", validators=[InputRequired(message="Please enter your username")])
    password = PasswordField("Password", validators=[InputRequired(message="Please enter your password")])

class addFeedback(FlaskForm):
    """form for new feedback"""

    title = StringField("Title", validators=[InputRequired(message="Please enter a title")])
    content = TextAreaField("Content", validators=[InputRequired(message="Please enter content")])