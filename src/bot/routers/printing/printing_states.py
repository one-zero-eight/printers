from aiogram.fsm.state import State, StatesGroup


class PrintWork(StatesGroup):
    request_file = State()
    wait_for_acceptance = State()
    printing = State()
