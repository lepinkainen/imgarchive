__version__ = "0.1.0"

from flask import Flask
from flask import render_template, make_response, g, send_from_directory
import redis

# add object
# hset <sha1sum>:data filename <filename>
# sadd <sha1sum>:tags tag1 tag2
# sadd tag:tag1 <sha1sum>
# sadd tag:tag2 <sha1sum>

# get random images for certain tag
# srandmember tag:tag1 <count>

# get random image


# Open a shared connection to db
def get_redis():
    if "redis" not in g:
        g.redis = redis.Redis(host="localhost", port=6379, db=0)

    return g.redis


def close_redis(e=None):
    redis = g.pop("redis", None)

    if redis is not None:
        redis.close()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev")
    # Close redis connection on teardown
    app.teardown_appcontext(close_redis)

    # Show with tag
    @app.route("/")
    def index():

        keys = get_redis().keys("tag:*")
        keys = map(lambda x: x.decode("utf-8")[4:], keys)
        keylist = list(keys)
        keylist.sort()

        tagdata = []
        for key in keylist:
            tags = get_redis().smembers("tag:%s" % key)
            tagdata.append((key, len(tags)))

        return render_template("index.html", tags=tagdata)

    # get object link method
    # S3 / Local FS / Full URL to internet?

    # View by tag
    # get count random objects from tag
    # SRANDMEMBER tag count

    # View by key (one image)

    @app.route("/files/<path:filename>")
    def download_file(filename):
        return send_from_directory("files", filename, as_attachment=True)

    # View by tag
    @app.route("/tag/")
    @app.route("/tag/<string:object>")
    def tag_object(object=None):
        if not object:
            return make_response({"error": "no object specified"}, 400)

        random_object = get_redis().srandmember("tag:%s" % object, 1)
        filename = get_redis().hget(
            "%s:data" % random_object[0].decode("utf-8"), "filename"
        )
        filetags = get_redis().smembers("%s:tags" % random_object[0].decode("utf-8"))
        filetags = map(lambda x: x.decode("utf-8"), filetags)

        return render_template(
            "randomtag.html",
            tag=object,
            filename=filename.decode("utf-8"),
            tags=filetags,
        )

    return app
