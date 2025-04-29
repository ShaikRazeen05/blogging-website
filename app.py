from datetime import datetime
from config import Config
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    posts = Blog.query.all()  # Get all blog posts
    return render_template('home.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Make sure both email and password are provided before checking them
        if not email or not password:
            flash('Please enter both email and password', 'warning')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()
        
        # Check if the user exists and if the password matches
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('profile'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    blogs = Blog.query.filter_by(author=current_user.username).all()  # Get user's blogs
    return render_template('profile.html', user=current_user, blogs=blogs)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_blog():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_blog = Blog(title=title, content=content, author=current_user.username)
        db.session.add(new_blog)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create_blog.html')

@app.route('/blog/<int:id>')
def blog(id):
    post = Blog.query.get_or_404(id)
    return render_template('blog.html', post=post)

@app.route('/delete_blog/<int:blog_id>', methods=['POST'])
@login_required
def delete_blog(blog_id):
    # Find the blog post to delete
    blog = Blog.query.get_or_404(blog_id)
    
    # Check if the blog belongs to the current user
    if blog.author == current_user.username:
        db.session.delete(blog)
        db.session.commit()
        flash('Blog deleted successfully!', 'success')
    else:
        flash('You cannot delete this blog.', 'danger')
    
    return redirect(url_for('profile'))

if __name__ == '__main__':
    app.run(debug=True)
