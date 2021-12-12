from stumana import app, db, utilities
from flask_admin.contrib.sqla import ModelView
from stumana.models import User, Student, ClassRoom, Subject, Teacher, Staff, UserRole
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_login import current_user, logout_user
from flask import redirect, request
import config
from datetime import datetime


admin = Admin(app=app, name='Quản trị Trường THPT', template_mode='bootstrap4')


class AuthenticatedBaseView(BaseView):
    def __index__(self):
        return current_user.is_authenticated


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class StaffBaseView(AuthenticatedBaseView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.user_role == UserRole.STAFF or current_user.user_role == UserRole.ADMIN


class AdminBaseView(AuthenticatedBaseView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.user_role == UserRole.ADMIN


class ModalModelView(AuthenticatedModelView):
    create_modal = True
    edit_modal = True


class SubjectModelView(ModalModelView):
    column_searchable_list = ['name']
    column_filters = ['name']
    column_labels = {
        'id': 'Mã môn học',
        'name': 'Tên môn học'
    }


class CustomPersonForm(ModalModelView):
    form_excluded_columns = ['user', 'classroom', 'classes']


class CustomUserForm(ModalModelView):
    form_excluded_columns = ['student', 'teacher', 'staff']


class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render("admin/index.html")


class ChangeRule(AdminBaseView):
    @expose("/")
    def __index__(self):
        return self.render("admin/change-rule.html",
                           min_age=config.min_age,
                           max_age=config.max_age,
                           max_size=config.max_size,)


class UserAllocation(AdminBaseView):    # de lam sau
    @expose("/")
    def __index__(self):
        return self.render("admin/index.html")


class StatsView(StaffBaseView):
    @expose('/')
    def index(self):
        subject_name = request.args.get("subject", "Toán 11")
        semester = request.args.get("semester", "1")
        year = request.args.get("year", datetime.now().year)
        stats = utilities.get_stats(subject_name=subject_name,
                                    semester=semester,
                                    year=year)

        return self.render("admin/stats.html",
                           stats=stats)


class SetUpClass(StaffBaseView):    # de lam sau
    @expose("/")
    def __index__(self):
        return self.render("admin/index.html")


# class StatsView(StaffBaseView):
#     @expose('/')
#     def __index__(self):
#         stats = utilities.student_count_by_class()
#         return self.render('admin/stats.html', stats=stats)


class LogoutView(BaseView):
    @expose('/')
    def __index__(self):
        logout_user()
        return redirect("/admin")

    def is_accessible(self):
        return current_user.is_authenticated


admin.add_view(CustomUserForm(User, db.session, name='Quản lý tài khoản', category="Tài khoản",
                              menu_icon_type='fa', menu_icon_value='fa-users'))
admin.add_view(UserAllocation(name="Cấp tài khoản", category="Tài khoản",
                              menu_icon_type='fa', menu_icon_value='fa-id-card'))
admin.add_view(CustomPersonForm(Student, db.session, name='Học sinh', category="Cá nhân",
                                menu_icon_type='fa', menu_icon_value='fa-graduation-cap'))
admin.add_view(CustomPersonForm(Teacher, db.session, name='Giáo viên', category="Cá nhân",
                                menu_icon_type='fa', menu_icon_value='fa-podcast'))
admin.add_view(CustomPersonForm(Staff, db.session, name='Nhân viên', category="Cá nhân",
                                menu_icon_type='fa', menu_icon_value='fa-briefcase'))

admin.add_view(ModalModelView(ClassRoom, db.session, name='Quản lý lớp học',
                              menu_icon_type='fa', menu_icon_value='fa-columns', category="Lớp học"))
admin.add_view(SetUpClass(name="Lập danh sách lớp", menu_icon_type='fa',
                          menu_icon_value='fa-reorder', category="Lớp học"))
admin.add_view(SubjectModelView(Subject, db.session, name='Môn học',
                                menu_icon_type='fa', menu_icon_value='fa-book'))
admin.add_view(ChangeRule(name="Thay đổi quy định", menu_icon_type='fa', menu_icon_value='fa-gear'))
admin.add_view(StatsView(name='Thống kê báo cáo', menu_icon_type='fa', menu_icon_value='fa-line-chart'))

admin.add_view(LogoutView(name="Đăng xuất", menu_icon_type='fa', menu_icon_value='fa-sign-out'))
