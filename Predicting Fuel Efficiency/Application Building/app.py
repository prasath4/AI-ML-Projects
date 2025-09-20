from flask import Flask ,request,render_template,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user,LoginManager,login_required,logout_user,current_user
from flask_wtf import FlaskForm
from wtforms import StringField , PasswordField , SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import joblib


app=Flask(__name__)
bcrypt=Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///C:/Users/nojma/OneDrive/Desktop/flask 2/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.config['SECRET_KEY']='thisissecretkey'
db=SQLAlchemy(app)
app.app_context().push()


login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),nullable=False,unique=True)
    password = db.Column(db.String(80),nullable=False)


class RegisterForm(FlaskForm):
    username=StringField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Username"})

    password=PasswordField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Password"})

    submit = SubmitField("Register")

    def validate_username(self,username):
        existing_user_usernamae=User.query.filter_by(username=username.data).first()

        if existing_user_usernamae:
            raise ValidationError(
                "That username already exists.please choose a different one."
            )


class LoginForm(FlaskForm):
    username=StringField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Username"})

    password=PasswordField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Password"})

    submit = SubmitField("logIn")

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user)
                return redirect(url_for("index"))
    return render_template("login.html",form=form)


@app.route('/index',methods=['GET','POST'])
@login_required
def index():
    return render_template("index.html")

#HTTP : //localhost: 8090/prediction
@app.route("/prediction",methods=["POST"])
def prediction():
    name1=float(request.form.get("name1"))
    name2=float(request.form.get("name2"))
    name3=float(request.form.get("name3"))
    name4=float(request.form.get("name4"))
    name5=float(request.form.get("name5"))
    name6=float(request.form.get("name6"))
    name7=float(request.form.get("name7"))
    name8=float(request.form.get("name8"))

    X=([[name1,name2,name3,name4,name5,name6,name7,name8]])


    jab="fuel.pkl"
    with open(jab,"rb") as file:
        load_model= joblib.load(file)
    result=load_model.predict(X)[0]
    return render_template("prediction.html",result=result)

@app.route("/logout",methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register',methods=['GET','POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        hashed_password= bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html",form=form)

if __name__=="__main__":
    app.run(debug=True)

