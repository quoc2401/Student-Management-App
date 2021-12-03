from stumana import app
from flask import render_template, redirect
from admin import *


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin/change-rule", methods=['POST', 'GET'])
def change_rule():
    if request.method.__eq__('POST'):
        min_age = request.form.get('min-age')
        max_age = request.form.get('max-age')
        result = utilities.change_chk_age(min_age=int(min_age), max_age=int(max_age))
        print(result)
    return redirect("changerule")


@app.context_processor
def common_response():
    return {

    }


if __name__ == '__main__':
    app.run(debug=True)
