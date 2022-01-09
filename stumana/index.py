from stumana import login
from flask import render_template, url_for, jsonify
from stumana.admin import *
from flask_login import login_user, logout_user, login_required


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    error_msg = ""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method.__eq__('POST'):
        try:
            username = request.form['username']
            password = request.form['password']

            user = utilities.check_login(username=username, password=password)
            if user:
                login_user(user=user)
                if current_user.user_role == UserRole.ADMIN:
                    return redirect('/admin')
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


@app.route("/change-password", methods=['GET', 'POST'])
@login_required
def change_password():
    error_msg = None
    success_msg = None
    if request.method.__eq__('POST'):
        try:
            n_password = request.form['n-password']
            c_password = request.form['c-password']
            if n_password == c_password:
                change = utilities.change_password(user_id=current_user.id,
                                                   password=n_password)
                success_msg = 'Thay đổi thành công'
                return render_template('change-password.html', success_msg=success_msg)
            else:
                error_msg = "Thay đổi thất bại"

        except Exception as ex:
            error_msg = str(ex)

    return render_template('change-password.html', error_msg=error_msg)


@app.route("/user-info")
@login_required
def user_info():
    if current_user.is_authenticated:
        print(current_user.teacher)
        if current_user.user_role == UserRole.STUDENT:
            student = utilities.get_info_student(user_id=current_user.id)
            return render_template('user-info.html',
                                   student=student)
        if current_user.user_role == UserRole.STAFF:
            staff = utilities.get_info_staff(user_id=current_user.id)
            return render_template('user-info.html',
                                   staff=staff)
        if current_user.user_role == UserRole.TEACHER:
            teacher = utilities.get_info_teacher(user_id=current_user.id)
            return render_template('user-info.html',
                                   teacher=teacher)
    return render_template('user-info.html')


@app.route("/api/change-rule", methods=['PUT'])
@login_required
def change_rule():
    data = request.json
    min_age = data.get('min_age')
    max_age = data.get('max_age')
    max_size = data.get('max_size')

    result1 = utilities.change_chk_age(min=min_age, max=max_age)
    result2 = utilities.change_max_size(max=max_size)
    if result1 or result2:
        return jsonify({'status': 404,
                        'err_msg1': result1,
                        'err_msg2': result2})

    return jsonify({'status': 200})


@app.route("/arrange-class")
@login_required
def arrange_class():
    if current_user.user_role in (UserRole.STAFF, UserRole.ADMIN):
        grade12 = utilities.get_classes_by_grade(grade='12')
        grade11 = utilities.get_classes_by_grade(grade='11')
        grade10 = utilities.get_classes_by_grade(grade='10')
        select_class = request.args.get('class')
        id_this_class = ''
        total = ''
        student_name = request.args.get('student_name')
        class_name = request.args.get('class_name')

        if select_class:
            this_class = select_class.split('-')
            id_this_class = utilities.get_class_id(grade=this_class[0], class_name=this_class[1])
            total = utilities.get_total(grade=this_class[0], class_name=this_class[1])
        students = utilities.get_all_student()
        if student_name:
            students = students.filter((Student.first_name + ' ' + Student.last_name).contains(student_name))
        if class_name:
            if class_name == '0':
                students = students.filter(Student.class_id.is_(None))
            else:
                students = students.filter((ClassRoom.grade + ClassRoom.name).contains(class_name))

        return render_template('arrange-class.html',
                               grade12=grade12,
                               grade11=grade11,
                               grade10=grade10,
                               class_id=id_this_class,
                               students=students.all(),
                               total=total)
    else:
        return redirect("/")


@app.route("/api/update-class", methods=['POST'])
@login_required
def update_class():
    data = request.json
    student_id = data.get('student_id')
    classid = data.get('class_id')

    try:
        result = utilities.update_classes(student_id=student_id, class_id=classid)
    except Exception as e:
        print(e)
        return jsonify({'status': 404})

    return jsonify({'status': 200})


@app.route("/setup-class")
@login_required
def setup_class():
    if current_user.user_role in (UserRole.STAFF, UserRole.ADMIN):
        err_msg = ''
        total = ''
        grade12 = utilities.get_classes_by_grade(grade='12')
        grade11 = utilities.get_classes_by_grade(grade='11')
        grade10 = utilities.get_classes_by_grade(grade='10')
        select_class = request.args.get('class')

        if select_class:
            select_grade = select_class.split('-')
            select_class_name = select_class.split('-')
            students = utilities.get_student_by_class(grade=select_grade[0],
                                                      class_name=select_class_name[1])
            total = utilities.get_total(grade=select_grade[0],
                                        class_name=select_class_name[1])
            if students:
                return render_template('set-up.html',
                                       grade12=grade12,
                                       grade11=grade11,
                                       grade10=grade10,
                                       students=students,
                                       total=total)
            else:
                err_msg = 'Không có học sinh nào !!!'

        return render_template('set-up.html',
                               grade12=grade12,
                               grade11=grade11,
                               grade10=grade10,
                               total=total,
                               err_msg=err_msg)
    else:
        return redirect("/")


@app.route("/students-marks")
@login_required
def students_marks():
    course_id = request.args.get('course_id')
    keyword = request.args.get('keyword')
    classes = utilities.get_classes_of_teacher(current_user.id)

    if course_id:
        if utilities.check_teacher_access(user_id=current_user.id, course_id=course_id):
            if keyword:
                filtered_classes = []
                for c in classes:
                    for i in c:
                        if keyword.lower() in str(i).lower():
                            if c not in filtered_classes:
                                filtered_classes.append(c)
                return render_template("students-marks.html", classes=filtered_classes)

            if course_id:
                course = utilities.get_course_info(course_id)
                utilities.create_all_mark_records(course_id=course_id) # Tao bang diem khi vao nhap diem
                marks = utilities.get_mark_by_course_id(course_id=course_id)

                return render_template("students-marks.html",
                                       marks=marks,
                                       course=course,
                                       classes=classes)
        else:
            return redirect("/")
    else:
        return render_template("students-marks.html", classes=classes)


