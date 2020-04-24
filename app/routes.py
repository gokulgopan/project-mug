from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegisterForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Team, userteams, Roles, userroles
from flask import request
from werkzeug.urls import url_parse

@app.route('/index/<int:page>', methods=['GET', 'POST'], defaults={"page": 1})
@login_required
def index(page):
    user = current_user
    page = request.args.get('page', 1, type=int)
    team = Team.query.join(userteams).join(User).filter((userteams.c.user_id == user.id) & (userteams.c.team_id == Team.id)).first()
    page = page
    per_page = 2
    posts = Post.query.filter(Post.team_id == team.id).order_by(Post.timestamp.desc()).paginate(page,per_page,error_out=False)
    
    return render_template('index.html', title='Updates', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash(f'Hello { form.username.data }')

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, islogin=True)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register' , methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, firstname=form.firstname.data, secondname=form.secondname.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user, isprofile=True)

@app.route('/add-update', methods=['GET', 'POST'])
@login_required
def add_update():
    form = PostForm()
    if form.validate_on_submit():
        user = current_user
        team_id = Team.query.join(userteams).join(User).filter((userteams.c.user_id == user.id) & (userteams.c.team_id == Team.id)).first()
        team = Team.query.get(team_id.id)
        post = Post(title = form.title.data, body=form.body.data, author = user, teams=team)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_post.html', form=form)


@app.route('/admin2')
@login_required
def admin():
    user = current_user
    role = Roles.query.join(userroles).join(User).filter((userroles.c.user_id == user.id) & (userroles.c.role_id == Roles.id)).first()
    admin_role = Roles.query.filter(Roles.name == 'Admin').first()
    if role is not None:
        if role.id is admin_role.id:
            return 'You are admin'
    return redirect(url_for('index'))


@app.route('/admin2/add-user')
@login_required
def admin_add_user():
    form = RegisterForm()
    user = current_user
    role = Roles.query.join(userroles).join(User).filter((userroles.c.user_id == user.id) & (userroles.c.role_id == Roles.id)).first()
    admin_role = Roles.query.filter(Roles.name == 'Admin').first()
    if role is not None:
        if role.id is admin_role.id:
            return render_template('register.html', form=form)
    return redirect(url_for('index'))

