import boto3
import click

session = boto3.Session(profile_name='DevOps')
s3 = session.resource('s3')

@click.group()
def cli():
    "Webotron deploys websites to AWS"
    pass

@cli.command('list_buckets')
def list_buckets():
    "list all buckets"
    for bucket in s3.buckets.all():
        print(bucket)

@cli.command('list_bucket_objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    print('List objects in an S3 bucket')
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)

if __name__ == "__main__":
    cli()