@app.route("/students-marks/edit/<int:student_id>")
@login_required
def edit_marks(student_id):
    year = request.args.get('year')
    subject_id = request.args.get('subject_id')

    if utilities.check_teacher_access(user_id=current_user.id, student_id=student_id, subject_id=subject_id):
        classes = utilities.get_classes_of_teacher(current_user.id)
        marks = utilities.get_marks_of_student(student_id=student_id,
                                               subject_id=subject_id,
                                               year=year)

        return render_template("student_marks.html", marks=marks, classes=classes)
    else:
        return redirect("/")


@app.route("/api/update-mark", methods=['PUT'])
@login_required
def update_marks():
    data = request.json
    subject_id = data.get('subject_id')
    student_id = data.get('student_id')
    year = data.get('year')
    mark15 = {
        '1': data.get('mark15_1'),
        '2': data.get('mark15_2')
    }
    mark45 = {
        '1': data.get('mark45_1'),
        '2': data.get('mark45_2')
    }
    final_mark = {
        '1': data.get('final_mark1'),
        '2': data.get('final_mark2')
    }
    if utilities.check_teacher_access(user_id=current_user.id, student_id=student_id, subject_id=subject_id):
        try:
            result = utilities.update_marks(subject_id=subject_id,
                                            student_id=student_id,
                                            year=year,
                                            mark15=mark15,
                                            mark45=mark45,
                                            final_mark=final_mark)
        except Exception as e:
            return jsonify({'status': 404,
                            'err_msg': e})

        return jsonify({'status': 200})

    return jsonify({'status': 404,
                    'err_msg': "You do not have the right to do this!"})


@app.route("/api/load-marks", methods=['POST'])
def load_marks():
    data = request.json
    try:
        marks = utilities.get_mark_by_course_id(course_id=data.get('course_id'),
                                                semester=data.get('semester'))
        return jsonify({'status': 200,
                        'marks': marks})
    except:
        return jsonify({'status': 404})


@app.route("/calendar")
def calendar():
    if current_user.user_role == UserRole.TEACHER:
        classes = utilities.get_classes_of_teacher(current_user.id)
    else:
        classes = None

    return render_template("calendar.html", classes=classes)


@app.route("/students",  methods=['get', 'post'])
@login_required
def list_students():
    if current_user.user_role == UserRole.STAFF:
        list_student = utilities.info_student()

        return render_template("add-students.html", list_student=list_student)
    else:
        return redirect("/")


# STAFF them hoc sinh
@app.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_students():
    if current_user.user_role == UserRole.STAFF:

        return render_template("add-students.html")


# xuat ho so hoc sinh moi
@app.route("/student/out", methods=['GET', 'POST'])
@login_required
def out_student():
    if current_user.user_role == UserRole.STAFF:
        if request.method.__eq__('POST'):
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            sex = request.form.get('sex')
            bday = request.form.get('bday')
            address = request.form.get('address')
            phone = request.form.get('phone')
            email = request.form.get('email')

            utilities.add_student(first_name=first_name,
                                  last_name=last_name,
                                  sex=sex,
                                  bday=bday,
                                  address=address,
                                  phone=phone,
                                  email=email)

            info_student = {
                'first_name': first_name,
                'last_name': last_name,
                'sex': 'Nam' if sex == 'male' else 'Nữ',
                'bday': 'Ngày ' + bday.split('-')[2] + ' Tháng ' + bday.split('-')[1] + ' Năm ' + bday.split('-')[0],
                'address': address,
                'phone': phone,
                'email': email
            }
            return render_template("out_student.html", info_student=info_student)
        return render_template("out_student.html")
    else:
        return redirect("/")


# xuat diem hoc ky
@app.route("/students-marks/out/<int:course_id>")
@login_required
def out_mark(course_id):
    semester = request.args.get('semester', 1)
    course = utilities.get_course_info(course_id=course_id)
    marks = utilities.get_mark_by_course_id(course_id=course_id, semester=semester)

    return render_template("out_mark.html", marks=marks, semester=semester, course=course)


# xuat diem ca nam
@app.route("/students-marks/out_total/<int:course_id>")
@login_required
def out_total_mark(course_id):
    if current_user.user_role == UserRole.TEACHER:
        classes = utilities.get_classes_of_teacher(current_user.id)
        course = utilities.get_course_info(course_id)
        marks = utilities.get_total_mark_by_course_id(course_id=course_id)
        keys_list = list(marks.keys())

        return render_template("out_total_mark.html",
                               marks=marks,
                               keys_list=keys_list,
                               course=course,
                               classes=classes)

    else:
        return redirect("/")


# xuat danh sach lop hoc
@app.route("/setup-class/out")
@login_required
def out_class():
    this_class = request.args.get('class')
    if this_class:
        this_grade = this_class.split('-')
        this_class_name = this_class.split('-')
        students = utilities.get_student_by_class(grade=this_grade[0],
                                                  class_name=this_class_name[1])
        total = utilities.get_total(grade=this_grade[0],
                                    class_name=this_class_name[1])

        if students:
            return render_template('out_class.html',
                                   students=students,
                                   total=total)
    return redirect("/setup-class")


@login.user_loader
def user_load(user_id):
    return utilities.get_user_by_id(user_id=user_id)


@app.context_processor
def common_response():
    return {
        'UserRole': UserRole,
        'current_year': datetime.now().year
    }


if __name__ == '__main__':
    app.run(debug=True)
