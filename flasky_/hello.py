import re
from flask import Flask, render_template, session, redirect, url_for, flash, request
from datetime import datetime
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'password'

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = StringField('What is your UofT Email?')
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data

        if not form.email.data:
            submitted_name = form.name.data or ''
            session['email'] = f"{submitted_name.strip()}@mail.utoronto.ca"
        elif form.email.data.lower().endswith('@mail.utoronto.ca'):
            session['email'] = form.email.data
        else:
            return render_template('index.html', form=form, name=session.get('name'),
                                   email=None, email_error=True,
                                   current_time=datetime.utcnow())
        return redirect(url_for('chat_page'))
    return render_template('index.html', form=form, name=session.get('name'),
                           email=session.get('email'), current_time=datetime.utcnow())

@app.route('/chat')
def chat_page():
    if 'name' not in session or 'email' not in session:
        return redirect(url_for('index'))
    return render_template('chat.html', name=session['name'], email=session['email'])

@app.route('/chat', methods=['POST'])
def chat():
    if 'name' not in session or 'email' not in session:
        return {'reply': 'Please submit your name and UofT email first.'}, 401

    data = request.get_json(silent=True) or {}
    message = data.get('message', '').strip()
    name_match = re.search(r'\bmy name is ([\w\s]+)', message, re.IGNORECASE)

    if name_match:
        remembered_name = name_match.group(1).strip()
        session['chat_name'] = remembered_name
        reply = f'Nice to meet you, {remembered_name}!'
    elif 'what is my name' in message.lower():
        remembered_name = session.get('chat_name')
        if remembered_name:
            reply = f'Your name is {remembered_name}.'
        else:
            reply = "I don't know your name."
    elif 'hello' in message.lower():
        reply = 'Hello!'
    else:
        reply = "I don't understand."
    return {'reply': reply}

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)