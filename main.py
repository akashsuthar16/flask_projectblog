from email import message
from flask import Flask,render_template, request, session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json
import math

with open('config.json' , 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail_user'],
    MAIL_PASSWORD = params['gmail_password']
)
mail = Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']                        #'mysql://root:@localhost/coding_blog'   #'sqlite:///contact.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['product_uri']

db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone_num = db.Column(db.String(120), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(120), nullable=True)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(120), nullable=True)
    img_file = db.Column(db.String(20), nullable=True)

# index page
@app.route('/', methods=['GET'])
def index():
    # Pageenecen blog
    pooos = Posts.query.filter_by().all() 
    last = math.ceil(len(pooos)/int(params['no_of_blog']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    pooos = pooos[(page-1)*int(params['no_of_blog']):(page-1)*int(params['no_of_blog'])+ int(params['no_of_blog'])]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)

    return render_template("index.html",params=params, pooos=pooos,prev=prev, next=next)

# About page 
@app.route('/aboutpage')
def about():
    return render_template("about.html",params=params)

# Data insert With Email sending message
@app.route('/contactpage' , methods = ['GET','POST'])
def contact():
    if(request.method=='POST'):
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')
        contac = Contacts(name=name,email=email,phone_num=phone,msg=message,date=datetime.now())
        db.session.add(contac)
        db.session.commit()
        # Messsage
        mail.send_message("New message from" + name,
                            sender =email,
                            recipients =[params['gmail_user']],
                            body =message + "\n" + name + (phone))
    return render_template("contact.html",params=params)

@app.route('/postpage/<string:post_slug>' , methods = ['GET'])
def postp(post_slug):
    postroute = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html",params=params, postroute=postroute)



# login page data insert with session 
@app.route('/login', methods=['GET','POST'])
def login():
    if 'uemail' in session['uemail'] ==params['admin_user']:    
        if request.method=="POST":
            email =request.form.get('uemail')
            password = request.form.get('upassword')
            if(email==params['admin_user'] and password==params['admin_password']):
                session['uemail'] = email
                postseen = Posts.query.all()
                return render_template("dashbord.html",params=params,postseen=postseen)
        else:
            return render_template("login.html",params=params)

#dashbord page table create
@app.route('/dashbordpage', methods=['GET','POST'])
def dashbord():
    postseen = Posts.query.all()
    return render_template("dashbord.html",params=params,postseen=postseen)

# Update Data Method
@app.route("/edit/<int:sno>" , methods=['GET', 'POST'])
def edit(sno):
    if "uemail" in session and session['uemail']==params['admin_user']:
        if request.method=="POST":
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            # date = datetime.now()
            post = Posts.query.filter_by(sno=sno).first()
            post.title =box_title
            post.tagline =tline
            post.slug =slug
            post.content =content
            post.img_file =img_file
            db.session.add(post)
            db.session.commit()
            postseen = Posts.query.all()
            return render_template('dashbord.html', params=params,postseen=postseen)        
        else:
            pass
    post = Posts.query.filter_by(sno=sno).first()
    return render_template("edit.html",params=params, post=post)

# New Add Post Data insert  
@app.route('/addnewpage',methods=['GET','POST'])
def addnews():
    if "uemail" in session and session['uemail']==params['admin_user']:
        if request.method=='POST':
            titlel=request.form.get('title')
            taline=request.form.get('tline')
            slugg=request.form.get('slug')
            contentt=request.form.get('content')
            img=request.form.get('img_file')
            aadpost = Posts(title=titlel,tagline=taline,slug=slugg,content=contentt,img_file=img,date=datetime.now())
            db.session.add(aadpost)
            db.session.commit()
    return render_template("addnew.html",params=params)

# Delete data
@app.route("/delete/<int:sno>" , methods=['GET', 'POST'])
def delete(sno):
    if "uemail" in session and session['uemail']==params['admin_user']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashbordpage")

if __name__ == "__main__":
    app.run(debug=True)