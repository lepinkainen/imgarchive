import redis
import sys

redis = redis.Redis(host="localhost", port=6379, db=0)

# del object
# del <sha1sum>:data
# del <sha1sum>:tags
# go through tags and delete image from each tag set

# add.py filename.jpg tag1 tag2 tag3

# TODO: delete by filename (find hash from redis)

if len(sys.argv) < 2:
    print("usage: del.py <hash>")
    sys.exit(0)

sha = sys.argv[1]

# TODO: Option(?) to delete file from source

# Delete object data
redis.delete("%s:data" % sha)
# Delete object tags
redis.delete("%s:tags" % sha)

# Tags
tags = redis.keys("tag:*")

# Remove object from all tags
for tag in tags:
    redis.srem(tag, sha)

redis.close()
