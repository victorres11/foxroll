import os
import analytics
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, session
from process_csv import process_csv
from api import segment_api_call
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
import logging
from logging.config import dictConfig

UPLOAD_FOLDER = '/upload'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "foobar"
app.logger.setLevel(logging.INFO)

app.logger.info('Info Logger is working')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    app.logger.info('hello from upload_file loggerr')
    form = FlaskForm(csrf_enabled=False)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER']))
            # return redirect(url_for('uploaded_file', filename=filename))
            processed_csv = process_csv(file)
            session['csv_output'] = processed_csv
            app.logger.info('processed csv')
            return render_template("index.html", form=form, csv_output=session['csv_output'])

    return render_template("index.html", form=form, processed_csv=None)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/segment_api_call', methods=['GET', 'POST'])
def api_call():
    """ API CALL"""
    app.logger.info('logger in api_call')
    segment_write_key = request.form['segment_write_key']
    segment_api_call(segment_write_key, session['csv_output'])
    return render_template("index.html", form=FlaskForm(), csv_output=session['csv_output'], segment_write_key=segment_write_key)
    # return "Hello segment api call"
