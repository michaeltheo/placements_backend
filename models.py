from enum import Enum

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from database import Base


# Define user roles
class UserRole(Enum):
    STUDENT = "student"
    ADMIN = "admin"
    SUPER_ADMIN = 'super_admin'


# Define submission times
class SubmissionTime(str, Enum):
    START = "Έναρξη"
    END = "Λήξη"


# Define departments
class Department(str, Enum):
    IT_TEITHE = 'ΤΜΗΜΑ ΜΗΧΑΝΙΚΩΝ ΠΛΗΡΟΦΟΡΙΚΗΣ'
    EL_TEITHE = 'ΤΜΗΜΑ ΗΛΕΚΤΡΟΝΙΚΗΣ'
    IHU_IEE = 'ΤΜΗΜΑ ΜΗΧΑΝΙΚΩΝ ΠΛΗΡΟΦΟΡΙΚΗΣ ΚΑΙ ΗΛΕΚΤΡΟΝΙΚΩΝ ΣΥΣΤΗΜΑΤΩΝ'


# Define internship programs
class InternshipProgram(str, Enum):
    OAED = "ΟΑΕΔ"
    ESPA = "ΕΣΠΑ"
    EMPLOYER_FINANCED = "Αποκλειστικά χρηματοδοτούμενη από εργοδότη"


# Define internship statuses
class InternshipStatus(str, Enum):
    PENDING_REVIEW = "Pending review"
    ACTIVE = "Active"
    ENDED = "Ended"


# Define document types with descriptions
class DikaiologitikaType(Enum):
    BebaiosiPraktikis = "BebaiosiPraktikis"
    AitisiForeaGiaApasxolisiFoititi = "AitisiForeaGiaApasxolisiFoititi"
    BebaiosiApasxolisis = "BebaiosiApasxolisis"
    AsfalisiAskoumenou = "AsfalisiAskoumenou"

    @staticmethod
    def get_description(type_member):
        descriptions = {
            DikaiologitikaType.BebaiosiPraktikis: "Βεβαίωση Πρακτικής",
            DikaiologitikaType.AitisiForeaGiaApasxolisiFoititi: "Αίτηση Φορέα Απασχόλησης Φοιτητή",
            DikaiologitikaType.BebaiosiApasxolisis: "Βεβαίωση Απασχόλησης",
            DikaiologitikaType.AsfalisiAskoumenou: "Ασφάλιση Ασκούμενου",
        }
        return descriptions.get(type_member, "Unknown Type")


# Define question types
class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    MULTIPLE_CHOICE_WITH_TEXT = "multiple_choice_with_text"
    FREE_TEXT = "free_text"


# Define the Users table
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    reg_year = Column(String, nullable=True)
    fathers_name = Column(String, nullable=True)
    telephone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    AM = Column(String, unique=True, nullable=True)
    department = Column(SQLAlchemyEnum(Department), nullable=True)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.STUDENT)

    # Define relationships
    dikaiologitika = relationship("Dikaiologitika", back_populates="user")
    answers = relationship("UserAnswer", back_populates="user")
    internships = relationship("Internship", back_populates="user")


# Define the Companies table
class Companies(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    AFM = Column(String, unique=True, nullable=False)

    # Define relationships
    internships = relationship("Internship", back_populates="company")


# Define the Internship table
class Internship(Base):
    __tablename__ = 'internships'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    program = Column(SQLAlchemyEnum(InternshipProgram), nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(SQLAlchemyEnum(InternshipStatus), default=InternshipStatus.PENDING_REVIEW, nullable=False)

    # Define relationships
    user = relationship("Users", back_populates='internships')
    company = relationship("Companies", back_populates="internships")


# Define the Dikaiologitika table
class Dikaiologitika(Base):
    __tablename__ = 'dikaiologitika'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String)
    date = Column(DateTime)
    type = Column(SQLAlchemyEnum(DikaiologitikaType))
    submission_time = Column(SQLAlchemyEnum(SubmissionTime))
    file_name = Column(String)

    # Define relationships
    user = relationship("Users", back_populates='dikaiologitika')


# Define the Question table
class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, nullable=False)
    question_type = Column(
        SQLAlchemyEnum(QuestionType, values_callable=lambda obj: [e.value for e in obj], create_constraint=True,
                       name='questiontype'),
        nullable=False)
    supports_multiple_answers = Column(Boolean, default=False, nullable=False)

    # Define relationships
    answer_options = relationship("AnswerOption", back_populates="question")


# Define the AnswerOption table
class AnswerOption(Base):
    __tablename__ = 'answer_options'

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    option_text = Column(String, nullable=False)

    # Define relationships
    question = relationship("Question", back_populates="answer_options")
    user_answers = relationship("UserAnswer", back_populates="answer_option")


# Define the UserAnswer table
class UserAnswer(Base):
    __tablename__ = 'user_answers'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_option_id = Column(Integer, ForeignKey('answer_options.id'), nullable=True)
    answer_text = Column(Text, nullable=True)  # For free text responses or "Άλλο" option text

    # Define relationships
    user = relationship("Users", back_populates="answers")
    question = relationship("Question")
    answer_option = relationship("AnswerOption", back_populates="user_answers")
