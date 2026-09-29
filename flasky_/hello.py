from flask import Flask, render_template, session, redirect, url_for, flash
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
            session['email'] = f"{form.name.data.strip()}@mail.utoronto.ca"
        elif form.email.data.lower().endswith('@mail.utoronto.ca'):
            session['email'] = form.email.data
        else:
            return render_template('index.html', form=form, name=session.get('name'),
                                   email=None, email_error=True,
                                   current_time=datetime.utcnow())
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'),
                           email=session.get('email'), current_time=datetime.utcnow())

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)