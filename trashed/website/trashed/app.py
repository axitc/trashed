# Parameters
THRESHOLD = 0.9
IMG_WIDTH, IMG_HEIGHT = 224, 224


from tensorflow.keras.models import load_model
cnn = load_model('cnn.keras')


import os
import sqlite3

# https://docs.python.org/3/library/sqlite3.html
# https://docs.python.org/3/library/os.path.html
# check_same_thread=False to avoid concurrency error
if os.path.exists('trash.db'):
    con = sqlite3.connect('trash.db', check_same_thread=False)
    cur = con.cursor()
    con.commit()
else:
    con = sqlite3.connect('trash.db', check_same_thread=False)
    cur = con.cursor()
    # images are stored in images dir
    # imagefile's name correspongs to rowid of database
    cur.execute('''
        CREATE TABLE trash (
            location TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            label INTEGER,
            report INTEGER DEFAULT 0);
    ''')
    con.commit()


from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import FileField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'arbitrarilylongsecretkey'


class TrashForm(FlaskForm):
    image = FileField(u'Image File', validators=[DataRequired()])
    location = StringField(u'Trash Location', validators=[DataRequired()])
    submit = SubmitField('Submit')

import cv2
import numpy as np
@app.route('/', methods=['GET', 'POST'])
def index():
    image = None
    location = None
    form = TrashForm()
    if form.validate_on_submit():
        image = form.image.data
        location = form.location.data

        cur.execute(f"""
            INSERT INTO trash (location) VALUES
                ('{location}');
        """)
        con.commit()

        imagefilename = str(cur.lastrowid) + '.jpg'
        image.save(os.path.join('images', imagefilename))

        image = cv2.imread(os.path.join('images',imagefilename))
        image = cv2.resize(image, (IMG_WIDTH, IMG_HEIGHT))
        image = image.astype('float32')
        image /= 225
        image = np.expand_dims(image, axis=0)

        prediction = cnn.predict(image)[0][0]
        label = 1 if prediction > THRESHOLD else 0

        cur.execute(f'''
            UPDATE trash
            SET label = {label}
            WHERE rowid = {cur.lastrowid};
        ''')
        con.commit()

        if prediction > THRESHOLD:
            return redirect(url_for('positive'))
        else:
            return redirect(url_for('negative'))
    return render_template('index.html', form=form, image=image, location=location)

@app.route('/positive')
def positive():
    return render_template('positive.html')

class ReportForm(FlaskForm):
    submit = SubmitField('Report')

@app.route('/negative', methods=['GET', 'POST'])
def negative():
    form = ReportForm()
    if form.validate_on_submit():
        return redirect(url_for('report'))
    return render_template('negative.html', form=form)

@app.route('/report')
def report():
    cur.execute(f'''
        UPDATE trash
        SET report = 1
        WHERE rowid = {cur.lastrowid};
    ''')
    con.commit()
    return render_template('report.html')

@app.route('/guide')
def guide():
    return render_template('guide.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.errorhandler(404)
def err404(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def err500(e):
    return render_template('500.html'), 500
