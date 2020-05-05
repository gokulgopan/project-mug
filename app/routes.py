from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegisterForm, PostForm, CreateTeam, UpdateNoteForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Team, userteams, Roles, userroles, UpdateNote
from flask import request
from werkzeug.urls import url_parse
from functools import wraps
from flask import g
from app.forms import SearchForm


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        u = current_user
        user = User.query.filter(User.id == u.id).first()
        role = user.roles.first()
        if role.name == "Admin":
            return f(*args, **kwargs)
        else:
            flash("You need to be an admin to view this page.")
            return redirect(url_for('index'))
    return wrap

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user = current_user
    team = Team.query.join(userteams).join(User).filter((userteams.c.user_id == user.id) & (userteams.c.team_id == Team.id)).first()
    #if team is not None:
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter(Post.team_id == team.id).order_by(Post.timestamp.desc()).paginate(page=page, per_page=8)
        #if posts is not None:
    return render_template('index.html', title='Updates', posts=posts)
    #return "Welcome"


@app.route('/create-team', methods=['GET', 'POST'])
@login_required
def create_team():
    user = current_user
    form = CreateTeam()
    if form.validate_on_submit():
        team = Team(name=form.name.data, body=form.body.data)
        db.session.add(team)
        db.session.commit()
        user.teams.append(team)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('join_team.html', form=form)

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


@app.route('/admin')
@login_required
def admin():
    user = current_user
    role = Roles.query.join(userroles).join(User).filter((userroles.c.user_id == user.id) & (userroles.c.role_id == Roles.id)).first()
    admin_role = Roles.query.filter(Roles.name == 'Admin').first()
    if role is not None:
        if role.id is admin_role.id:
            return 'You are admin'
    return redirect(url_for('index'))


@app.route('/admin2')
@login_required
@admin_required
def admin2():
    return redirect(url_for('index'))


@app.route('/admin/users/add-user', methods=['GET', 'POST'])
@admin_required
@login_required
def admin_add_user():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, firstname=form.firstname.data, secondname=form.secondname.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/admin/teams/add-team', methods=['GET', 'POST'])
@admin_required
@login_required
def admin_add_team():
    return "Add Team"

@app.route('/admin/teams/rm-team', methods=['GET', 'POST'])
@admin_required
@login_required
def admin_remove_team():
    return "Add Team"
    
@app.route('/admin/teams/add-user', methods=['GET', 'POST'])
@admin_required
@login_required
def admin_add_user_team():
    return "Add User to Team"
    
@app.route('/admin/teams/remove-user', methods=['GET', 'POST'])
@admin_required
@login_required
def admin_rm_user_team():
    return "Remove User from Team"

@app.route('/admin/users/remove-user', methods=['GET', 'POST'])
@admin_required
@login_required
def admin_rm_user():
    return "Remove User"

@app.route('/search')
@login_required
def search():
    page = request.args.get('page', 1, type=int)
    searchquery = request.args.get('search', default=None, type=None)
    posts, total = Post.search(searchquery, 1, 5)
    post = posts.paginate(page=page, per_page=3)
    return render_template('search.html', posts=post, searchquery=searchquery)

@app.route('/updates/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_view(post_id):
    form = UpdateNoteForm()
    post = Post.query.get(post_id)
    if form.validate_on_submit():
        user = current_user
        un = UpdateNote(note=form.note.data, post_id=post.id)
        db.session.add(un)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)       
    notes = UpdateNote.query.filter(UpdateNote.post_id == post_id)
    return render_template('post_view.html', post=post, form=form, notes=notes)
