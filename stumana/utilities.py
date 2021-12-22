from stumana import db
from sqlalchemy import text, func, update, null
from stumana.models import User, Student, Mark, Subject, XVMark, XXXXVMark, ClassRoom, Course, Teacher
import config


# Dang nhap
def get_user_by_id(user_id):
    return User.query.get(user_id)


def check_login(username, password):
    # password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


# Thay doi tuoi quy dinh
def change_chk_age(min=None, max=None):
    try:
        min = int(min)
        _min_age = str(min - 1)
        drop_min = "CALL PROC_DROP_CHECK_CONSTRAINT('student', 'chk_age1');"
        add_min = "CALL PROC_ADD_CHECK_CONSTRAINT('student', 'chk_age1'," \
                  " '(YEAR(join_date) - YEAR(bday)) > " + _min_age + "');"
        db.engine.execute(text(drop_min))
        db.engine.execute(text(add_min))
        config.min_age = min
        max = int(max)
        _max_age = str(max + 1)
        drop_max = "CALL PROC_DROP_CHECK_CONSTRAINT('student', 'chk_age2');"
        add_max = "CALL PROC_ADD_CHECK_CONSTRAINT('student', 'chk_age2'," \
                  " '(YEAR(join_date) - YEAR(bday)) < " + _max_age + "');"
        db.engine.execute(text(drop_max))
        db.engine.execute(text(add_max))
        config.max_age = max
    except Exception as e:
        return str(e)


# thay doi si so toi da
def change_max_size(max=None):
    try:
        if max:
            max = int(max)
            _max_size = str(max)

            # tao cau lenh sql
            drop_trigger = "drop trigger if exists before_enter_class;"
            create_trigger = " create trigger before_enter_class after update on class_room for each row"\
                " begin declare new_size int; set new_size = (select total from class_room"\
                " where new.id = id); if new_size >= (" + _max_size + " + 1) then"\
                " signal sqlstate '45001' set message_text = 'Vuot qua so luong toi da'; end if; end;"

            db.engine.execute(text(drop_trigger))
            db.engine.execute(text(create_trigger))
            config.max_size = max
    except Exception as e:
        return str(e)


def get_class_by_id(classroom_id):
    return ClassRoom.query.get(classroom_id)


def count_student_by_class(class_id):
    return db.session.query(func.count(Student.id))\
        .join(ClassRoom, ClassRoom.id.__eq__(Student.class_id))\
        .filter(ClassRoom.id.__eq__(class_id)).all()


def get_students_mark(class_id=None, semester=None, year=None, subject_id=None):
    students = db.session.query(Subject, Student, Mark.semester, Mark.year, XVMark, XXXXVMark, Mark.FinalMark, Mark.avg)\
                                .join(Mark, Mark.subject_id.__eq__(Subject.id))\
                                .join(Student, Student.id.__eq__(Mark.student_id))\
                                .join(XVMark, XVMark.id.__eq__(Mark.XV_mark_id), isouter=True)\
                                .join(XXXXVMark, XXXXVMark.id.__eq__(Mark.XXXXV_mark_id), isouter=True)

    if class_id:
        students = students.filter(Student.class_id.__eq__(class_id))
    if semester:
        students = students.filter(Mark.semester.__eq__(semester))
    if year:
        students = students.filter(Mark.year.__eq__(year))
    if subject_id:
        students = students.filter(Mark.subject_id.__eq__(subject_id))

    return students.all()


def average_ignore_none(numbers):
    total = []
    for n in numbers:
        if n:
            total.append(n)
    avg = sum(total) / len(total)
    return avg


def get_student_by_class(grade, class_name):
    return db.session.query(Student)\
            .join(ClassRoom, ClassRoom.id.__eq__(Student.class_id))\
            .filter(ClassRoom.name.__eq__(class_name))\
            .filter(ClassRoom.grade.__eq__(grade)).all()


def get_total(grade, class_name):
    return db.session.query(ClassRoom.total) \
        .filter(ClassRoom.name.__eq__(class_name)) \
        .filter(ClassRoom.grade.__eq__(grade)).first()


def cal_avg_mark(subject_id, semester, year):
    marks = get_students_mark(subject_id=subject_id, semester=semester, year=year)

    for s in marks:
        if s.XVMark:
            mark15 = average_ignore_none([s.XVMark.col1, s.XVMark.col2, s.XVMark.col3, s.XVMark.col4, s.XVMark.col5])
        else:
            mark15 = 0
        if s.XXXXVMark:
            mark45 = average_ignore_none([s.XXXXVMark.col1, s.XXXXVMark.col2, s.XXXXVMark.col3])
        else:
            mark45 = 0
        if s.FinalMark:
            avg = (mark15 + mark45 * 2 + s.FinalMark * 3) / 6
        else:
            avg = (mark15 + mark45 * 2) / 6
        result = db.session.query(Mark).filter(Mark.subject_id.__eq__(subject_id),
                                               Mark.student_id.__eq__(s.Student.id),
                                               Mark.semester.__eq__(semester),
                                               Mark.year.__eq__(year)).update({Mark.avg: avg},
                                                                              synchronize_session=False)
    db.session.commit()
    return result


