from stumana import db
from sqlalchemy import text, func
from stumana.models import User, Student, Mark, Subject, XVMark, XXXXVMark, ClassRoom
import config, numpy


# Dang nhap
def get_user_by_id(account_id):
    return User.query.get(account_id)


def check_login(username, password):
    # password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()

<<<<<<< HEAD
# aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
=======
>>>>>>> 1bc128d50d6bd12609498f0d78971c2dd4c58714

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

        max = int(max)
        _max_age = str(max + 1)
        drop_max = "CALL PROC_DROP_CHECK_CONSTRAINT('student', 'chk_age2');"
        add_max = "CALL PROC_ADD_CHECK_CONSTRAINT('student', 'chk_age2'," \
                  " '(YEAR(join_date) - YEAR(bday)) < " + _max_age + "');"
        db.engine.execute(text(drop_max))
        db.engine.execute(text(add_max))
        config.min_age = min
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


def get_students_mark(class_id):
    students = db.session.query(Subject, Student, Mark.semester, Mark.year, XVMark, XXXXVMark, Mark.FinalMark)\
                                .join(Mark, Mark.subject_id.__eq__(Subject.id))\
                                .join(Student, Student.id.__eq__(Mark.student_id))\
                                .join(XVMark, XVMark.id.__eq__(Mark.XV_mark_id), isouter=True)\
                                .join(XXXXVMark, XXXXVMark.id.__eq__(Mark.XXXXV_mark_id), isouter=True)

    if class_id:
        students = students.filter(Student.class_id.__eq__(class_id))

    d = {}
    for s in students:
        d[str(s.Student.id)] = {
            'subject_id': s.Subject.id,
            'semester': s.semester,
            'year': s.year,
            'mark15': average_ignore_none([s.XVMark.col1, s.XVMark.col2, s.XVMark.col3, s.XVMark.col4, s.XVMark.col5])
            if s.XVMark else 0,
            'mark45': average_ignore_none([s.XXXXVMark.col1, s.XXXXVMark.col2, s.XXXXVMark.col3])
            if s.XXXXVMark else 0,
            'final_mark': s.FinalMark if s.FinalMark else 0
        }

    # return students.all()
    return d


def average_ignore_none(numbers):
    total = []
    for n in numbers:
        if n:
            total.append(n)
    avg = sum(total) / len(total)
    return avg


# Tu day tro xuong la de test = console
# change_chk_age(15, 20)
# print(config.min_age)
a = get_students_mark(1)
print(a)
#
# import numpy.ma as ma
# a = ma.array([7, None, None, None, None], mask=[0, 1, 1, 1, 1])
# print("average =", ma.average(a))