from crypt import methods

from flask_migrate import current
from app import app, db
from app.models import User
from flask import render_template, request, redirect, flash, url_for
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime
# from werkzeug.urls import url_parse

from app.forms import EditProfileForm, LoginForm, RegForm
from app.models import Article

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route("/")
@app.route("/index")
@login_required
def index():
    posts = current_user.followed_posts()
    return render_template("index.html", posts=posts)


@app.route("/sign_up", methods=["POST", "GET"])
def sign_up():
    if current_user.is_authenticated: # type: ignore
        return redirect(url_for('index'))
    
    form = RegForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data) # type: ignore
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated: # type: ignore
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page:
            next_page = url_for('index')
        return redirect(next_page)    
    
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/posts")
@login_required
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("posts.html", articles=articles)


@app.route("/profile/<username>")
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Article.query.filter_by(user_id=user.id).order_by(Article.date.desc()).all()
    return render_template("profile.html", user=user, posts=posts)


@app.route("/edit_profile", methods=["POST", "GET"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('profile', username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    
    return render_template('edit_profile.html', form=form)


@app.route("/create_article", methods=["POST", "GET"])
@login_required
def create_article():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article = Article(title=title, intro=intro, text=text, user_id=current_user.id) # type: ignore
        
        try:
            db.session.add(article)
            db.session.commit()

            return redirect("/posts")
        except:
            return "Ошибка при сохранении статьи"    
    else:
        return render_template("create_article.html")
    

@app.route('/posts/<id>')
def get_article(id):
    article = Article.query.get(id)

    return render_template('article.html', article=article)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is not None and user != current_user:
        current_user.follow(user)
        db.session.commit()
        return redirect(url_for('profile', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is not None and user != current_user:
        current_user.unfollow(user)
        db.session.commit()
        return redirect(url_for('profile', username=username))