from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()



class User(db.Model):
    """" User Model """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)

    @classmethod
    def register(cls, first_name, last_name, email, username, password):
        """ Registger User (Signup): Returns new user class 
            Hash user provided password and then create new user class
        """
        hashed_pw = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_pw_utf = hashed_pw.decode("utf8")

        new_user = cls(
            first_name = first_name,
            last_name = last_name,
            email = email,
            username = username,
            password = hashed_pw_utf
        )
        return new_user

    @classmethod
    def authenticate(cls, username, password):
        """ Authenticate User (Login): User.authenticate('ursname', 'pwd') 
            Checks for user and if user password matches hashed password returns user
            Otherwise returns false
        """
        
        user = cls.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


class Feedback(db.Model):
    """ Feedback Model Class """

    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String, db.ForeignKey('users.username', ondelete="CASCADE"))

    user = db.relationship('User', backref="feedbacks")



def connect_db(app):
    db.app = app
    db.init_app(app)


