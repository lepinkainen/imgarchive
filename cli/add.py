import redis
import hashlib
import sys
import os.path
import boto3

redis = redis.Redis(host="localhost", port=6379, db=0)

# add object
# hset <sha1sum>:data filename <filename>
# sadd <sha1sum>:tags tag1 tag2
# sadd tag:tag1 <sha1sum>
# sadd tag:tag2 <sha1sum>

# add.py filename.jpg tag1 tag2 tag3

S3BUCKET = "fapomatic"

if len(sys.argv) < 3:
    print("usage: add.py <filename> <tags...>")
    print("       at least one tag is required")
    sys.exit(0)

# TODO: Copy file to actual hosting location

filename = sys.argv[1]
basefilename = os.path.basename(filename)

tags = sys.argv[2:]

# Hash file to get UID
BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

sha1 = hashlib.sha1()
with open(filename, "rb") as f:
    while True:
        data = f.read(BUF_SIZE)
        if not data:
            break
        sha1.update(data)

sha = sha1.hexdigest()


print("Storing file %s with hash %s" % (filename, sha))

# Upload the file to S3
s3 = boto3.resource("s3")
s3.meta.client.upload_file(
    filename,
    S3BUCKET,
    basefilename,
    ExtraArgs={"ACL": "public-read", "CacheControl": "max-age=3153600"},
)

# Save metadata to Redis
# Set filename
redis.hset("%s:data" % sha, "filename", basefilename)
# Set tags
redis.sadd("%s:tags" % sha, *tags)

# Add file to tag collections
for tag in tags:
    redis.sadd("tag:%s" % tag, sha)

redis.close()