def get_classes():
    return db.session.query(ClassRoom).all()


def total_qualified_by_class(class_id, semester, year, subject_id):
    count = db.session.query(func.count(Mark.avg)).\
        join(Student, Student.id.__eq__(Mark.student_id)).\
        join(ClassRoom, ClassRoom.id.__eq__(Student.class_id)).\
        filter(ClassRoom.id.__eq__(class_id),
               Mark.subject_id.__eq__(subject_id),
               Mark.semester.__eq__(semester),
               Mark.year.__eq__(year),
               Mark.avg.__ge__(5)).first()
    return count[0]


def get_subjects():
    return db.session.query(Subject.name)


def get_stats(semester, year, subject_name):
    classes = get_classes()
    stats = []
    subject_id = db.session.query(Subject.id).filter(Subject.name.__eq__(subject_name)).first()
    for c in classes:
        total_qualified = total_qualified_by_class(c.id, semester=semester, year=year, subject_id=subject_id[0])
        total = c.total if c.total else 0
        stats.append({
            'class_id': c.id,
            'class_name': c.grade + c.name,
            'total': total,
            'total_qualified': total_qualified,
            'ratio': "{0:.2f}".format((float(total_qualified) / total * 100) if total != 0 else 0 )
        })

    return stats


def get_teacher_id(user_id):
    return db.session.query(Teacher.id).filter(Teacher.user_id.__eq__(user_id))


def get_class_by_teacher_id(teacher_id):
    return db.session.query(Subject.name, ClassRoom.grade, ClassRoom.name, Course.id)\
            .join(Course, Course.subject_id.__eq__(Subject.id))\
            .join(ClassRoom, ClassRoom.id.__eq__(Course.class_id))\
            .filter(Course.teacher_id.__eq__(teacher_id)).all()

    # return TeacherSubjectClass.query.join(Subject, Subject.id.__eq__(TeacherSubjectClass.subject_id))\
    #         .join(ClassRoom, ClassRoom.id.__eq__(TeacherSubjectClass.class_id))\
    #         .add_columns(Subject.name, ClassRoom.grade, ClassRoom.name).all()


def get_course_info(course_id):
    return db.session.query(ClassRoom.grade, ClassRoom.name, Subject.name, Course.year)\
            .join(ClassRoom, ClassRoom.id.__eq__(Course.class_id))\
            .join(Subject, Subject.id.__eq__(Course.subject_id)).filter(Course.id.__eq__(course_id)).first()


def get_mark_by_course_id(course_id, semester=None):
    course = Course.query.get(course_id)
    # course = db.session.query(Course).filter(Course.id.__eq__(course_id)).first()
    if semester:
        students = get_students_mark(subject_id=course.subject_id,
                                     class_id=course.class_id,
                                     year=course.year,
                                     semester=semester)
    else:
        students = get_students_mark(subject_id=course.subject_id,
                                     class_id=course.class_id,
                                     year=course.year,
                                     semester=1)

    marks = []
    for s in students:
        marks.append({
            'student_name': s.Student.first_name + " " + s.Student.last_name,
            'mark15': [s.XVMark.col1, s.XVMark.col2, s.XVMark.col3, s.XVMark.col4, s.XVMark.col5],
            'mark45': [s.XXXXVMark.col1, s.XXXXVMark.col2, s.XXXXVMark.col3],
            'final_mark': s.FinalMark,
            'avg_mark': s.avg,
            'student_id': s.Student.id,
            'subject_id': s.Subject.id
        })

    return marks


def get_marks_of_student(subject_id, student_id, year, semester=None):
    records = db.session.query(Subject, Student,
                             Mark.semester, XVMark, XXXXVMark, Mark.FinalMark)\
                            .join(Subject, Subject.id.__eq__(Mark.subject_id))\
                            .join(Student, Student.id.__eq__(Mark.student_id))\
                            .join(XVMark, XVMark.id.__eq__(Mark.XV_mark_id), isouter=True)\
                            .join(XXXXVMark, XXXXVMark.id.__eq__(Mark.XXXXV_mark_id), isouter=True)\
                            .filter(Mark.subject_id.__eq__(subject_id),
                                    Mark.year.__eq__(year),
                                    Mark.student_id.__eq__(student_id))

    if semester:
        records = records.filter(Mark.semester.__eq__(semester))

    marks = []
    for r in records.all():
        marks.append({
            'subject': {
                'id': r.Subject.id,
                'name': r.Subject.name,
            },
            'student': {
                'id': r.Student.id,
                'name': r.Student.first_name + " " + r.Student.last_name,
            },
            'semester': r.semester,
            'mark15': [r.XVMark.col1, r.XVMark.col2, r.XVMark.col3, r.XVMark.col4, r.XVMark.col5],
            'mark45': [r.XXXXVMark.col1, r.XXXXVMark.col2, r.XXXXVMark.col3],
            'final_mark': r.FinalMark,
        })

    return marks


