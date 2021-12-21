from stumana import app, db, utilities
from flask_admin.contrib.sqla import ModelView
from stumana.models import User, Student, ClassRoom, Subject, Teacher, Staff, UserRole
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_login import current_user, logout_user
from flask import redirect, request
import config
from datetime import datetime


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
    column_labels = {
        'first_name': 'Họ',
        'last_name': 'Tên',
        'bday': 'Ngày sinh',
        'sex': 'Giới tính',
        'address': 'Địa chỉ',
        'phone': 'SĐT',
        'email': 'Email',
        'join_date': 'Ngày gia nhập',
        'active': 'Active',
        'user': 'Tên tài khoản',
        'classroom': 'Lớp',
        'grade': 'Khối',
        'total': 'Sỉ số',
        'class_name': 'Tên lớp',
        'name': 'Tên người dùng',
        'username': 'Tài khoản',
        'password': 'Mật khẩu',
        'avatar': 'Ảnh đại diện',
        'user_role': 'Chức vụ'
    }


class SubjectModelView(ModalModelView):
    column_searchable_list = ['subject_name']
    column_filters = ['subject_name']
    column_labels = {
        'id': 'Mã môn học',
        'subject_name': 'Tên môn học'
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
                           max_size=config.max_size)

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.user_role == UserRole.ADMIN


class UserAllocation(AdminBaseView):    # de lam sau
    @expose("/")
    def __index__(self):
        return self.render("admin/index.html")

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.user_role == UserRole.ADMIN


class Accept_student(ModalModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.user_role == UserRole.STAFF


class StatsView(AdminBaseView):
    @expose('/')
    def index(self):
        subject_name = request.args.get("subject", "Toán")
        semester = request.args.get("semester", "1")
        year = request.args.get("year", datetime.now().year)
        stats = utilities.get_stats(subject_name=subject_name,
                                    semester=semester,
                                    year=year)

        return self.render("admin/stats.html",
                           stats=stats,
                           subjects=utilities.get_subjects())


class SetUpClass(StaffBaseView):    # de lam sau
    @expose("/")
    def index(self):
        err_msg = ""
        grade = request.args.get('grade', '12')
        class_name = request.args.get('class', 'A1')
        students = utilities.get_student_by_class(grade=grade,
                                                  class_name=class_name)

        if students:
            return self.render("admin/class-list.html",
                               classes=utilities.get_classes(),
                               students=students,
                               total=utilities.get_total(grade=grade,
                                                         class_name=class_name))
        else:
            error_msg = "Lớp không tồn tại hoặc không có học sinh nào!!!"

        return self.render("admin/class-list.html",
                           classes=utilities.get_classes(),
                           students=students,
                           total=utilities.get_total(grade=grade,
                                                     class_name=class_name),
                           error_msg=error_msg)


class LogoutView(BaseView):
    @expose('/')
    def __index__(self):
        logout_user()
        return redirect("/")

    def is_accessible(self):
        return current_user.is_authenticated


admin = Admin(app=app, name='Quản trị Trường THPT',
              template_mode='bootstrap4',
              index_view=MyAdminIndexView())
admin.add_view(CustomUserForm(User, db.session,
                              name='Quản lý tài khoản',
                              category="Tài khoản",
                              menu_icon_type='fa',
                              menu_icon_value='fa-users'))
admin.add_view(UserAllocation(name="Cấp tài khoản",
                              category="Tài khoản",
                              menu_icon_type='fa',
                              menu_icon_value='fa-id-card'))
# Staff
admin.add_view(Accept_student(Student, db.session,
                              name='Tiếp nhận học sinh',
                              menu_icon_type='fa',
                              menu_icon_value='fa-graduation-cap'))
# Staff
# admin.add_view(Change_class(Student, db.session,
#                             name='Điều chỉnh lớp học',
#                             category="Lớp học"))
# Admin
admin.add_view(CustomPersonForm(Teacher, db.session,
                                name='Giáo viên',
                                category="Cá nhân",
                                menu_icon_type='fa',
                                menu_icon_value='fa-podcast'))
# Admin
admin.add_view(CustomPersonForm(Staff, db.session,
                                name='Nhân viên',
                                category="Cá nhân",
                                menu_icon_type='fa',
                                menu_icon_value='fa-briefcase'))
# Admin
admin.add_view(ModalModelView(ClassRoom, db.session,
                              name='Quản lý lớp học',
                              menu_icon_type='fa',
                              menu_icon_value='fa-columns',
                              category="Lớp học"))
# Staff
# admin.add_view(Change_class(Student, db.session,
#                             menu_icon_type='fa',
#                             menu_icon_value='fa-graduation-cap',
#                             category="Lớp học"))
# Staff
admin.add_view(SetUpClass(name="Lập danh sách lớp",
                          menu_icon_type='fa',
                          menu_icon_value='fa-reorder',
                          category="Lớp học"))
# Admin
admin.add_view(SubjectModelView(Subject, db.session,
                                name='Môn học',
                                menu_icon_type='fa',
                                menu_icon_value='fa-book'))
# Admin
admin.add_view(ChangeRule(name="Thay đổi quy định",
                          menu_icon_type='fa',
                          menu_icon_value='fa-gear'))
# Admin
admin.add_view(StatsView(name='Thống kê báo cáo',
                         menu_icon_type='fa',
                         menu_icon_value='fa-line-chart'))

admin.add_view(LogoutView(name="Đăng xuất",
                          menu_icon_type='fa',
                          menu_icon_value='fa-sign-out-alt'))
