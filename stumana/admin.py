from stumana import app, db, utilities
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from stumana.models import Account, Student, ClassRoom, Subject, Mark, UserRole, XVMark
from flask_login import logout_user, current_user
from flask import redirect



# Quyen admin
class AuthenticatedAminModelView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_rode == UserRole.ADMIN


class ModalModelView(ModelView):
    column_display_pk = True
    create_modal = True
    edit_modal = True


class SubjectModelView(ModalModelView):
    column_searchable_list = ['name']
    # column_filters = ['name']
    column_labels = {
        'id': 'Mã môn học',
        'name': 'Tên môn học'
    }


class MarkModelView(ModalModelView):
    column_labels = {
        'semester': 'hoc ki',
        'year': 'nam hoc',
        'FinalMark': 'Diem tb nam'

    }


class LogoutView(BaseView):
    @expose('/')
    def __index__(self):
        logout_user()

        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated


class StatsView(ModalModelView):
    @expose('/')
    def __index__(self):
        stats = utilities.student_count_by_class()
        return self.render('admin/stats.html', stats=stats)

    def is_accessible(self):
        return current_user.is_authenticated


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def __index__(self):
        return self.render('admin/index.html', stats=utilities.student_count_by_class())


admin = Admin(app=app, name='Quản trị Trường THPT', template_mode='bootstrap4', index_view=MyAdminIndexView())


admin.add_view(ModalModelView(Account, db.session, name='Tài khoản'))
admin.add_view(ModalModelView(Student, db.session, name='Học sinh'))
admin.add_view(ModalModelView(ClassRoom, db.session, name='Lớp học'))
admin.add_view(SubjectModelView(Subject, db.session, name='Môn học'))
admin.add_view(MarkModelView(Mark, db.session, name='Nhap diem'))
admin.add_views(StatsView(XVMark, db.session, name='Thong ke bao cao'))
admin.add_view(LogoutView(name='Dang Xuat'))
