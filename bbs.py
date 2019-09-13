#encoding: utf-8
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from sqlalchemy import or_
from exts import db
from models import User, Question, Answer
from decorator import login_required
app = Flask(__name__)

app.config.from_pyfile('config.py')

db.init_app(app)



@app.route('/')
def index():
    content = {
        'questions': db.session.query(Question).order_by(Question.create_time.desc()).all()
    }
    return render_template('index.html', **content)

@app.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get("telephone")
        password = request.form.get("password")
        user = User.query.filter(User.telephone==telephone).first()
        if user and user.check_password(password):
            session['user_id']=user.id
            session.permanent = True
            return redirect('/')
        else:
            flash(u'手机号码或密码错误，请确认后再登录')
            return render_template('login.html')

@app.route('/regist', methods=["GET", "POST"])
def regist():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter_by(telephone=telephone).first()
        if user:
            return u'手机号已被注册，请换个号码，或使用该号码登录'
        else:
            if password1 != password2:
                return u'两次输入密码不一致'
            else:
                user = User(telephone=telephone,username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))

@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/question', methods=['GET', 'POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        # user_id = session.get('user_id')
        # user = User.query.filter(User.id == user_id).first()
        author = g.user
        db.session.add(Question(title=title,content=content,author=author))
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/detail/<question_id>/')
def detail(question_id):
    question_model = Question.query.filter_by(id=question_id).first()
    return render_template('detail.html', question=question_model)

@app.route('/add_answer/', methods=['POST'])
@login_required
def add_answer():
    content = request.form.get('answer_content')
    question_id = request.form.get('question_id')
    # user_id = session['user_id']
    # print(1, user_id, content, question_id)
    # user = User.query.filter(User.id == user_id).first()
    quest = Question.query.filter(Question.id == question_id).first()

    answer = Answer()
    answer.author = g.user
    answer.content = content
    answer.question = quest
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail', question_id=question_id))

@app.route('/search/')
def search():
    q = request.args.get("q")
    questions = Question.query.filter(
        or_(Question.title.contains(q), Question.content.contains(q))).order_by(
        Question.create_time.desc()).all()
    return render_template('index.html', questions=questions)

@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id==user_id).first()
        if user:
            g.user = user

@app.context_processor
def my_context_processor():
    if hasattr(g, 'user'):
        return {'user': g.user}
    return {}

if __name__ == '__main__':
    app.run()