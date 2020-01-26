#-*- coding: utf-8 -*-
from pathlib import Path
#from botoccore.exceptions import ClientError
'''Class for S3 Buckets'''
import mimetypes

class BucketManager:
    def __init__(self,session):
        '''Create BucketManager object'''
        self.session = session
        self.s3 = session.resource('s3')

    def all_buckets(self):
        '''Get an iterator for all buckets'''
        return self.s3.buckets.all()

    def all_objects(self,bucket):
        '''Get an iterator for all objects'''
        return self.s3.Bucket(bucket).objects.all()

    def init_bucket(self, bucket_name):
        '''Create bucket or return an existing one by name '''
        s3_bucket = None
        try:
            s3_bucket = self.s3.create_bucket(
                Bucket = bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': self.session.region_name
                }
            )
        except ClientError as error:
            if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket = self.s3.Bucket(bucket)
            else:
                raise error

        return s3_bucket

    def set_policy(self,bucket):
        '''Set the bucket policy to be readable by everyone'''
        policy = """
            {
                "Version":"2012-10-17",
                "Statement":[{
                "Sid":"PublicReadForGetBucketObjects",
                "Effect":"Allow",
                "Principal": "*",
                "Action":["s3:GetObject"],
                "Resource":["arn:aws:s3:::automatingawsbill/*"
               ]
             }
            ]
            }
            """ % bucket.name
        policy = policy.strip()
        pol = bucket.Policy()
        pol.put(Policy=policy)

    def configure_webiste(self,bucket):
        bucket.Website().put(WebsiteConfiguration={
            'ErrorDocument':{
                'Key': 'error.html'
                },
            'IndexDocument': {
                'Suffix': 'index.html'
            }
            })

    def upload_file(self,bucket, path, key):
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                     'ContentType': content_type
                     }
                            )

    def sync(self,pathname,bucket_name):
        bucket = self.s3.Bucket(bucket_name)

        root = Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for p in target.iterdir():
                if p.is_dir():
                    handle_directory(p)
                if p.is_file():
                    self.upload_file(bucket, str(p), str(p.relative_to(root)))

        handle_directory(root)
