from flask import Flask, request, flash, redirect, render_template, session
from flask_debugtoolbar import DebugToolbarExtension

from models import User, Feedback, db, connect_db
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///feedback_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "abcdaasdfasfsdfadsfasdfef"

toolbar = DebugToolbarExtension(app)

connect_db(app)

@app.route("/")
def root_route():
    """ Root Route"""

    feedbacks = Feedback.query.all()

    return render_template("root.html", feedbacks=feedbacks)


@app.route("/users")
def users_route():
    """ Users Route """

    users = User.query.all()

    return render_template("users.html", users=users)



@app.route("/register", methods=["GET", "POST"])
def register_user():
    """ Register user"""

    if "username" in session:
        flash(f"{session['username']} is logged in! Please logout to register new user!", "warning")
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()

    if form.validate_on_submit():
        new_user = User.register(
            form.first_name.data,
            form.last_name.data,
            form.email.data,
            form.username.data,
            form.password.data
        )

        db.session.add(new_user)
        db.session.commit()
        session["username"] = new_user.username

        flash(f"New User: {new_user.username} added!", "success")
        return redirect(f"/users/{new_user.username}")
    else:
        return render_template("register_form.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_user():
    """ Login User 
        Add user to session if user successfully authenticates
    """
    if "username" in session:
        flash(f"{session['username']} is already logged in!", "warning")
        return redirect(f"/users/{session['username']}")


    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            session["username"] = user.username
            flash(f"Hello {user.username}! Welcome Back!", "success")
            return redirect(f"/users/{user.username}")
        else:
            flash(f"Invalid username and password combination! Try again!", "danger")
            return redirect("/login")
    else:
        return render_template("login_form.html", form=form)


@app.route("/users/<username>")
def secret_route(username):
    """ Secret Route """

    if "username" not in session:
        flash(f"Unauthorized access! Please login first!", "warning")
        return redirect("/login")
    else:
        user = User.query.filter_by(username = username).one_or_none()
        return render_template("user.html", user=user)


@app.route("/logout", methods=["POST"])
def logout_user():
    """ Logout User 
    """

    session.pop("username")
    flash(f"Logged Out", "success")
    return redirect("/")


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """ Delete User """
    session.pop("username")

    user = User.query.filter_by(username = username).one_or_none()

    db.session.delete(user)
    db.session.commit()


    flash(f"{user.username} deleted!", "success")
    return redirect("/")


@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    """ Add feedback if user is logged in """

    if "username" not in session:
        flash(f"Unauthorized access! Please login first!", "warning")
        return redirect("/login")

    if session["username"] != username:
        flash(f"Unauthorized access! Only logged in users can add feedback to their page!", "warning")
        return redirect("/")

    form = FeedbackForm()

    if form.validate_on_submit():
        new_feedback = Feedback(
            title = form.title.data,
            content = form.content.data,
            username = username
        )

        db.session.add(new_feedback)
        db.session.commit()

        flash(f"Feedback Added!", "success")
        return redirect(f"/")
    else:
        return render_template("add_feedback.html", form=form)

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """ Update Feedbacks """

    if "username" not in session:
        flash(f"Unauthorized access! Please login first!", "warning")
        return redirect("/login")

    feedback = Feedback.query.get(feedback_id)

    if session["username"] != feedback.user.username:
        flash(f"Unauthorized access! Only logged in users can update feedbacks from their page!", "warning")
        return redirect("/")
    
    form = FeedbackForm()


    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        feedback.username = feedback.user.username

        db.session.add(feedback)
        db.session.commit()

        flash(f"Feedback Updated!", "success")
        return redirect(f"/users/{feedback.username}")

    form.title.data = feedback.title
    form.content.data = feedback.content

    return render_template("update_feedback.html", form=form)




@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """" Deletes Selected Feedback """

    if "username" not in session:
        flash(f"Unauthorized access! Please login first!", "warning")
        return redirect("/login")

    feedback = Feedback.query.get(feedback_id)

    if session["username"] != feedback.user.username:
        flash(f"Unauthorized access! Only logged in users can remove feedbacks from their page!", "warning")
        return redirect("/")

    db.session.delete(feedback)
    db.session.commit()

    flash("Feedback Deleted!", "success")
    return redirect(f"/users/{feedback.username}")



def create_db_func():
    with app.app_context():
        db.create_all()