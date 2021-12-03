from stumana import app
from flask import render_template
from admin import *


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
