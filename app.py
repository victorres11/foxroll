import os
import analytics
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, session, flash
from app.process_csv import process_csv
from app.api import segment_api_call
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
import logging
from logging.config import dictConfig

UPLOAD_FOLDER = 'app/upload/'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "elijah"
app.logger.setLevel(logging.INFO)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = FlaskForm()
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file detected. Please upload a csv file!')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('We can only accept CSV files!')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            app.logger.info('Saving file to server...')
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            app.logger.info('File path: {}'.format(file_path))
            file.save(os.path.join(file_path))
            app.logger.info('File saved...')

            if session.get('csv_output', None):
                del session['csv_output']

            app.logger.info('Processing new csv file...')
            session['csv_output'] = process_csv(file_path)
            app.logger.info('Finished processing csv file...')
            return render_template("index.html", form=form,
                   csv_output=session.get('csv_output', None),
                   segment_write_key=session.get('segment_write_key', None),
                   user_id_header=session.get('user_id_header', None)
                   )

    return render_template("index.html", form=form, processed_csv=None)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/segment_api_call', methods=['GET', 'POST'])
def api_call():
    """ Make segment api calls."""
    app.logger.info('logger in api_call')
    segment_write_key = session['segment_write_key'] = request.form['segment_write_key']
    user_id_header    = session['user_id_header'] = request.form['user_id_header']

    segment_api_call(segment_write_key, user_id_header, session['csv_output'])

    return render_template("index.html", form=FlaskForm(),
            csv_output=session.get('csv_output', None),
            segment_write_key=segment_write_key,
            user_id_header=user_id_header
            )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
