from stumana import app
from flask import render_template, redirect, url_for
from admin import *


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin/changerule", methods=['POST', 'GET'])
def change_rule():
    if request.method.__eq__('POST'):
        min_age = request.form.get('min-age')
        max_age = request.form.get('max-age')
        max_size = request.form.get('max-size')

        result1 = utilities.change_chk_age(min_age=min_age, max_age=max_age)
        result2 = utilities.change_chk_max_size(max_size=max_size)
        print(result1)
        print(result2)

    return redirect(url_for("change_rule"))


@app.context_processor
def common_response():
    return {

    }


if __name__ == '__main__':
    app.run(debug=True)
