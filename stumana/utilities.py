from stumana import db
from sqlalchemy import text, func, update
from stumana.models import User, Student, Mark, Subject, XVMark, XXXXVMark, ClassRoom
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


def student_count_by_class(class_id):
    return db.session.query(func.count(Student.id))\
        .join(ClassRoom, ClassRoom.id.__eq__(Student.class_id))\
        .filter(ClassRoom.id.__eq__(class_id)).all()
    # return ClassRoom.query.join(Student, Student.class_id.__eq__(ClassRoom.id), isouter=True)\
    #     .add_columns(func.count(Student.id)).group_by(ClassRoom.id).all()


def get_students_mark(class_id=None, semester=None, year=None, subject_id=None):
    students = db.session.query(Subject, Student, Mark.semester, Mark.year, XVMark, XXXXVMark, Mark.FinalMark)\
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
    # d = {}
    # for s in students:
    #     d[str(s.Student.id)] = {
    #         'subject_id': s.Subject.id,
    #         'semester': s.semester,
    #         'year': s.year,
    #         'mark15': average_ignore_none([s.XVMark.col1, s.XVMark.col2, s.XVMark.col3, s.XVMark.col4, s.XVMark.col5])
    #         if s.XVMark else 0,
    #         'mark45': average_ignore_none([s.XXXXVMark.col1, s.XXXXVMark.col2, s.XXXXVMark.col3])
    #         if s.XXXXVMark else 0,
    #         'final_mark': s.FinalMark if s.FinalMark else 0
    #     }

    return students.all()
    # return d


def average_ignore_none(numbers):
    total = []
    for n in numbers:
        if n:
            total.append(n)
    avg = sum(total) / len(total)
    return avg


def get_student_by_class(class_id):
    return Student.query.filter(Student.class_id.__eq__(class_id)).all()


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
                                            Mark.year.__eq__(year)).\
            update({Mark.avg: avg}, synchronize_session=False)
        print(result)
    db.session.commit()


def get_classes():
    return db.session.query(ClassRoom).all()


def total_qualifed_by_class(class_id, semester, year, subject_id):
    count = db.session.query(func.count(Mark.avg)).\
        join(Student, Student.id.__eq__(Mark.student_id)).\
        join(ClassRoom, ClassRoom.id.__eq__(Student.class_id)).\
        filter(ClassRoom.id.__eq__(class_id),
               Mark.subject_id.__eq__(subject_id),
               Mark.subject_id.__eq__(semester),
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
        total_qualified = total_qualifed_by_class(c.id, semester=semester, year=year, subject_id=subject_id[0])
        stats.append({
            'class_id': c.id,
            'class_name': c.grade + c.name,
            'total': c.total,
            'total_qualified': total_qualified,
            'ratio': "{0:.2f}".format(float(total_qualified) / c.total * 100)
        })

    return stats

# Tu day tro xuong la de test = console
# a = get_stats(semester=2, year=2020, subject_name='Toán 10')
# print(a)