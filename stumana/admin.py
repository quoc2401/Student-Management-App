from stumana import app, db, utilities
from flask_admin.contrib.sqla import ModelView
from models import Account, Student, ClassRoom, Subject
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask import request


admin = Admin(app=app, name='Quản trị Trường THPT', template_mode='bootstrap4')


class ModalModelView(ModelView):
    create_modal = True
    edit_modal = True
    edit_modal = True


class SubjectModelView(ModalModelView):
    column_searchable_list = ['name']
    column_filters = ['name']
    column_labels = {
        'id': 'Mã môn học',
        'name': 'Tên môn học'
    }


class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render("admin/index.html")


class ChangeRule(BaseView):
    @expose("/")
    def __index__(self):
        return self.render("admin/change-rule.html",
                           min_age=app.config['MIN_AGE'],
                           max_age=app.config['MAX_AGE'])


admin.add_view(ModalModelView(Account, db.session, name='Tài khoản'))
admin.add_view(ModalModelView(Student, db.session, name='Học sinh'))
admin.add_view(ModalModelView(ClassRoom, db.session, name='Lớp học'))
admin.add_view(SubjectModelView(Subject, db.session, name='Môn học'))
admin.add_view(ChangeRule(name="Thay đổi quy định"))

