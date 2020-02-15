import redis
import sys
import boto3

S3BUCKET = "fapomatic"

client = boto3.client("s3")
redis = redis.Redis(host="localhost", port=6379, db=0)


res = client.list_objects_v2(Bucket=S3BUCKET)

if res["IsTruncated"]:
    print("There's more")

stored_files = set()
for file in res["Contents"]:
    stored_files.add(file["Key"])

metadata_files = set()
for key in redis.keys("*:data"):
    fname = redis.hget(key, "filename")
    metadata_files.add(fname.decode("utf8"))

redis.close()

# TODO: delete metadata in this case
print("Has metadata, no stored file:")
print(metadata_files - stored_files)
# TODO: ask for metadata or delete stored file
print("Is stored, no metadata")
print(stored_files - metadata_files)

sys.exit(0)
