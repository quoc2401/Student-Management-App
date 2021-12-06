from flask_admin.menu import MenuLink
from stumana import app, db, utilities
from flask_admin.contrib.sqla import ModelView
from models import Account, Student, ClassRoom, Subject, Teacher, Staff
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


class CustomPersonForm(ModalModelView):
    form_excluded_columns = ['account']


class CustomAccountForm(ModalModelView):
    form_excluded_columns = ['student', 'teacher', 'staff']


class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render("admin/index.html")


class ChangeRule(BaseView):
    @expose("/")
    def __index__(self):
        return self.render("admin/change-rule.html",
                           min_age=app.config['MIN_AGE'],
                           max_age=app.config['MAX_AGE'],
                           max_size=app.config['MAX_SIZE'])


class UserAllocation(BaseView):
    @expose("/")
    def __index__(self):
        return self.render("admin/index.html")


admin.add_view(CustomAccountForm(Account, db.session, name='Quản lý tài khoản', category="Tài khoản",
                                 menu_icon_type='fa', menu_icon_value='fa-users'))
admin.add_view(UserAllocation(name="Cấp tài khoản", category="Tài khoản",
                              menu_icon_type='fa', menu_icon_value='fa-id-card'))
admin.add_view(CustomPersonForm(Student, db.session, name='Học sinh', category="Cá nhân",
                                menu_icon_type='fa', menu_icon_value='fa-graduation-cap'))
admin.add_view(CustomPersonForm(Teacher, db.session, name='Giáo viên', category="Cá nhân",
                                menu_icon_type='fa', menu_icon_value='fa-podcast'))
admin.add_view(CustomPersonForm(Staff, db.session, name='Nhân viên', category="Cá nhân",
                                menu_icon_type='fa', menu_icon_value='fa-briefcase'))
# admin.add_sub_category(name="Nhân viên", parent_name="Cá nhân")
admin.add_view(ModalModelView(ClassRoom, db.session, name='Lớp học',
                              menu_icon_type='fa', menu_icon_value='fa-columns'))
admin.add_view(SubjectModelView(Subject, db.session, name='Môn học',
                                menu_icon_type='fa', menu_icon_value='fa-book'))
admin.add_view(ChangeRule(name="Thay đổi quy định", menu_icon_type='fa', menu_icon_value='fa-gear'))

admin.add_link(MenuLink(name='Trang chủ', url='/', category='Links'))


