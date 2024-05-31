from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, INTEGER, Float


class Base(DeclarativeBase):
    pass


'''
Таблица с пользователями
'''
class User(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32))
    chat_id: Mapped[str] = mapped_column(String(50))
    

    # Обозначение связи с таблицей слов
    words: Mapped[list["Words"]] = relationship("Words", back_populates="user")
    competition: Mapped[list["Competition"]] = relationship("Competition", back_populates="user")


'''
Таблица со словами
'''
class Words(Base):
    __tablename__ = 'words'

    word_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    word: Mapped[str] = mapped_column(String(100))
    translation: Mapped[str] = mapped_column(String(100))
    transcription: Mapped[str] = mapped_column(String(100))

# внешний ключ для присвоения каждому пользователю своего "словаря"
    # Т.е. у каждого пользователя будет свой набор слов
    user_id: Mapped[str] = mapped_column(ForeignKey("user.user_id"))
    user: Mapped["User"] = relationship("User", back_populates="words")


'''
Таблица с темами для слов 
'''
class Themes(Base):
    __tablename__ = "theme"

    theme_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    theme_name: Mapped[str] = mapped_column(String(60))

    theme_w: Mapped[list["ThemedWords"]] = relationship("ThemedWords", back_populates="theme")


'''
Таблица со словами, разделенными по темам
'''
class ThemedWords(Base):
    __tablename__  = "themed_word"

    word_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    word: Mapped[str] = mapped_column(String(100))
    translation: Mapped[str] = mapped_column(String(100))
    transcription: Mapped[str] = mapped_column(String(100))

    # Добавление внешнего ключа для соединения таблицы темы с таблицей со словами (разделенными по темам)
    theme_id: Mapped[int] = mapped_column(ForeignKey("theme.theme_id"))
    theme: Mapped[list["Themes"]] = relationship("Themes", back_populates="theme_w")


'''
Таблица с данными по соревнованиям
'''
class Competition(Base):
    __tablename__ = "competiton"
    
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    global_points: Mapped[int] = mapped_column(INTEGER, default=0)
    global_attempts: Mapped[int] = mapped_column(INTEGER, default=0)
    global_percentage: Mapped[float] = mapped_column(Float, default=0)

# Добавление внешнего ключа с id пользователя
    user_id: Mapped[str] = mapped_column(ForeignKey("user.user_id"))
    user: Mapped["User"] = relationship("User", back_populates="competition")

