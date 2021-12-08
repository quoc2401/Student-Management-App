from stumana import db
from sqlalchemy import text
from stumana.models import User
import config


# Dang nhap
def get_user_by_id(account_id):
    return User.query.get(account_id)


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


# change_chk_age(15, 20)
# print(config.min_age)