def update_marks(subject_id, student_id, year, mark15=None, mark45=None, final_mark=None):
    # record = db.session.query(XXXXVMark, XVMark, Mark.FinalMark)\
    #                     .join(XXXXVMark, XXXXVMark.id.__eq__(Mark.XXXXV_mark_id))\
    #                     .join(XVMark, XVMark.id.__eq__(Mark.XV_mark_id))\
    #                     .filter(Mark.subject_id.__eq__(subject_id),
    #                             Mark.student_id.__eq__(student_id),
    #                             Mark.year.__eq__(year))
    record = db.session.query(Mark.XV_mark_id, Mark.XXXXV_mark_id)\
                .filter(Mark.subject_id.__eq__(subject_id),
                        Mark.student_id.__eq__(student_id),
                        Mark.year.__eq__(year))

    # record_put = record.filter(Mark.semester.__eq__(1))
    if mark15['1'] or mark45['1']:
        record_put = record.filter(Mark.semester.__eq__(1)).first() # xvmark_id, xxxxvmark_id cuar hoc ky 1
        # Lay ra 2 id cua xvmark voi xxxxvmark trong Mark vi tri [0] la id cua xvmark, [1] la id cua xxxxvmark

        db.session.query(XVMark).filter(XVMark.id.__eq__(record_put[0]))\
            .update({XVMark.col1: mark15['1'][0] if mark15['1'][0] != '' else null(),
                     XVMark.col2: mark15['1'][1] if mark15['1'][1] != '' else null(),
                     XVMark.col3: mark15['1'][2] if mark15['1'][2] != '' else null(),
                     XVMark.col4: mark15['1'][3] if mark15['1'][3] != '' else null(),
                     XVMark.col5: mark15['1'][4] if mark15['1'][4] != '' else null()},
                    synchronize_session=False)

        db.session.query(XXXXVMark).filter(XXXXVMark.id.__eq__(record_put[1])) \
            .update({XXXXVMark.col1: mark45['1'][0] if mark45['1'][0] != '' else null(),
                     XXXXVMark.col2: mark45['1'][1] if mark45['1'][1] != '' else null(),
                     XXXXVMark.col3: mark45['1'][2] if mark45['1'][2] != '' else null()},
                    synchronize_session=False)

    if mark15['2'] or mark45['2']:
        pass
        record_put = record.filter(Mark.semester.__eq__(2)).first() # xvmark_id, xxxxvmark_id cuar hoc ky 2
        # Lay ra 2 id cua xvmark voi xxxxvmark trong Mark vi tri [0] la id cua xvmark, [1] la id cua xxxxvmark
        print(record_put)

        db.session.query(XVMark).filter(XVMark.id.__eq__(record_put[0])) \
            .update({XVMark.col1: mark15['2'][0] if mark15['2'][0] != '' else null(),
                     XVMark.col2: mark15['2'][1] if mark15['2'][1] != '' else null(),
                     XVMark.col3: mark15['2'][2] if mark15['2'][2] != '' else null(),
                     XVMark.col4: mark15['2'][3] if mark15['2'][3] != '' else null(),
                     XVMark.col5: mark15['2'][4] if mark15['2'][4] != '' else null()},
                    synchronize_session=False)

        db.session.query(XXXXVMark).filter(XXXXVMark.id.__eq__(record_put[1])) \
            .update({XXXXVMark.col1: mark45['2'][0] if mark45['2'][0] != '' else null(),
                     XXXXVMark.col2: mark45['2'][1] if mark45['2'][1] != '' else null(),
                     XXXXVMark.col3: mark45['2'][2] if mark45['2'][2] != '' else null()},
                    synchronize_session=False)

    db.session.commit()
    return record_put


# Tu day tro xuong la de test = console
# a = get_mark_by_course_id(1)
# cal_avg_mark(subject_id=1, year=2021, semester=1)
# a = get_students_mark(class_id=2, semester=1, year=2021, subject_id=1)
# a = get_marks_of_student(subject_id=1, student_id=6, year=2021)
# a = update_marks(1, 6, 2021)
# print(a)