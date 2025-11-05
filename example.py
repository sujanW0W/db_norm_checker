from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session, declarative_base
from connection import get_db_connection

Base = declarative_base()


class StudentEnrollment(Base):
    __tablename__ = "studentenrollment"
    student_id = Column(Integer, primary_key=True)
    student_name = Column(String(100), nullable=False)
    student_phone = Column(String(50))
    course_id = Column(Integer)
    course_name = Column(String(100))
    instructor_name = Column(String(100))
    instructor_office = Column(String(50))
    department_name = Column(String(100))
    department_head = Column(String(100))
    semester = Column(String(20))
    grade = Column(String(2))

    def __repr__(self):
        return f"{self.__table_name__} - {self.student_id}"


DB_NAME = "universitydb"
engine = get_db_connection(DB_NAME)

with Session(engine) as session:
    student_1 = StudentEnrollment(
        student_id=100, student_name="Apple", student_phone="123456789", course_id="745", course_name="DB", instructor_name="Dr. Denton", instructor_office="123", department_name="CS", department_head="Dr. Simone", semester="6", grade="A")
    student_2 = StudentEnrollment(
        student_id=101, student_name="Ball", student_phone="123456798", course_id="745", course_name="DB", instructor_name="Dr. Denton", instructor_office="123", department_name="CS", department_head="Dr. Simone", semester="6", grade="B")

    session.begin()
    try:
        session.add(student_1)
        session.add(student_2)

    except Exception as e:
        print("Exception", e)
        session.rollback()

    else:
        session.commit()
