from stumana import db
from sqlalchemy import Column, String, Integer, DATETIME, ForeignKey, Enum, Boolean, Float, CheckConstraint
from datetime import datetime
from sqlalchemy.orm import relationship, backref
from enum import Enum as UserEnum


class UserRole(UserEnum):
    ADMIN = 0
    STAFF = 1
    TEACHER = 2
    STUDENT = 3


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, autoincrement=True, primary_key=True)


class Account(BaseModel):
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    user_role = Column(Enum(UserRole), nullable=False)
    student = relationship('Student', backref='account', lazy=True)
    teacher = relationship('Teacher', backref='account', lazy=True)
    staff = relationship('Staff', backref='account', lazy=True)

    def __str__(self):
        return self.name


class Ethnic(BaseModel):
    name = Column(String(20), nullable=False)


class Person(BaseModel):
    __abstract__ = True

    first_name = Column(String(20), nullable=False)
    last_name = Column(String(20), nullable=False)
    bday = Column(DATETIME, nullable=False)
    sex = Column(Boolean, default=True)
    address = Column(String(100))
    phone = Column(String(15))
    email = Column(String(50))
    join_date = Column(DATETIME, default=datetime.now())
    active = Column(Boolean, default=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class ClassRoom(BaseModel):
    grade = Column(String(5), nullable=False)
    name = Column(String(10), nullable=False)
    total = Column(Integer, default=0)
    students = relationship('Student', backref='classroom', lazy=False)

    def __str__(self):
        return self.name


class Student(Person):
    __table_args__ = (
        CheckConstraint('(year(join_date) - year(bday)) > 14', name='chk_age1'),
        CheckConstraint('(year(join_date) - year(bday)) < 21', name='chk_age2')
    )

    ethnic_id = Column(Integer, ForeignKey(Ethnic.id))
    account_id = Column(Integer, ForeignKey(Account.id), unique=True)
    class_id = Column(Integer, ForeignKey(ClassRoom.id))


class Teacher(Person):
    ethnic_id = Column(Integer, ForeignKey(Ethnic.id))
    account_id = Column(Integer, ForeignKey(Account.id), unique=True)
    classes = relationship('ClassRoom', secondary='teacher_subject_class', lazy='subquery',
                           backref=backref('teacher', lazy=True))


class Staff(Person):
    ethnic_id = Column(Integer, ForeignKey(Ethnic.id))
    account_id = Column(Integer, ForeignKey(Account.id), unique=True)


# mon hoc
class Subject(BaseModel):
    name = Column(String(20), nullable=False)


# 1 giao vien day nhieu lop, 1 lop co nhieu giao vien
class TeacherSubjectClass(db.Model):
    __tablename__ = 'teacher_subject_class'

    teacher_id = Column(Integer, ForeignKey(Teacher.id), nullable= False, primary_key=True)
    class_id = Column(Integer, ForeignKey(ClassRoom.id), nullable=False, primary_key=True)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)


# diem 15p
class XVMark(BaseModel):
    col1 = Column(Float)
    col2 = Column(Float)
    col3 = Column(Float)
    col4 = Column(Float)
    col5 = Column(Float)
    mark = relationship('Mark', backref='xvmark', lazy=True)


# diem 45p
class XXXXVMark(BaseModel):
    col1 = Column(Float)
    col2 = Column(Float)
    col3 = Column(Float)
    mark = relationship('Mark', backref='xxxxvmark', lazy=True)


# bang diem cua 1 hoc sinh trong mot hoc ky cua 1 nam
class Mark(db.Model):
    subject_id = Column(Integer, ForeignKey(Subject.id), primary_key=True)
    student_id = Column(Integer, ForeignKey(Student.id), primary_key=True)
    semester = Column(Integer, primary_key=True)
    year = Column(Integer, primary_key=True)
    XV_mark_id = Column(Integer, ForeignKey(XVMark.id))
    XXXXV_mark_id = Column(Integer, ForeignKey(XXXXVMark.id))
    FinalMark = Column(Float)


if __name__ == '__main__':
    # db.drop_all()
    db.create_all()
