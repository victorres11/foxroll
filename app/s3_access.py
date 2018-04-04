import boto3
import botocore
import logging
import gzip
import shutil

# logger setup
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

aws_access_key_id = "AKIAIBNBGVBZLT7LLNPQ" # should be user input.
aws_secret_access_key = "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" # should be user input.

S3_BUCKET_NAME         = "foxroll-csv" # should be user input
S3_UPLOAD_BUCKET_NAME  = "foxroll-csv-upload"
S3_REGION              = "us-east-2"
S3_STORAGE_PREFIX      = "https://s3.{region}.amazonaws.com/{bucket_name}/".format(region=S3_REGION, bucket_name=S3_BUCKET_NAME)

resource = boto3.resource('s3', region_name=S3_REGION) #high-level object-oriented API

def convert_to_gzip(filename, filepath):
    content = open(filepath)

    gzip_filename = '{}.gz'.format(filename)
    gzip_filepath = filepath.replace(filename, gzip_filename)

    with open(filepath, 'rb') as f_in, gzip.open(gzip_filepath, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

    return gzip_filename, gzip_filepath

def read_gzip_file(filename):
    with gzip.open(filename, 'rb') as f:
        return f.read().splitlines()

def init_s3_client():
    config = botocore.config.Config(read_timeout=240, retries={'max_attempts':10})
    return boto3.resource('s3', aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        region_name=S3_REGION, config=config)

def read_s3_file(bucket_name, filename, compressed=False):
    if compressed:
        logger.info("Anticipating compressed file...")
        filename = "{}.gz".format(filename)

    logger.info("Checking S3 for file {} in bucket {}".format(filename, bucket_name))
    s3 = init_s3_client()

    # TODO: Update to use temporary files here for scalability!!!
    filepath = 'app/download/{}'.format(filename)
    logger.info("Downloading file to {}...".format(filepath))
    s3.Bucket(bucket_name).download_file(filename, filepath)

    logger.info("reading file...")
    contents = read_gzip_file(filepath) if compressed else open(filepath, 'rb').readlines()
    return contents

def upload_to_s3(filename, filepath, compressed=False):
    s3 = init_s3_client()

    # Upload a new file
    if compressed:
        logger.info("Converting csv into compressed version...")
        filename, filepath = convert_to_gzip(filename, filepath)

    data = open(filepath, 'rb')

    s3.Bucket(S3_UPLOAD_BUCKET_NAME).put_object(Key=filename, Body=data.read())
    logger.info("Uploaded file {} in S3 bucket {}".format(filename, S3_UPLOAD_BUCKET_NAME))
