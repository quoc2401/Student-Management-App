from stumana import db, app
from sqlalchemy import text


def get_constraints():
    sql = ''
    return sql;


# Thay doi tuoi quy dinh
def change_chk_age(min_age=None, max_age=None):
    errmsg = ''
    if min_age:
        app.config['MIN_AGE'] = min_age
    if max_age:
        app.config['MAX_AGE'] = max_age
    _min_age = str(app.config['MIN_AGE'] - 1)
    _max_age = str(app.config['MAX_AGE'] + 1)

    drop_min = "CALL PROC_DROP_CHECK_CONSTRAINT('student', 'chk_age1');"
    add_min = "CALL PROC_ADD_CHECK_CONSTRAINT('student', 'chk_age1'," \
              " '(YEAR(join_date) - YEAR(bday)) > " + _min_age + "');"

    drop_max = "CALL PROC_DROP_CHECK_CONSTRAINT('student', 'chk_age2');"
    add_max = "CALL PROC_ADD_CHECK_CONSTRAINT('student', 'chk_age2'," \
              " '(YEAR(join_date) - YEAR(bday)) < " + _max_age + "');"

    try:
        result1 = db.engine.execute(text(drop_min))
        result2 = db.engine.execute(text(add_min))
        result3 = db.engine.execute(text(drop_max))
        result4 = db.engine.execute(text(add_max))
        errmsg = 'min = ' + _min_age + 'max = ' + _max_age
    except Exception as e:
        errmsg = e

    return errmsg


# test
