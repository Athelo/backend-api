from athelo import app


@app.route("/", methods=["GET"])
def hello_world():
    return "Hello World! This is Athelo Health's API"
