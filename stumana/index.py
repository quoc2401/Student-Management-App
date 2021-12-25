from stumana import login
from flask import render_template, url_for, jsonify
from admin import *
from flask_login import login_user, logout_user


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/user_login', methods=['get', 'post'])
def user_login():
    error_msg = ""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method.__eq__('POST'):
        try:
            username = request.form['username']
            password = request.form['password']

            user = utilities.check_login(username=username, password=password, role=UserRole.STUDENT)
            user_admin = utilities.check_login(username=username, password=password, role=UserRole.ADMIN)
            user_staff = utilities.check_login(username=username, password=password, role=UserRole.STAFF)
            user_teacher = utilities.check_login(username=username, password=password, role=UserRole.TEACHER)
            if user:
                login_user(user=user)

                next = request.args.get('next', '/')
                return redirect(next)
            else:
                error_msg = "Sai tài khoản hoặc mật khẩu !!!"

            if user_admin:
                login_user(user=user_admin)
                return redirect('/admin')

            if user_staff:
                login_user(user=user_staff)
                return render_template('staff.html')

            if user_teacher:
                login_user(user=user)
                return redirect('/admin')

        except Exception as ex:
            error_msg = str(ex)

    return render_template('login.html', error_msg=error_msg)


@app.route("/user_logout")
def user_logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/api/change-rule", methods=['POST'])
def change_rule():
    data = request.json
    min_age = data.get('min_age')
    max_age = data.get('max_age')
    max_size = data.get('max_size')

    result1 = utilities.change_chk_age(min=min_age, max=max_age)
    result2 = utilities.change_max_size(max=max_size)
    if result1 or result2:
        return jsonify({'status': 404})

    return jsonify({'status': 200})


@app.route("/staff/arrange-class")
def arrange_class():
    return render_template('arrange-class.html')


@login.user_loader
def user_load(user_id):
    return utilities.get_user_by_id(user_id=user_id)


@app.context_processor
def common_response():
    return {
        'ADMIN': UserRole.ADMIN,
        'year': datetime.now().year
    }


if __name__ == '__main__':
    app.run(debug=True)
