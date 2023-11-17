from aiogram.fsm.state import StatesGroup, State


class PersonDataForm(StatesGroup):
    is_driver = State()
    name = State()
    phone = State()
    city = State()
    vehicle = State()


class EditProfileDataForm(StatesGroup):
    name = State()
    phone = State()
    city = State()
    vehicle = State()


class TripModificationDataForm(StatesGroup):
    action = State()
    trip_id = State()


class EditTripDataForm(StatesGroup):
    id = State()
    place = State()
    date = State()
    available_seats = State()
    number_of_persons = State()
    comments = State()


class CreateTripDataForm(StatesGroup):
    place = State()
    date = State()
    is_person_driver = State()
    available_seats = State()
    number_of_persons = State()
    comments = State()

class FindTripByDateForm(StatesGroup):
    date = State()
    city = State()