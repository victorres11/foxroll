import boto3
import logging

# logger setup
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

aws_access_key_id = "AKIAIBNBGVBZLT7LLNPQ" # should be user input.
aws_secret_access_key = "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" # should be user input.

S3_BUCKET_NAME         = "foxroll-csv" # should be user input
S3_UPLOAD_BUCKET_NAME  = "foxroll-csv-upload"
S3_REGION              = "us-east-2"   # should be user input
S3_STORAGE_PREFIX      = "https://s3.{region}.amazonaws.com/{bucket_name}/".format(region=S3_REGION, bucket_name=S3_BUCKET_NAME)

resource = boto3.resource('s3', region_name=S3_REGION) #high-level object-oriented API


def does_bucket_exists():
    bucket = s3.Bucket('mybucket')
    exists = True
    try:
        s3.meta.client.head_bucket(Bucket='mybucket')
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            exists = False
    return exists

def read_s3_file(bucket_name, file_name):
    logger.info("Checking S3 for file {} in bucket {}".format(file_name, bucket_name))

    # Doesn't seem like region is needed? Validate for sure.
    s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        region_name=S3_REGION)

    obj = s3.Object(bucket_name, file_name)
    # Will download csv contests as string i.e. 'email, products_bought, last_order\npeterclark@me.com,4,123456\n'

    contents = obj.get()['Body'].read().splitlines()
    # reader = csv.DictReader(contents)
    # ouput = [ line for line in reader ]
    return contents

def upload_to_s3(filename, filepath):
    # TODO: Do this froma  single place.
    # filename = 'test.csv'
    s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        region_name=S3_REGION)
    # Upload a new file
    data = open(filepath, 'rb')
    s3.Bucket(S3_UPLOAD_BUCKET_NAME).put_object(Key=filename, Body=data)
    logger.info("Uploaded file {} in S3 bucket {}".format(filename, S3_UPLOAD_BUCKET_NAME))
