import os
import analytics
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, session, flash
from app.process_csv import parse_csv_into_dict, process_csv_file
from app.api import segment_api_call
from app.s3_access import read_s3_file
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
import logging
from logging.config import dictConfig

from rq import Queue
from rq.job import Job
from app.worker import conn

UPLOAD_FOLDER = 'app/upload/'
ALLOWED_EXTENSIONS = set(['csv'])
NEEDED_FORM_NAMES_FOR_S3 = ['aws_access_key_id', 'aws_access_secret_key_id', 'bucket_name', 'aws_region']

app = Flask(__name__, static_folder="static")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "elijah"
app.logger.setLevel(logging.INFO)

q = Queue(connection=conn)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = FlaskForm()
    if request.method == 'POST':
        if request.form.get('s3_csv_file', None):
            # Download S3 file and process that csv
            app.logger.info("S3 Bucket Checked!")
            s3_csv_filename = session['s3_csv_file'] = request.form['s3_csv_file']
            s3_contents = read_s3_file('foxroll-csv', s3_csv_filename)

            data_parsed_successfully = False
            if s3_contents:
                data_parsed_successfully = True

            app.logger.info("s3_contents: {}".format(s3_contents))
            parsed_csv = parse_csv_into_dict(s3_contents)
            app.logger.info("parsed_csv: {}".format(parsed_csv))

            return render_template("charts.html", form=form,
                   csv_output=parsed_csv,
                   is_checked=True,
                   segment_write_key=session.get('segment_write_key', None),
                   user_id_header=session.get('user_id_header', None),
                   s3_csv_file=session.get('s3_csv_file', None),
                   data_parsed_successfully=data_parsed_successfully
                   )

        if request.files:
            file = request.files['uploadFile']
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
            processed_csv = process_csv_file(file_path)

            data_parsed_successfully = False
            if processed_csv:
                data_parsed_successfully = True

            # Can't store the content of processed csv in session bc it's too big. So we store path instead.
            session['file_path'] = file_path
            app.logger.info('Finished processing csv file...')

            return render_template("charts.html", form=form,
                   csv_output=processed_csv,
                   segment_write_key=session.get('segment_write_key', None),
                   user_id_header=session.get('user_id_header', None),
                   data_parsed_successfully=data_parsed_successfully
                   )

    return render_template("charts.html", form=form,
           csv_output=None,
           segment_write_key=session.get('segment_write_key', None),
           user_id_header=session.get('user_id_header', None)
           )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/segment_api_call', methods=['GET', 'POST'])
def api_call():
    """ Make segment api calls."""
    segment_write_key   = session['segment_write_key'] = request.form['segment_write_key']
    user_id_header      = session['user_id_header'] = request.form['user_id_header']
    s3_csv_file         = session.get('s3_csv_file', None)

    if s3_csv_file:
        s3_contents = read_s3_file('foxroll-csv', s3_csv_file)
        parsed_csv = parse_csv_into_dict(s3_contents)
        app.logger.info('processed file from s3...')
    else:
        file_path = session.get('file_path', None)
        parsed_csv = process_csv_file(file_path)
        app.logger.info('processed file from csv upload...')

    success = q.enqueue_call(
            func=segment_api_call, args=(segment_write_key, user_id_header, parsed_csv), result_ttl=5000
        )

    return render_template("charts.html", form=FlaskForm(),
            csv_output=parsed_csv,
            segment_write_key=segment_write_key,
            user_id_header=user_id_header,
            success=success
            )

@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        return str(job.result), 200
    else:
        return "Nay!", 202

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
