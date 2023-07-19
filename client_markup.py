from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
import replicas
start_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
    KeyboardButton(text=replicas.food),
    KeyboardButton(text=replicas.event),
    KeyboardButton(text=replicas.favorite),
    KeyboardButton(text=replicas.places_nearby_by_geolocation),

)

food_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
    KeyboardButton(text=replicas.eat),
    KeyboardButton(text=replicas.drink),
    KeyboardButton(text=replicas.back),
)


drink_markup = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text="Кафе", callback_data="drinks_cafe"),
    InlineKeyboardButton(text="Бары", callback_data="drinks_bar"),
    InlineKeyboardButton(text="Клубы", callback_data="drinks_club"),
)


geo_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
    KeyboardButton(text=replicas.geo_restaurant),
    KeyboardButton(text=replicas.geo_cafe),
    KeyboardButton(text=replicas.geo_club),
    KeyboardButton(text=replicas.geo_bar),
    KeyboardButton(text=replicas.back),
)

geo_get_location_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(text=replicas.get_geo, request_location=True),
    KeyboardButton(text=replicas.back),
)


event_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
    KeyboardButton(text=replicas.photo_day),
)


def generate_markup_like_kitchens(kitchen_id, is_like=False, is_last=False):
    markup = InlineKeyboardMarkup()
    if is_like:
        markup.add(
            InlineKeyboardButton(text="❤️", callback_data=f"kitchen_{kitchen_id}")
        )
    else:
        markup.add(
            InlineKeyboardButton(text="🤍", callback_data=f"kitchen_{kitchen_id}")
        )
    if is_last:
        markup.add(
            InlineKeyboardButton(text="Получить результат", callback_data="get_result_kitchen")
        )
    return markup


def generate_markup_restaurants(link, id_favorite, is_favorite=False):
    markup_restaurants = InlineKeyboardMarkup(row_width=1)
    if is_favorite:
        markup_restaurants.add(
            InlineKeyboardButton(text="Удалить из избранного", callback_data=f"delete_favorite_restaurant_{id_favorite}"),

        )
    else:
        markup_restaurants.add(
            InlineKeyboardButton(text="Добавить в избранное", callback_data=f"add_favorite_restaurant_{id_favorite}"),

        )
    markup_restaurants.add(InlineKeyboardButton(text="Показать на карте", url=link))
    markup_restaurants.add(
        InlineKeyboardButton(text="Показать еще заведения", callback_data="more_restaurants"),
        InlineKeyboardButton(text="Главное меню", callback_data="main_menu"),
    )
    return markup_restaurants


markup_geo = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text="Показать еще заведения", callback_data="more_places_geo"),
    InlineKeyboardButton(text="Главное меню", callback_data="main_menu"),

)


def generate_markup_drink_places(type, link, id_favorite, is_favorite=False):
    markup = InlineKeyboardMarkup()
    if is_favorite:
        markup.add(
            InlineKeyboardButton(text="Удалить из избранного", callback_data=f"delete_favorite_place_{id_favorite}"),

        )
    else:
        markup.add(
            InlineKeyboardButton(text="Добавить в избранное", callback_data=f"add_favorite_place_{id_favorite}"),

        )
    markup.add(InlineKeyboardButton(text="Показать на карте", url=link))
    markup.add(InlineKeyboardButton(text="Показать еще заведения", callback_data=f"more_drink_places_{type}"),)
    return markup


def generate_markup_link_to_yandex(type, link, id_favorite, is_favorite=False):
    markup = InlineKeyboardMarkup(row_width=1)
    if is_favorite:
        markup.add(
            InlineKeyboardButton(text="Удалить из избранного", callback_data=f"delete_favorite_{type}_{id_favorite}"),

        )
    else:
        markup.add(
            InlineKeyboardButton(text="Добавить в избранное", callback_data=f"add_favorite_{type}_{id_favorite}"),

        )
    markup.add(
        InlineKeyboardButton(text="Показать на карте", url=link),
    )
    return markup


def markup_like_experts(expert_id, expert_type, is_last=False):
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Лайк", callback_data=f"like_expert_{expert_id}_{expert_type}"))
    if is_last:
        markup.add(
            InlineKeyboardButton(text="Пропустить категорию", callback_data=f"skip_expert_{expert_type}")
        )
    return markup


def create_markup_to_record(free_times_to_record, current_date):
    markup = InlineKeyboardMarkup(row_width=4)
    markup.add(
        InlineKeyboardButton(text="<<<", callback_data=f"previous_day_record_{current_date}"),
        InlineKeyboardButton(text=current_date, callback_data="current_day_record"),
        InlineKeyboardButton(text=">>>", callback_data=f"next_day_record_{current_date}"),
    )
    btns = []
    for time in free_times_to_record:
        btns.append(InlineKeyboardButton(text=time, callback_data=f"record_{time}_{current_date}"))
    markup.add(*btns)
    return markup


def create_markup_payment(url, bill_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text="Оплатить", url=url),
        InlineKeyboardButton(text="Я оплатил(а)", callback_data=f"payment_successful_{bill_id}")

    )
    return markup


def markup_favorite(place_type, place_id, link):
    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text="Удалить из избранного", callback_data=f"delete_from_favorite_{place_type}_{place_id}"),
        InlineKeyboardButton(text="Найти на карте", url=link),
    )
    return markup