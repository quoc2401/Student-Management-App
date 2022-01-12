from flask_admin.babel import gettext
from flask_admin.form import FormOpts
from stumana import app, db, utilities
from flask_admin.contrib.sqla import ModelView
from stumana.models import User, Student, ClassRoom, Subject, Teacher, Staff, UserRole, Course
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_login import current_user, logout_user
from flask import redirect, request
from stumana import config
from datetime import datetime


class AuthenticatedBaseView(BaseView):
    def __index__(self):
        return current_user.is_authenticated


class AuthenticatedModelView(ModelView):
    page_size = 10
    create_modal = True
    edit_modal = True
    column_display_all_relations = True
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
        'user': 'Tài khoản',
        'classroom': 'Lớp',
        'name': 'Tên người dùng',
        'username': 'Tài khoản',
        'password': 'Mật khẩu',
        'avatar': 'Ảnh đại diện',
        'user_role': 'Chức vụ',
        'classes': 'Các lớp phụ trách',
        'teacher': 'Giáo viên',
        'class_room': 'Lớp',
        'student': 'Học sinh',
        'staff': 'Nhân viên',
        'subject': 'Môn',
        'year': 'Năm',
        'course': 'Khóa học'
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class PersonView(AuthenticatedModelView):
    column_searchable_list = ['first_name', 'last_name']


class TeacherView(PersonView):
    column_exclude_list = ['course', 'classes']
    form_excluded_columns = ['course', 'classes']


class AdminBaseView(AuthenticatedBaseView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.user_role == UserRole.ADMIN


class UserView(AuthenticatedModelView):
    column_display_all_relations = False
    column_searchable_list = ['name', 'username']


class ClassModalView(AuthenticatedModelView):
    column_exclude_list = ['course', 'teacher']
    form_excluded_columns = ['course', 'teacher', 'total']
    column_labels = {
        'grade': 'Khối',
        'name': 'Tên lớp',
        'total': 'Sỉ số',
        'students': 'Các học sinh trong lớp'
    }


class SubjectModelView(AuthenticatedModelView):
    column_exclude_list = ['course']
    form_excluded_columns = ['course']
    column_searchable_list = ['name']
    column_filters = ['name']
    column_labels = {
        'id': 'Mã môn học',
        'name': 'Tên môn học'
    }


class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        count_student = utilities.count_student()
        count_classroom = utilities.count_classroom()
        count_staff = utilities.count_staff()
        count_teacher = utilities.count_teacher()

        return self.render("admin/index.html",
                           count_student=count_student,
                           count_classroom=count_classroom,
                           count_staff=count_staff,
                           count_teacher=count_teacher)


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


# class Student(ModalModelView):
#     def is_accessible(self):
#         if current_user.is_authenticated:
#             return current_user.user_role == UserRole.STAFF


class StatsView(AdminBaseView):
    @expose('/')
    def __index__(self):
        subject_name = request.args.get("subject", "Toán 10")
        semester = request.args.get("semester", "1")
        year = request.args.get("year", 2021)
        if subject_name and semester and year:
            stats = utilities.get_stats(subject_name=subject_name,
                                        semester=semester,
                                        year=year)

            return self.render("admin/stats.html",
                               stats=stats,
                               subjects=utilities.get_subjects())
        return self.render("admin/stats.html", subjects=utilities.get_subjects())


class SetUpClass(AdminBaseView):
    @expose('/')
    def __index__(self):
        return redirect("/setup-class")


class ArrangeClass(AdminBaseView):
    @expose('/')
    def __index__(self):
        return redirect("/arrange-class")


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
admin.add_view(UserView(User, db.session,
                        name='Tài khoản',
                        menu_icon_type='fa',
                        menu_icon_value='fa-users'))
# Staff
admin.add_view(PersonView(Student, db.session,
                                      name='Học sinh',
                                      category="Cá nhân",
                                      menu_icon_type='fa',
                                      menu_icon_value='fa-graduation-cap'))
# Staff
# admin.add_view(Change_class(Student, db.session,
#                             name='Điều chỉnh lớp học',
#                             category="Lớp học"))
# Admin
admin.add_view(TeacherView(Teacher, db.session,
                                      name='Giáo viên',
                                      category="Cá nhân",
                                      menu_icon_type='fa',
                                      menu_icon_value='fa-podcast'))
# Admin
admin.add_view(PersonView(Staff, db.session,
                                      name='Nhân viên',
                                      category="Cá nhân",
                                      menu_icon_type='fa',
                                      menu_icon_value='fa-briefcase'))
# Admin
admin.add_view(ClassModalView(ClassRoom, db.session,
                              name='Quản lý lớp học',
                              menu_icon_type='fa',
                              menu_icon_value='fa-columns',
                              category="Lớp học"))
# Staff
admin.add_view(ArrangeClass(name='Xếp lớp',
                            menu_icon_type='fa',
                            menu_icon_value='fa-reorder',
                            category="Lớp học"))
# Staff
admin.add_view(SetUpClass(name="Lập danh sách lớp",
                          menu_icon_type='fa',
                          menu_icon_value='fa-reorder',
                          category="Lớp học"))

admin.add_view(AuthenticatedModelView(Course, db.session,
                                      name='Quản lý khóa học',
                                      menu_icon_type='fa',
                                      menu_icon_value='fa-book',
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
                          menu_icon_value='fa-sign-out'))
