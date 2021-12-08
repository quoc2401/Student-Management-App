from stumana import app, utilities, login
from flask import render_template, redirect, url_for, request, session
from admin import *
from flask_login import current_user, login_user, logout_user


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/user_login', methods=['get', 'post'])
def user_login():
    error_msg = ""
    if request.method.__eq__('POST'):
        try:
            username = request.form['username']
            password = request.form['password']

            user = utilities.check_login(username=username, password=password)
            if user:
                login_user(user=user)

                next = request.args.get('next', '/')
                return redirect(next)
            else:
                error_msg = "Sai tài khoản hoặc mật khẩu !!!"

        except Exception as ex:
            error_msg = str(ex)

    return render_template('login.html', error_msg=error_msg)


@app.route("/user_logout")
def user_logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/admin/changerule", methods=['POST'])
def change_rule():
    err_msg = 0
    if request.method.__eq__('POST'):
        min_age = request.form.get('min_age')
        max_age = request.form.get('max_age')
        max_size = request.form.get('max_size')
        result1 = utilities.change_chk_age(min=min_age, max=max_age)
        result2 = utilities.change_max_size(max=max_size)
        # print(config.min_age)
        if result1:
            err_msg = 1
        if result2:
            err_msg = 2
    return redirect(url_for('change_rule', err_msg=err_msg))


@login.user_loader
def user_load(user_id):
    return utilities.get_user_by_id(user_id=user_id)


@app.context_processor
def common_response():
    return {
        'ADMIN': UserRole.ADMIN
    }


if __name__ == '__main__':
    app.run(debug=True)
