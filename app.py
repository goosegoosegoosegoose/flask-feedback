
from flask import Flask, redirect, render_template, session, flash
from werkzeug.utils import validate_arguments
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import addUser, loginUser, addFeedback

app = Flask(__name__)

app.config['SECRET_KEY'] = "whatnow"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

@app.route('/')
def redirect_to_register():
    """redirect"""
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    """Form for registering new user"""
    form = addUser()

    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        email=form.email.data
        first_name=form.first_name.data
        last_name=form.last_name.data
        
        new_user = User.register(username=username, password=password, email=email, first_name=first_name, last_name=last_name)

        db.session.add(new_user)
        db.session.commit()

        session["user"] = new_user.username
        return redirect(f'/users/{username}')
    else:
        return render_template("reg_form.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Login form and post request processing"""
    form = loginUser()

    if "user" in session:
        logged_user = session["user"]
        return redirect(f"users/{logged_user}")

    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data

        user = User.authenticate(username=username, password=password)

        if user:
            session["user"] = user.username

            return redirect(f'/users/{username}')
        else:
            form.password.errors = ['Unable to log in']

    return render_template("login_form.html", form=form)

@app.route('/users/<username>')
def user_page(username):
    """Only logged in users can see this"""

    user = User.query.get_or_404(username)
    feedback = Feedback.query.filter_by(recipient=username).all()
    
    if "user" not in session:
        flash("Not logged in")
        return redirect('/login')
    else:
        return render_template('user_page.html', user=user, feedback=feedback)

@app.route('/logout')
def logout():
    """log out button"""

    session.pop("user")

    return redirect('/login')

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """delete your user"""

    user = User.query.get_or_404(username)

    if username == session["user"]:
        db.session.delete(user)
        db.session.commit()
        session.pop("user")

        flash("Deleted user")
        return redirect('/login')
    else:
        flash("You lack permissions")
        return redirect('/login')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    """Feedback adding form and post request handler"""
    form = addFeedback()

    if "user" not in session:   
        flash("Not logged in")
        return redirect('/login')
    
    elif form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        recipient = username
        user = session["user"]

        new_feedback = Feedback(title=title, content=content, recipient=recipient, user=user)
        db.session.add(new_feedback)
        db.session.commit()

        flash("Added feedback")
        return redirect(f'/users/{username}')
    else:
        return render_template("feedback_form.html", form=form, username=username)

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    """Edit posted feedback"""
    
    feedback = Feedback.query.get_or_404(feedback_id)
    form = addFeedback(obj=feedback)

    if "user" not in session:   
        flash("Not logged in")
        return redirect('/login')
    
    elif form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        flash("Edited feedback")
        return redirect(f'/users/{feedback.recipient}')
    else:
        return render_template("feedback_edit.html", form=form, feedback_id=feedback_id, recipient=feedback.recipient)

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    """User who created feedback can delete feedback"""

    feedback = Feedback.query.get_or_404(feedback_id)
    recipient = feedback.recipient
    
    db.session.delete(feedback)
    db.session.commit()

    return redirect(f'/users/{recipient}')