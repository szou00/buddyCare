from flask import Flask, redirect, url_for, render_template, request, session, flash, g
from datetime import timedelta, datetime

from flask.signals import Namespace
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "weAreCoolest"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=7)

db = SQLAlchemy(app)
db1 = SQLAlchemy(app)
class User(db.Model):
    id = db.Column("id", db.Integer, primary_key= True)
    username = db.Column("username", db.String(100))
    password = db.Column("password", db.String(100))
    bud = db.Column("bud", db.Boolean)
    activity = db.Column("activity", db.String(100))
    streak = db.Column("streak", db.Integer, primary_key=True)
    bio = db.Column("bio", db.String(300))
    achieve = db.Column("achieve", db.String(300))
    joke = db.Column("joke", db.String(200))
    # budName = db.Column("buddy",db.String(200))
    

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
        self.activity = None
        self.streak = 0
        self.bud = True #should automatically signal they want a buddy unless they change it
        self.bio = 'Nice to meet you! I love sleep'
        self.achieve = "I want to sleep more"
        self.joke = "Why can’t you be friends with a squirrel?... They drive everyone nuts!"
        # self.budName = None
        
    def __repr__(self):
        return self.username

class newActivity(db1.Model):
     id1 = db1.Column("id1", db1.Integer, primary_key= True)
     activityname= db1.Column("activityname", db1.String(100))

     def __init__(self,activityname):
         self.activityname=activityname
    
     def __repr__(self):
         return self.activityname

db.create_all()
db.session.commit()

db1.create_all()
db1.session.commit()

@app.before_request
def before_request():
    g.user = None
    if 'name' in session and not(session['name'] == None):
        user = User.query.filter_by(username = session['name']).first()
        g.user = user

@app.route("/")
@app.route('/home')
def home():
    if 'name' in session:
        found_user = User.query.filter_by(username = session['name']).first()
        return render_template("index.html", values=User.query.all(),user=found_user)

@app.route('/<name>')
def viewBuddy(name):
    buddy = User.query.filter_by(username=name).first()
    if buddy == None:
        flash("No Buddy!")
        return render_template("index.html")
    return render_template("buddy.html",name=buddy.username,id=buddy.id, activity=buddy.activity,streak=buddy.streak,bud=buddy.bud)
    
@app.route("/profile", methods=["POST", "GET"])
def profile():
    if "name" in session:
        user = User.query.filter_by(username=session['name']).first()

        if user == None:
            flash("Cannot find user")
            return redirect(url_for("home"))

        print("it works at this line")
        if request.method=="POST":
            bio = request.form["bio"]
            achieve = request.form["achieve"]
            joke = request.form["joke"]
            
            print("\n\n\n BIO IS", bio, "\n\n\n")
            print("HELLOOOOOOOOOOOOOOO")
            if not(bio == None):
                user.bio = bio
            if not(achieve == None):
                user.achieve = achieve
            if not(joke == None):
                user.joke = joke
            
            db.session.commit()
        return render_template('profile.html', user=user)
    flash("You must login first!")
    return redirect(url_for("login"))

@app.route("/activity", methods=["POST", "GET"])
def activity():
    if request.method == "POST":
        activity=request.form["activity"]
        find_act=newActivity.query.filter_by(activityname=activity).first()
        if find_act:
            flash("activity already exists")
            session["activityname"] = find_act.activityname
        else:
            actname = newActivity(activity)
            flash("new activity added")
            db1.session.add(actname)
            db1.session.commit()
    if (newActivity.query.first == None):
        return render_template("activity.html")
    return render_template("activity.html",activities=newActivity.query.all())
    

@app.route("/Meditation",methods=["POST", "GET"])
def meditation():
    if request.method == "POST":
        if "name" in session:
            flash("yay!")
            user = User.query.filter_by(username=session['name']).first()
            user.activity = "Meditation"
            db.session.commit()
            return redirect(url_for("profile"))
    return render_template("Meditation.html")

@app.route("/Journal",methods=["POST", "GET"])
def journal():
    if request.method == "POST":
        if "name" in session:
            flash("yay!")
            user = User.query.filter_by(username=session['name']).first()
            user.activity = "Journaling"
            db.session.commit()
            return redirect(url_for("profile"))
    return render_template("Journal.html")

@app.route("/Walk",methods=["POST", "GET"])
def walk():
    if request.method == "POST":
        if "name" in session:
            flash("yay!")
            user = User.query.filter_by(username=session['name']).first()
            user.activity = "Walking"
            db.session.commit()
            return redirect(url_for("profile"))
    return render_template("Walk.html")

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        username = request.form["username"]
        password = request.form["password"]

        #db 
        # user = [x for x in users if x.username == username][0]
        user = User.query.filter_by(username=username).first()
        #print(user)
        #print(user)
        #print(user[0])
        if user and user.password == password:
            session['name'] = user.username
            flash("Login Successful!")
            return redirect(url_for('profile'))
        else:
            flash("Login Unsuccessful :(")
            return redirect(url_for("login"))
    else: 
        if "name" in session:        
            flash("Already Logged In!")
            return redirect(url_for("home"))
        return render_template("login.html")

@app.route("/create", methods=["POST","GET"])
def create():
    
    if request.method == "POST":
        newusername = request.form["newusername"]
        newpassword = request.form["newpassword"]
        found_user = User.query.filter_by(username=newusername).first()
        
        if found_user:
            flash("That username is already taken!")
            return render_template("create.html")
        else:
            
            flash("Congrats! You have created a new account.")
            usr = User(len(User.query.all())+1, newusername, newpassword) 
            session['name'] = newusername
            db.session.add(usr)
            db.session.commit()
            return redirect(url_for("questions"))
    else:
        return render_template("create.html")

@app.route("/Questions", methods=["POST", "GET"])
def questions():
    flash(request.method)
    if request.method == "POST":
        if "name" in session:
            session.permanent = True
            user = User.query.filter_by(username=session['name']).first()
            user.bio=request.form["bio"]
            user.achieve=request.form["achieve"]
            user.joke=request.form["joke"]
            db.session.commit()
            return redirect(url_for("profile"))
    return render_template("Questions.html")


@app.route("/view")
def view():
    return render_template("view.html", values=User.query.all(), values1=newActivity.query.all())

@app.route("/finder")
def finder():
    return render_template("finder.html", values = User.query.all())

@app.route("/<usr>/edit", methods=["POST", "GET"])
def edit(usr):
    if "name" in session:
        user = User.query.filter_by(username=session['name']).first()
        if request.method=="POST":
            flash("Buddy Status Changed!")
            buddy = request.form["buddy"]
            if buddy == "no":
                user.bud = False
            else:
                user.bud = True
            db.session.commit()
            return render_template('profile.html', user=user)
    return render_template("edit.html",user=usr)


@app.route('/addActivity')
def addActivity():
    return render_template("addActivity.html")

@app.route("/activity/<activityName>", methods=["POST", "GET"])
def activityPage(activityName):
    if request.method == "POST":
        if "name" in session:
            flash("yay!")
            user = User.query.filter_by(username=session['name']).first()
            user.activity = activityName
            db.session.commit()
            return redirect(url_for("profile"))
    return render_template("chooseActivity.html", name=activityName) 

@app.route("/logout")
def logout():
    flash("You have been logged out!", "info")
    session.pop("name", None)
    #session.pop("email", None)
    return redirect(url_for("login"))

 
if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True) 