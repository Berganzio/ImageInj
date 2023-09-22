import os
from io import BytesIO
from tempfile import mkdtemp
from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired
from PIL import Image
from stegano import lsb

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# this is to prevent caching of pages so that when you logout you can't go back to the previous page
@app.after_request 
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SECRET_KEY"] = os.urandom(16) # this is to generate a random secret key for the session
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQLAlchemy(app)
login_manager = LoginManager(app)


# Define your User model, RegistrationForm, LoginForm, and ImageForm here
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


db_file = "site.db"

# Create the database only if it doesn't exist
if not os.path.exists(db_file):
    with app.app_context():
        db.create_all()


class RegistrationForm(FlaskForm):
    # Define registration form fields and validators here
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired()]
    )
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    # Define login form fields and validators here
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class InjectImageForm(FlaskForm):
    # Define image form fields and validators here
    image = FileField("Image", validators=[DataRequired()])
    text = StringField("Text", validators=[DataRequired()])
    submit = SubmitField("Inject")
    
class ExtractImageForm(FlaskForm):
    # Define image form fields and validators here
    image = FileField("Image", validators=[DataRequired()])
    submit = SubmitField("Extract")
    

@app.route("/")
def home():
    return render_template("layout.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Passwords do not match')
            return redirect(url_for("register"))
        # if username already exists flash message
        user_check = User.query.filter_by(username=form.username.data).first()
        if user_check:
            flash('Username already exists')
            return redirect(url_for("register"))
        else:
            hashed_password = generate_password_hash(form.password.data)
            user = User(username=form.username.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
    return render_template("register.html", form=form)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password")
            return redirect(url_for("login"))
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    form = LoginForm()
    logout_user()
    return render_template("login.html", form=form)

@app.route("/inject", methods=["GET", "POST"])
@login_required
def inject():
    form = InjectImageForm()
    if form.validate_on_submit():
        image = form.image.data
        text = form.text.data
        filename = image.filename

        # Read the image file into memory
        image_bytes = BytesIO(image.read())
        img = Image.open(image_bytes)

        # Inject the text into the image
        secret = lsb.hide(img, text)

        # Save the modified image
        secret.save(filename)

        return redirect(url_for("home"))
    return render_template("inject.html", form=form)

@app.route("/extract", methods=["GET", "POST"])
@login_required
def extract():
    form = ExtractImageForm()
    if form.validate_on_submit():
        image = form.image.data

        # Read the image file into memory
        image_bytes = BytesIO(image.read())
        img = Image.open(image_bytes)

        # Extract the hidden text from the image
        try:
            secret = lsb.reveal(img)
        except IndexError:
            flash("No text found in image")
        else:
            return render_template("extract.html", secret=secret, form=form)
    return render_template("extract.html", form=form)



if __name__ == "__main__":
    app.run(debug=True)
