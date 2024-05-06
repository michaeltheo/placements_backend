from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from database import Base


class UserRole(Enum):
    STUDENT = "student"
    ADMIN = "admin"


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


class QuestionType(str, Enum):
    multiple_choice = "multiple_choice"
    multiple_choice_with_text = "multiple_choice_with_text"
    free_text = "free_text"


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    reg_year = Column(String)
    fathers_name = Column(String)
    telephone_number = Column(String)
    email = Column(String)
    AM = Column(String, unique=True)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.STUDENT)

    # Define the relationships here, within the Users class
    dikaiologitika = relationship("Dikaiologitika", back_populates="user")
    answers = relationship("UserAnswer", back_populates="user")


class Dikaiologitika(Base):
    __tablename__ = 'dikaiologitika'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String)
    date = Column(DateTime)
    type = Column(SQLAlchemyEnum(DikaiologitikaType))
    file_name = Column(String)

    user = relationship("Users", back_populates='dikaiologitika')


class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, nullable=False)
    question_type = Column(
        SQLAlchemyEnum(QuestionType, values_callable=lambda obj: [e.value for e in obj], create_constraint=True,
                       name='questiontype'), nullable=False)
    supports_multiple_answers = Column(Boolean, default=False, nullable=False)
    # Relationship to AnswerOption
    answer_options = relationship("AnswerOption", back_populates="question")


class AnswerOption(Base):
    __tablename__ = 'answer_options'
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    option_text = Column(String, nullable=False)

    # Relationship to Question
    question = relationship("Question", back_populates="answer_options")
    user_answers = relationship("UserAnswer", back_populates="answer_option")


class UserAnswer(Base):
    __tablename__ = 'user_answers'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_option_id = Column(Integer, ForeignKey('answer_options.id'), nullable=True)
    answer_text = Column(Text, nullable=True)  # For free text responses or "Other" option text

    # Relationships
    user = relationship("Users", back_populates="answers")
    question = relationship("Question")
    answer_option = relationship("AnswerOption", back_populates="user_answers")
