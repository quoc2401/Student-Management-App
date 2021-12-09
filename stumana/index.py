from stumana import app, login
from flask import render_template, request, redirect
import os
import utilities
from flask_login import login_user
from admin import *


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/admin-login', methods=['post'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = utilities.check_login(username=username, password=password)
    if user:
        login_user(user=user)

    return redirect('/admin')


@login.user_loader
def load_user(user_id):
    return utilities.get_user_by_id(user_id=user_id)


if __name__ == '__main__':
    app.run(debug=True)
