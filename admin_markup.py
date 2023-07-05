from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
import replicas


start_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    KeyboardButton(text=replicas.admin_add),
    KeyboardButton(text=replicas.admin_show),
)

add_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    KeyboardButton(text=replicas.add_restaurant),
    KeyboardButton(text=replicas.add_cafe),
    KeyboardButton(text=replicas.add_bar),
    KeyboardButton(text=replicas.add_club),
    KeyboardButton(text=replicas.add_expert),
    KeyboardButton(text=replicas.add_kitchen),
    KeyboardButton(text=replicas.back_admin),

)


show_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    KeyboardButton(text=replicas.show_restaurant),
    KeyboardButton(text=replicas.show_cafe),
    KeyboardButton(text=replicas.show_bar),
    KeyboardButton(text=replicas.show_club),
    KeyboardButton(text=replicas.show_expert),
    KeyboardButton(text=replicas.back_admin),
)

next_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(text=replicas.next)
)


markup_add_expert = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    KeyboardButton(text=replicas.add_expert_photographer),
    KeyboardButton(text=replicas.add_expert_visagiste),
    KeyboardButton(text=replicas.add_expert_stylist),
    KeyboardButton(text=replicas.add_expert_hair_stylist),
    KeyboardButton(text=replicas.add_expert_photo_studio),
    KeyboardButton(text=replicas.back_admin),

)

markup_show_expert = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text=replicas.show_expert_photographer, callback_data="show_expert_photographer"),
    InlineKeyboardButton(text=replicas.show_expert_visagiste, callback_data="show_expert_visagiste"),
    InlineKeyboardButton(text=replicas.show_expert_stylist, callback_data="show_expert_stylist"),
    InlineKeyboardButton(text=replicas.show_expert_hair_stylist, callback_data="show_expert_hair_stylist"),
    InlineKeyboardButton(text=replicas.show_expert_photo_studio, callback_data="show_expert_photo_studio"),
)


def generate_markup_kitchens_add(kitchens):
    markup = InlineKeyboardMarkup(row_width=1)
    for kitchen in kitchens:
        markup.add(
            InlineKeyboardButton(text=kitchen[1], callback_data=f"add_restaurant_{kitchen[0]}")
        )
    return markup

def generate_markup_kitchens_show(kitchens):
    markup = InlineKeyboardMarkup(row_width=1)
    for kitchen in kitchens:
        markup.add(
            InlineKeyboardButton(text=kitchen[1], callback_data=f"show_kitchen_restaurant_{kitchen[0]}")
        )
    return markup



def generate_markup_places_show(places):
    markup = InlineKeyboardMarkup(row_width=1)
    for place in places:
        markup.add(
            InlineKeyboardButton(text=place[1], callback_data=f"show_place_{place[0]}")
        )
    return markup


def generate_markup_delete_place(place_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(text="Удалить", callback_data=f"delete_place_{place_id}")
    )
    return markup


def generate_markup_delete_restaurant(restaurant_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(text="Удалить", callback_data=f"delete_restaurant_{restaurant_id}")
    )
    return markup


def generate_markup_restaurants_show(restaurants):
    markup = InlineKeyboardMarkup(row_width=1)
    for restaurant in restaurants:
        markup.add(
            InlineKeyboardButton(text=restaurant[1], callback_data=f"show_restaurant_{restaurant[0]}")
        )
    return markup


def generate_markup_experts_show(experts):
    markup = InlineKeyboardMarkup(row_width=1)
    for expert in experts:
        markup.add(
            InlineKeyboardButton(text=expert[1], callback_data=f"show_expert_id_{expert[0]}")
        )
    return markup


def generate_markup_delete_expert(expert_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(text="Удалить", callback_data=f"delete_expert_{expert_id}")
    )
    return markup
