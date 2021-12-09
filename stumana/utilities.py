from stumana import db
from stumana.models import Account, ClassRoom, Student
from sqlalchemy import func

#import hashlib


def get_user_by_id(user_id):
    return Account.query.get(user_id)


def check_login(username, password):
    if username and password:
       # password = str(hashlib.mb5(password.strip().encode('utf8')).hexdigest()) #(ma bam pass)
        return Account.query.filter(Account.username.__eq__(username.strip()),
                                    Account.password.__eq__(password)).first()


# join bang
def student_count_by_class():
    return ClassRoom.query.join(Student, Student.class_id.__eq__(ClassRoom.id), isouter=True)\
        .add_columns(func.count(Student.id)).group_by(ClassRoom.id).all()


# Thay doi tuoi quy dinh
def change_chk_age(min_age=15, max_age=20):
    change_min = 'ALTER TABLE student DROP CONSTRAINT chk_age1;' \
                 ' ALTER TABLE student ADD CONSTRAINT chk_age1' \
                 ' CHECK((YEAR(join_date) - YEAR(bday)) > ' + str(min_age - 1) + ')'
    change_max = 'ALTER TABLE student DROP CONSTRAINT chk_age2;' \
                 ' ALTER TABLE student ADD CONSTRAINT chk_age2' \
                 ' CHECK((YEAR(join_date) - YEAR(bday)) < ' + str(max_age + 1) + ')'
    result1 = db.engine.execute(change_min)
    result2 = db.engine.execute(change_max)

    return result1 + ' ' + result2


# test
# result = change_chk_age(min_age=10, max_age=30)
# print(result)
