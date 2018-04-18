import os
import analytics
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, session, flash
from app.process_csv import parse_csv_into_dict, process_csv_file, count_rows, is_column_consistent
from app.api import segment_api_call
from app.s3_access import upload_to_s3, download_s3_file, S3_FLOW_BUCKET_NAME, CSV_FLOW_BUCKET_NAME
from app.utils import redis_worker_wrapper, shard_csv
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
import logging
from logging.config import dictConfig
from worker import conn

from rq import Queue
from rq.job import Job

UPLOAD_FOLDER = 'app/upload/'
ALLOWED_EXTENSIONS = set(['csv'])
NEEDED_FORM_NAMES_FOR_S3 = ['aws_access_key_id', 'aws_access_secret_key_id', 'bucket_name', 'aws_region']
SHARD_THRESHOLD = 50000

app = Flask(__name__, static_folder="static")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "elijah"
app.logger.setLevel(logging.INFO)

q = Queue(connection=conn)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_shards_to_s3(sharded_filepaths, bucket):
    for shard_path in sharded_filepaths:
        app.logger.info('Initiating S3 upload for {}...'.format(shard_path))
        shard_name = shard_path.split('/')[-1]
        upload_to_s3(shard_name, shard_path, bucket)
        app.logger.info('File {} saved to S3...'.format(shard_name))

@app.route('/', methods=['GET', 'POST'])
def foxroll_form():
    form = FlaskForm()
    if request.method == 'POST':
        # Download S3 file and process that csv.
        if request.form.get('s3_csv_file', None):
            app.logger.info("S3 flow chosen...")
            s3_csv_filename = session['s3_csv_file'] = request.form['s3_csv_file']
            s3_bucket = session['s3_bucket'] = S3_FLOW_BUCKET_NAME

            app.logger.info("Download and shard the file...")
            filepath = download_s3_file(s3_bucket, s3_csv_filename)
            shard_filename_template = "{}_shard_%s.csv".format(s3_csv_filename)
            sharded_filepaths = shard_csv(open(filepath), row_limit=SHARD_THRESHOLD,
                output_name_template=shard_filename_template, output_path='./app/download',
                keep_headers=True)

            upload_shards_to_s3(sharded_filepaths, s3_bucket)
            app.logger.info('{} shard(s) made....'.format(len(sharded_filepaths)))

            # Save shard filepaths.
            session['sharded_filepaths'] = sharded_filepaths

            # Parse for preview.
            shard_filecontents = open(sharded_filepaths[0]).readlines()
            parsed_csv = parse_csv_into_dict(shard_filecontents, limit=50)

            data_parsed_successfully = False
            if parsed_csv:
                data_parsed_successfully = True

            csv_row_count = session['csv_row_count'] = count_rows(filepath)

            # is_column_consistent = test_column_consistency(sharded_filepaths)
            is_column_consistent = True

            return render_template("charts.html", form=form,
                   csv_output=parsed_csv,
                   is_checked=True,
                   segment_write_key=session.get('segment_write_key', None),
                   user_id_header=session.get('user_id_header', None),
                   s3_csv_file=session.get('s3_csv_file', None),
                   data_parsed_successfully=data_parsed_successfully,
                   csv_row_count=csv_row_count or None,
                   is_column_consistent=is_column_consistent
                   )

        # Handle CSV Upload.
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
            filename = session['uploaded_csv_filename'] = secure_filename(file.filename)
            filepath = session['csv_filepath'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            s3_bucket = session['s3_bucket'] = CSV_FLOW_BUCKET_NAME

            app.logger.info('File path: {}'.format(filepath))
            file.save(os.path.join(filepath))
            app.logger.info('File saved to server...')

            sharded_filepaths = shard_csv(open(filepath), row_limit=SHARD_THRESHOLD,
                output_name_template='shard_%s.csv', output_path='./app/download',
                keep_headers=True)
            session['sharded_filepaths'] = sharded_filepaths
            app.logger.info('{} shard(s) made....'.format(len(sharded_filepaths)))

            upload_shards_to_s3(sharded_filepaths, s3_bucket)

            if session.get('csv_output', None):
                del session['csv_output']

            app.logger.info('Processing new csv file...')
            # TODO: Update this so it all uses the same function.
            processed_csv = process_csv_file(filepath, limit=50)

            data_parsed_successfully = False
            if processed_csv:
                data_parsed_successfully = True

            # Run tests on the files.
            is_column_consistent = True
            # is_column_consistent = test_column_consistency(sharded_filepaths)

            # app.logger.info("Running consistency data test finished...")

            csv_row_count = session['csv_row_count'] = count_rows(filepath)

            # Can't store the content of processed csv in session bc it's too big. So we store path instead.
            session['filepath'] = filepath
            app.logger.info('Finished processing csv file...')

            return render_template("charts.html", form=form,
                   csv_output=processed_csv,
                   segment_write_key=session.get('segment_write_key', None),
                   user_id_header=session.get('user_id_header', None),
                   data_parsed_successfully=data_parsed_successfully,
                   csv_row_count=csv_row_count or None,
                   is_column_consistent=is_column_consistent,
                   has_empty_column=False
                   )

    return render_template("charts.html", form=form,
           csv_output=None,
           segment_write_key=session.get('segment_write_key', None),
           user_id_header=session.get('user_id_header', None)
           )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def test_column_consistency(sharded_filepaths):
    app.logger.info("Running consistency data test now...")
    data_type_by_header = {}
    for shard_filepath in sharded_filepaths:
        app.logger.info("Checking shard {}".format(shard_filepath))
        print sharded_filepaths
        print "data_type_by_header in loop in app.py is: {}".format(data_type_by_header)
        shard_contents = open(shard_filepath).readlines() # is it still available on harddisk?
        parsed_csv = parse_csv_into_dict(shard_contents)
        column_consistency = is_column_consistent(parsed_csv, data_type_by_header)
        if not column_consistency:
            app.logger.info("Detected a column with column inconsistency...")
            return column_consistency
    return column_consistency

@app.route('/segment_api_call', methods=['GET', 'POST'])
def api_call():
    """ Make segment api calls."""
    segment_write_key   = session['segment_write_key'] = request.form['segment_write_key']
    user_id_header      = session['user_id_header'] = request.form['user_id_header']
    s3_bucket           = session['s3_bucket']

    sharded_filepaths = session.get('sharded_filepaths')
    shard_filecontents = open(sharded_filepaths[0]).readlines()
    parsed_csv = parse_csv_into_dict(shard_filecontents, limit=50)

    # Each shard will be it's own redis message.
    for shard_path in sharded_filepaths:
        # will need to retrieve from s3
        shard_name = shard_path.split('/')[-1]
        app.logger.info('Sending {} to Redis queue...'.format(shard_name))
        success = q.enqueue_call(
                func=redis_worker_wrapper,
                args=(segment_write_key, s3_bucket, user_id_header, parse_csv_into_dict, shard_name,),
                result_ttl=5000,
                timeout=2000
            )

    app.logger.info('Finished sending to redis queue....')

    return render_template("charts.html", form=FlaskForm(),
            csv_output=parsed_csv,
            segment_write_key=segment_write_key,
            user_id_header=user_id_header,
            success=success,
            csv_row_count=session.get('csv_row_count', None)
            )

@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        return str(job.result), 200
    else:
        return "Nay!", 202

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404-alt.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500-alt.html'), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
