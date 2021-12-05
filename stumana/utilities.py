from stumana import db, app
from sqlalchemy import text


# Thay doi tuoi quy dinh
def change_chk_age(min_age=None, max_age=None):
    errmsg = ''

    if min_age:
        app.config['MIN_AGE'] = int(min_age)
    if max_age:
        app.config['MAX_AGE'] = int(max_age)
    _min_age = str(app.config['MIN_AGE'] - 1)
    _max_age = str(app.config['MAX_AGE'] + 1)

# tao cau lenh sql
    drop_min = "CALL PROC_DROP_CHECK_CONSTRAINT('student', 'chk_age1');"
    add_min = "CALL PROC_ADD_CHECK_CONSTRAINT('student', 'chk_age1'," \
              " '(YEAR(join_date) - YEAR(bday)) > " + _min_age + "');"
    drop_max = "CALL PROC_DROP_CHECK_CONSTRAINT('student', 'chk_age2');"
    add_max = "CALL PROC_ADD_CHECK_CONSTRAINT('student', 'chk_age2'," \
              " '(YEAR(join_date) - YEAR(bday)) < " + _max_age + "');"

    try:
        db.engine.execute(text(drop_min))
        db.engine.execute(text(add_min))
        db.engine.execute(text(drop_max))
        db.engine.execute(text(add_max))
        errmsg = 'min = ' + str(app.config['MIN_AGE']) + 'max = ' + str(app.config['MAX_AGE'])
    except Exception as e:
        errmsg = e

    return errmsg


# thay doi si so toi da
def change_max_size(max_size=None):
    errmsg=''

    if max_size:
        app.config['MAX_SIZE'] = int(max_size)

    _max_size = str(app.config['MAX_SIZE'])

# tao cau lenh sql
    drop_trigger = "drop trigger if exists before_enter_class;"
    create_trigger = " create trigger before_enter_class after update on class_room for each row"\
        " begin declare new_size int; set new_size = (select total from class_room"\
        " where new.id = id); if new_size >= (" + _max_size + " + 1) then"\
        " signal sqlstate '45001' set message_text = 'Vuot qua so luong toi da'; end if; end;"

    try:
        db.engine.execute(text(drop_trigger))
        db.engine.execute(create_trigger)
        errmsg = str(app.config['MAX_SIZE'])
    except Exception as e:
        errmsg = e

    return errmsg