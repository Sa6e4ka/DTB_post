from aiogram.fsm.state import State, StatesGroup

class Savewords(StatesGroup):
    Hebrew = State()
    Translate = State()
    Transcription = State()


class Learn(StatesGroup):
    Translate = State()


class Learn1(StatesGroup):
    Translate = State()

    
class Delete(StatesGroup):
    Delete = State()


class Delete2(StatesGroup):
    Delete2 = State()


class Definitions(StatesGroup):
    first = State()


class Start(StatesGroup):
    first = State()


class SaveThemed(StatesGroup):
    first = State()
    second = State()
    third = State()
    fourth = State()


class Theme(StatesGroup):
    first = State()


class LearnThemed(StatesGroup):
    first = State()
    second = State()
    third = State()
    fourth = State()


class Competition(StatesGroup):
    Translate = State() 