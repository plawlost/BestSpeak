from flask import render_template, url_for, redirect, flash, request, current_app
from bestspeak import app, db
from bestspeak.forms import RegistrationForm, LoginForm
from bestspeak.models import User, Question, Answer
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from bestspeak.config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Hesabınız başarıyla oluşturuldu!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Kayıt Ol', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Giriş başarısız. Lütfen kullanıcı adı ve parolayı kontrol edin.', 'danger')
    return render_template('login.html', title='Giriş Yap', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        text = request.form.get('text')
        audio = request.files['audio']
        if audio and allowed_file(audio.filename):
            filename = secure_filename(audio.filename)
            audio.save(os.path.join(UPLOAD_FOLDER, filename))  # Burada direkt UPLOAD_FOLDER'ı kullanabiliriz.
            question = Question(text=text, audio_filename=filename)
            db.session.add(question)
            db.session.commit()
            flash('Soru başarıyla eklendi!', 'success')
    return render_template('add_question.html')

@app.route('/answer_question/<int:question_id>', methods=['POST'])
@login_required  # Bu route'a sadece giriş yapmış kullanıcılar erişebilmeli
def answer_question(question_id):
    question = Question.query.get_or_404(question_id)
    audio = request.files.get('audio')  # .get() kullanarak eğer audio dosyası yoksa None değeri alabiliriz.
    if audio and allowed_file(audio.filename):
        filename = secure_filename(audio.filename)
        audio.save(os.path.join(UPLOAD_FOLDER, filename))  # Burada direkt UPLOAD_FOLDER'ı kullanabiliriz.
        answer = Answer(student_id=current_user.id, question_id=question.id, audio_filename=filename)
        db.session.add(answer)
        db.session.commit()
        flash('Cevabınız başarıyla kaydedildi!', 'success')
    return redirect(url_for('index'))