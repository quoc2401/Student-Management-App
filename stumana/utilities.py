from stumana import db


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
