from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMClient(StatesGroup):
    choice_kitchens = State()
    choice_drink_places = State()
    choice_experts = State()
    choice_times_to_record = State()
    payment = State()

class FSMGeo(StatesGroup):
    enter_type_place = State()
    get_places = State()


class FSMPlace(StatesGroup):
    kitchen = State()

    photos = State()
    name = State()
    address = State()
    work_hours = State()
    link_to_yandex = State()
    latitude = State()


class FSMExpert(StatesGroup):
    photos = State()
    name = State()
    description = State()
    price = State()
    link = State()
    calendar_id = State()


class FSMKitchen(StatesGroup):
    name = State()
    photos = State()