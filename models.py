from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from database import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    AM = Column(String, unique=True)
    role = Column(String, default='student')

    # Define the relationships here, within the Users class
    dikaiologitika = relationship("Dikaiologitika", back_populates="user")
    answers = relationship("UserAnswer", back_populates="user")


class Dikaiologitika(Base):
    __tablename__ = 'dikaiologitika'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String, unique=True)
    date = Column(DateTime)
    type = Column(String)

    user = relationship("Users", back_populates='dikaiologitika')


# class Question(Base):
#     __tablename__ = 'questions'
#
#     id = Column(Integer, primary_key=True, index=True)
#     question_text = Column(String, nullable=False)
#     question_answers = Column(JSON, nullable=True)
#     answers = relationship("Answer", back_populates="question")
#
#
# class Answer(Base):
#     __tablename__ = 'answers'
#
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     question_id = Column(Integer, ForeignKey('questions.id'))
#     answer_text = Column(String, nullable=False)  # Could be the selected choice or an open-ended response
#
#     # Ensure the back_populates parameters refer to the correct relationships
#     user = relationship("Users", back_populates="answers")
#     question = relationship("Question", back_populates="answers")


class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, nullable=False)
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
    user_id = Column(Integer, ForeignKey('users.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_option_id = Column(Integer, ForeignKey('answer_options.id'))
    answer_text = Column(String, nullable=True)
    user = relationship("Users", back_populates="answers")
    question = relationship("Question")
    answer_option = relationship("AnswerOption", back_populates="user_answers")
