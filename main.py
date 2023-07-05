import datetime
import logging
import random
import admin_markup
import config
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from FSM import FSMClient, FSMPlace, FSMExpert, FSMGeo, FSMKitchen
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import client_markup
import replicas
from database.database import Database
import geopy.distance
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from google_api_calendar import GoogleCalendar
from payment import Payment


logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
db = Database("database/db.sqlite")
calendar = GoogleCalendar()
wallet = Payment(config.yoomoney_wallet, config.yoomoney_token)

async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
    ])


@dp.message_handler(commands=['start'], state="*")
async def send_welcome(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.from_user.id, "Главное меню", reply_markup=client_markup.start_markup)


@dp.callback_query_handler(lambda c: c.data.startswith("kitchen"), state=FSMClient.choice_kitchens)
async def choice_kitchen(callback_query: types.CallbackQuery, state: FSMContext):
    kitchen_id = callback_query.data.split("_")[-1]
    async with state.proxy() as data:
        data["kitchens"].append(kitchen_id)
        kitchen_last_id = data["kitchen_last_id"]
    await callback_query.message.edit_reply_markup(client_markup.generate_markup_like_kitchens(kitchen_id, is_like=True, is_last=kitchen_last_id == int(kitchen_id)))
    await callback_query.answer("Лайкнуто!")


@dp.callback_query_handler(lambda c: c.data.startswith("drinks"))
async def choice_drink_places(callback_query: types.CallbackQuery, state: FSMContext):
    drink_place_type = callback_query.data.split("_")[-1]
    places = db.get_random_3_drink_place_by_type(drink_place_type)
    if len(places) == 0:
        await bot.send_message(callback_query.from_user.id, "Список заведений пуст!", reply_markup=client_markup.start_markup)
    else:
        for index, place in enumerate(places):
            place_id = place[0]

            place_name = place[2]
            place_address = place[3]
            place_work_hours = place[4]
            place_link_to_yandex = place[5]
            place_photos = db.get_place_photo_by_id(place_id)

            caption = f"Информация о заведение - <b>{place_name}</b>:\n" \
                      f"Адрес: {place_address}\n" \
                      f"Часы работы: {place_work_hours}\n"
            is_favorite = db.is_favorite_place(callback_query.from_user.id, place_id)
            if index == len(places) - 1:
                reply_markup = client_markup.generate_markup_drink_places(drink_place_type, place_link_to_yandex, is_favorite=is_favorite, id_favorite=place_id)
            else:
                reply_markup = client_markup.generate_markup_link_to_yandex("restaurant", place_link_to_yandex, is_favorite=is_favorite, id_favorite=place_id)
            if len(place_photos) == 0:
                await bot.send_message(callback_query.from_user.id, caption, parse_mode="HTML", reply_markup=reply_markup)
            else:
                if len(place_photos) > 1:
                    media = types.MediaGroup()
                    for photo in place_photos:
                        media.attach_photo(photo[0])
                    await bot.send_media_group(callback_query.from_user.id, media=media)
                    await bot.send_message(callback_query.from_user.id, caption, reply_markup=reply_markup, parse_mode="HTML")
                else:
                    await bot.send_photo(photo=place_photos[0][0], chat_id=callback_query.from_user.id,
                                         caption=caption, parse_mode="HTML", reply_markup=reply_markup)


@dp.callback_query_handler(lambda c: c.data.startswith("more_drink_places"))
async def more_drink_places(callback_query: types.CallbackQuery, state: FSMContext):
    drink_place_type = callback_query.data.split("_")[-1]
    places = db.get_random_3_drink_place_by_type(drink_place_type)
    if len(places) == 0:
        await bot.send_message(callback_query.from_user.id, "Список заведений пуст!",
                               reply_markup=client_markup.start_markup)
    else:
        for index, place in enumerate(places):
            place_id = place[0]
            place_name = place[2]
            place_address = place[3]
            place_work_hours = place[4]
            place_link_to_yandex = place[5]
            place_photos = db.get_place_photo_by_id(place_id)

            caption = f"Информация о заведение - <b>{place_name}</b>:\n" \
                      f"Адрес: {place_address}\n" \
                      f"Часы работы: {place_work_hours}\n"
            is_favorite = db.is_favorite_place(callback_query.from_user.id, place_id)
            if index == len(places) - 1:
                reply_markup = client_markup.generate_markup_drink_places(drink_place_type, place_link_to_yandex, is_favorite=is_favorite, id_favorite=place_id)
            else:
                reply_markup = client_markup.generate_markup_link_to_yandex("place", place_link_to_yandex, is_favorite=is_favorite, id_favorite=place_id)
            if len(place_photos) == 0:
                await bot.send_message(callback_query.from_user.id, caption, parse_mode="HTML", reply_markup=reply_markup)
            else:
                if len(place_photos) > 1:
                    media = types.MediaGroup()
                    for photo in place_photos:
                        media.attach_photo(photo[0])
                    await bot.send_media_group(callback_query.from_user.id, media=media)
                    await bot.send_message(callback_query.from_user.id, caption, reply_markup=reply_markup, parse_mode="HTML")
                else:
                    await bot.send_photo(photo=place_photos[0][0], chat_id=callback_query.from_user.id,
                                         caption=caption, parse_mode="HTML", reply_markup=reply_markup)


@dp.callback_query_handler(lambda c: c.data == "main_menu", state="*")
async def main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Главное меню", reply_markup=client_markup.start_markup)
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "more_restaurants", state=FSMClient.choice_kitchens)
async def more_restaurants(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        result = data["restaurants"]
        if len(result) > 0:
            if len(result) > 3:
                restaurants = []
                for i in range(3):
                    index = random.randint(0, len(result) - 1)
                    restaurants.append(result[index])
                    result.pop(index)
            else:
                restaurants = result
                result = []
            async with state.proxy() as data:
                data["restaurants"] = result

            for index, restaurant in enumerate(restaurants):
                restaurant_photos = db.get_restaurant_photo_by_id(restaurant[0])
                restaurant_id = restaurant[0]
                restaurant_name = restaurant[1]
                restaurant_address = restaurant[2]
                restaurant_work_hours = restaurant[3]
                restaurant_link_to_yandex = restaurant[4]

                caption = f"Информация о ресторане - <b>{restaurant_name}</b>:\n" \
                          f"Адрес: {restaurant_address}\n" \
                          f"Часы работы: {restaurant_work_hours}\n" \

                is_favorite = db.is_favorite_restaurant(callback_query.from_user.id, restaurant_id)
                if index == len(restaurants) - 1:
                    reply_markup = client_markup.generate_markup_restaurants(restaurant_link_to_yandex, is_favorite=is_favorite, id_favorite=restaurant_id)
                else:
                    reply_markup = client_markup.generate_markup_link_to_yandex("restaurant", restaurant_link_to_yandex, is_favorite=is_favorite, id_favorite=restaurant_id)
                if len(restaurant_photos) == 0:
                    await bot.send_message(callback_query.from_user.id, caption, parse_mode="HTML", reply_markup=reply_markup)
                elif len(restaurant_photos) > 1:
                    media = types.MediaGroup()
                    for photo in restaurant_photos:
                        media.attach_photo(photo[0])
                    await bot.send_media_group(callback_query.from_user.id, media=media)
                    await bot.send_message(callback_query.from_user.id, caption, parse_mode="HTML", reply_markup=reply_markup)
                else:
                    await bot.send_photo(photo=restaurant_photos[0][0], chat_id=callback_query.from_user.id,
                                         caption=caption, parse_mode="HTML", reply_markup=reply_markup)
        else:
            await bot.send_message(callback_query.from_user.id, "Рестораны закончились! Скоро добавим новые заведения, а пока перейдите в главное меню", reply_markup=client_markup.start_markup)
            await state.finish()


@dp.callback_query_handler(lambda c: c.data == "get_result_kitchen", state=FSMClient.choice_kitchens)
async def get_restaurants(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        kitchens = data["kitchens"]
        if len(kitchens) > 0:
            result = db.get_restaurant(kitchens)
            if len(result) > 3:
                restaurants = []
                for i in range(3):
                    index = random.randint(0, len(result) - 1)
                    restaurants.append(result[index])
                    result.pop(index)
            else:
                restaurants = result
                result = []
            async with state.proxy() as data:
                data["restaurants"] = result
            if len(restaurants) == 0:
                await bot.send_message(callback_query.from_user.id, "Рестораны закончились! Скоро добавим новые заведения, а пока перейдите в главное меню",
                                       reply_markup=client_markup.start_markup)
                await state.finish()
            else:
                for index, restaurant in enumerate(restaurants):
                    restaurant_photos = db.get_restaurant_photo_by_id(restaurant[0])
                    restaurant_id = restaurant[0]
                    restaurant_name = restaurant[1]
                    restaurant_address = restaurant[2]
                    restaurant_work_hours = restaurant[3]
                    restaurant_link_to_yandex = restaurant[4]

                    caption = f"Информация о ресторане - <b>{restaurant_name}</b>:\n" \
                              f"Адрес: {restaurant_address}\n" \
                              f"Часы работы: {restaurant_work_hours}\n"
                    is_favorite = db.is_favorite_restaurant(callback_query.from_user.id, restaurant_id)
                    if index == len(restaurants) - 1:
                        reply_markup = client_markup.generate_markup_restaurants(restaurant_link_to_yandex,
                                                                                 is_favorite=is_favorite,
                                                                                 id_favorite=restaurant_id)
                    else:
                        reply_markup = client_markup.generate_markup_link_to_yandex("restaurant",
                                                                                    restaurant_link_to_yandex,
                                                                                    is_favorite=is_favorite,
                                                                                    id_favorite=restaurant_id)
                    if len(restaurant_photos) == 0:
                        await bot.send_message(callback_query.from_user.id, caption, parse_mode="HTML",
                                               reply_markup=reply_markup)
                    elif len(restaurant_photos) > 1:
                        media = types.MediaGroup()
                        for photo in restaurant_photos:
                            media.attach_photo(photo[0])
                        await bot.send_media_group(callback_query.from_user.id, media=media)
                        await bot.send_message(callback_query.from_user.id, caption, parse_mode="HTML",
                                               reply_markup=reply_markup)
                    else:
                        await bot.send_photo(photo=restaurant_photos[0][0], chat_id=callback_query.from_user.id,
                                             caption=caption, parse_mode="HTML", reply_markup=reply_markup)
        else:
            await bot.send_message(callback_query.from_user.id, "Не лайкнуто ни одной кухни")


@dp.message_handler(content_types=types.ContentType.PHOTO, state=FSMPlace.photos)
async def get_place_photos(message: types, state: FSMContext):

    file_id = message.photo[-1].file_id
    async with state.proxy() as data:
        data["photos"].append(file_id)
    await bot.send_message(message.from_user.id, "Добавил фотографию!")


@dp.message_handler(content_types=types.ContentType.TEXT, state=FSMPlace.photos)
async def next_place_photos(message: types, state: FSMContext):
    await bot.send_message(message.from_user.id, "Теперь пришлите мне название заведения")
    await FSMPlace.next()


@dp.message_handler(content_types=types.ContentType.TEXT, state=FSMPlace.name)
async def get_place_name(message: types, state: FSMContext):
    name = message.text
    async with state.proxy() as data:
        data["name"] = name
    await bot.send_message(message.from_user.id, "Теперь пришлите мне адрес заведения")
    await FSMPlace.next()


@dp.message_handler(content_types=types.ContentType.TEXT, state=FSMPlace.address)
async def get_place_address(message: types, state: FSMContext):
    address = message.text
    async with state.proxy() as data:
        data["address"] = address
    await bot.send_message(message.from_user.id, "Теперь пришлите мне режим работы заведения")
    await FSMPlace.next()


@dp.message_handler(content_types=types.ContentType.TEXT, state=FSMPlace.work_hours)
async def get_place_work_hours(message: types, state: FSMContext):
    work_hours = message.text
    async with state.proxy() as data:
        data["work_hours"] = work_hours
    await bot.send_message(message.from_user.id, "Теперь пришлите мне ссылку на яндекс карты заведения")
    await FSMPlace.next()


@dp.message_handler(content_types=types.ContentType.TEXT, state=FSMPlace.link_to_yandex)
async def get_place_yandex_link(message: types, state: FSMContext):
    link_to_yandex = message.text
    async with state.proxy() as data:
        data["link_to_yandex"] = link_to_yandex
    await bot.send_message(message.from_user.id, "Теперь пришлите мне координаты заведения")
    await FSMPlace.next()


@dp.message_handler(content_types=types.ContentType.TEXT, state=FSMPlace.latitude)
async def get_place_latitude(message: types, state: FSMContext):
    latitude = message.text
    async with state.proxy() as data:
        place_type = data["place_type"]
        photos = data["photos"]
        name = data["name"]
        address = data["address"]
        work_hours = data["work_hours"]
        link_to_yandex = data["link_to_yandex"]
        if place_type == "restaurant":
            kitchen_id = data["kitchen_id"]
            db.add_restaurant(kitchen_id, photos, name, address, work_hours, link_to_yandex, latitude)
        else:
            db.add_drink_place(photos, name, address, work_hours, link_to_yandex, latitude, place_type)
    await bot.send_message(message.from_user.id, "Успешно добавил заведение!", reply_markup=admin_markup.add_markup)
    await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith("add_restaurant_"), state=FSMPlace.kitchen)
async def get_kitchen_add_restaurant(callback: types.CallbackQuery, state: FSMContext):
    kitchen_id = callback.data.split("_")[-1]
    async with state.proxy() as data:
        data["kitchen_id"] = kitchen_id
        data["photos"] = []
    await bot.send_message(callback.from_user.id, "Теперь пришлите фотографии заведения (в сжатом виде)",
                           reply_markup=admin_markup.next_markup)
    await FSMPlace.next()


@dp.message_handler(content_types=types.ContentType.PHOTO, state=FSMExpert.photos)
async def get_expert_photos(message: types, state: FSMContext):
    file_id = message.photo[-1].file_id
    async with state.proxy() as data:
        data["photos"].append(file_id)
    await bot.send_message(message.from_user.id, "Добавил фотографию!")


@dp.message_handler(content_types=types.ContentType.TEXT, state=FSMExpert.photos)
async def next_expert_photos(message: types, state: FSMContext):
    await bot.send_message(message.from_user.id, "Теперь пришлите мне имя специалиста")
    await FSMExpert.next()


@dp.message_handler(content_types=types.ContentType.TEXT, state=FSMExpert.name)
async def get_expert_name(message: types, state: FSMContext):
    name = message.text
    async with state.proxy() as data:
        data["name"] = name
    await bot.send_message(message.from_user.id, "Теперь пришлите мне описание стиля специалиста")
    await FSMExpert.next()


@dp.message_handler(content_types=types.ContentType.TEXT, state=FSMExpert.description)
async def get_expert_description_style(message: types, state: FSMContext):
    description_style = message.text
    async with state.proxy() as data:
        data["description_style"] = description_style
    await bot.send_message(message.from_user.id, "Теперь пришлите мне стоимость")
    await FSMExpert.next()


@dp.message_handler(content_types=types.ContentType.TEXT, state=FSMExpert.price)
async def get_expert_price(message: types, state: FSMContext):
    price = message.text
    async with state.proxy() as data:
        data["price"] = price
    await bot.send_message(message.from_user.id, "Теперь пришлите ссылку на страничку специалиста на сайте")
    await FSMExpert.next()


@dp.message_handler(content_types=types.ContentType.TEXT, state=FSMExpert.link)
async def get_expert_link(message: types, state: FSMContext):
    link = message.text
    async with state.proxy() as data:
        data["link"] = link
    await bot.send_message(message.from_user.id, "Теперь пришли мне id календаря специалиста")
    await FSMExpert.next()


@dp.message_handler(content_types=types.ContentType.TEXT, state=FSMExpert.calendar_id)
async def get_expert_calendar_id(message: types, state: FSMContext):
    calendar_id = message.text
    if calendar.add_calendar(calendar_id):
        async with state.proxy() as data:
            expert_type = data["expert_type"]
            photos = data["photos"]
            name = data["name"]
            description_style = data["description_style"]
            price = data["price"]
            link = data["link"]
            db.add_expert(expert_type, photos, name, description_style, price, link, calendar_id)

        await bot.send_message(message.from_user.id, "Успешно добавил специалиста!", reply_markup=admin_markup.markup_add_expert)
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, "Не удалось добавить календарь с таким идентификатором, проверь введенные данные и попробуй еще раз!")


@dp.callback_query_handler(lambda c: c.data.startswith("show_kitchen_restaurant_"))
async def get_kitchen_show_restaurant(callback: types.CallbackQuery, state: FSMContext):
    kitchen_id = callback.data.split("_")[-1]
    restaurants = db.get_name_restaurants(kitchen_id)
    if len(restaurants) > 0:
        await bot.send_message(callback.from_user.id, "Список ресторанов",
                           reply_markup=admin_markup.generate_markup_restaurants_show(restaurants))
    else:

        await bot.send_message(callback.from_user.id, "Список ресторанов этой кухни пуст", reply_markup=admin_markup.show_markup)


@dp.callback_query_handler(lambda c: c.data.startswith("show_restaurant_"))
async def show_restaurant(callback: types.CallbackQuery, state: FSMContext):
    restaurant_id = callback.data.split("_")[-1]
    restaurant_photos = db.get_restaurant_photo_by_id(restaurant_id)
    restaurant_info = db.get_restaurant_by_id(restaurant_id)[0]
    restaurant_name = restaurant_info[0]
    restaurant_address = restaurant_info[1]
    restaurant_work_hours = restaurant_info[2]
    restaurant_link_to_yandex = restaurant_info[3]
    restaurant_latitude = restaurant_info[4]
    caption = f"Информация о ресторане - <b>{restaurant_name}</b>:\n"\
                                                      f"Адрес: {restaurant_address}\n"\
                                                      f"Часы работы: {restaurant_work_hours}\n"\
                                                      f"Ссылка на яндекс карты: {restaurant_link_to_yandex}\n"\
                                                      f"Координаты: {restaurant_latitude}\n"
    if len(restaurant_photos) == 0:
        await bot.send_message(callback.from_user.id, caption,
                             reply_markup=admin_markup.generate_markup_delete_restaurant(restaurant_id),
                             parse_mode="HTML")
    elif len(restaurant_photos) > 1:
        media = types.MediaGroup()

        media.attach_photo(restaurant_photos[0][0], caption, parse_mode="HTML")
        for i in range(1, len(restaurant_photos)):
            media.attach_photo(restaurant_photos[i][0])
        await bot.send_media_group(callback.from_user.id, media=media)
        await bot.send_message(callback.from_user.id, "Удалить данный ресторан?", reply_markup=admin_markup.generate_markup_delete_restaurant(restaurant_id))
    else:
        await bot.send_photo(photo=restaurant_photos[0][0], chat_id=callback.from_user.id, caption=caption,
                               reply_markup=admin_markup.generate_markup_delete_restaurant(restaurant_id), parse_mode="HTML")


@dp.callback_query_handler(lambda c: c.data.startswith("delete_restaurant_"))
async def delete_restaurant(callback: types.CallbackQuery, state: FSMContext):
    restaurant_id = callback.data.split("_")[-1]
    db.delete_restaurant(restaurant_id)
    await bot.send_message(callback.from_user.id, f"Успешно удалил ресторан!",
                           reply_markup=admin_markup.show_markup, parse_mode="HTML")


@dp.callback_query_handler(lambda c: c.data.startswith("show_place_"))
async def show_place(callback: types.CallbackQuery, state: FSMContext):
    place_id = callback.data.split("_")[-1]
    place_info = db.get_place_by_id(place_id)[0]
    place_name = place_info[0]
    place_address = place_info[1]
    place_work_hours = place_info[2]
    place_link_to_yandex = place_info[3]
    place_latitude = place_info[4]
    place_photos = db.get_place_photo_by_id(place_id)

    caption = f"Информация о заведение - <b>{place_name}</b>:\n"\
                                                  f"Адрес: {place_address}\n"\
                                                  f"Часы работы: {place_work_hours}\n"\
                                                  f"Ссылка на яндекс карты: {place_link_to_yandex}\n"\
                                                  f"Координаты: {place_latitude}\n"
    if len(place_photos) == 0:
        await bot.send_message(callback.from_user.id, caption,
                             reply_markup=admin_markup.generate_markup_delete_place(place_id),
                             parse_mode="HTML")
    elif len(place_photos) > 1:
        media = types.MediaGroup()

        media.attach_photo(place_photos[0][0], caption, parse_mode="HTML")
        for i in range(1, len(place_photos)):
            media.attach_photo(place_photos[i][0])
        await bot.send_media_group(callback.from_user.id, media=media)
        await bot.send_message(callback.from_user.id, "Удалить данное заведение?", reply_markup=admin_markup.generate_markup_delete_place(place_id))
    else:
        await bot.send_photo(photo=place_photos[0][0], chat_id=callback.from_user.id, caption=caption,
                             reply_markup=admin_markup.generate_markup_delete_place(place_id),
                             parse_mode="HTML")


@dp.callback_query_handler(lambda c: c.data.startswith("delete_place_"))
async def delete_place(callback: types.CallbackQuery, state: FSMContext):
    place_id = callback.data.split("_")[-1]
    db.delete_place(place_id)
    await bot.send_message(callback.from_user.id, f"Успешно удалил заведение!",
                           reply_markup=admin_markup.show_markup, parse_mode="HTML")


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    if message.from_user.id in config.ADMINS:
        await bot.send_message(message.from_user.id, "Админка", reply_markup=admin_markup.start_markup)


@dp.callback_query_handler(lambda c: c.data.startswith("show_expert_id_"))
async def show_expert_by_id(callback: types.CallbackQuery, state: FSMContext):
    expert_id = callback.data.split("_")[-1]
    expert_info = db.get_expert_by_id(expert_id)[0]
    expert_name = expert_info[0]
    expert_style = expert_info[1]
    expert_price = expert_info[2]
    expert_link = expert_info[3]
    expert_photos = db.get_expert_photo_by_id(expert_id)

    caption = f"Информация о специалисте - <b>{expert_name}</b>:\n"\
                                                  f"Описание стиля: {expert_style}\n"\
                                                  f"Цена: {expert_price}\n"\
                                                  f"Ссылка на специалиста: {expert_link}\n"
    if len(expert_photos) == 0:
        await bot.send_message(callback.from_user.id, caption,
                             reply_markup=admin_markup.generate_markup_delete_expert(expert_id),
                             parse_mode="HTML")
    elif len(expert_photos) > 1:
        media = types.MediaGroup()

        media.attach_photo(expert_photos[0][0], caption, parse_mode="HTML")
        for i in range(1, len(expert_photos)):
            media.attach_photo(expert_photos[i][0])
        await bot.send_media_group(callback.from_user.id, media=media)
        await bot.send_message(callback.from_user.id, "Удалить данного специалиста?", reply_markup=admin_markup.generate_markup_delete_expert(expert_id))
    else:
        await bot.send_photo(photo=expert_photos[0][0], chat_id=callback.from_user.id, caption=caption,
                             reply_markup=admin_markup.generate_markup_delete_expert(expert_id),
                             parse_mode="HTML")


@dp.callback_query_handler(lambda c: c.data.startswith("show_expert_"))
async def show_expert_(callback: types.CallbackQuery, state: FSMContext):
    expert_type = callback.data.split("_")[-1]
    experts = db.get_experts_name_by_type(expert_type)
    if len(experts) > 0:
        markup_ = admin_markup.generate_markup_experts_show(experts)
        await bot.send_message(callback.from_user.id, f"Список специалистов",
                               reply_markup=markup_)
    else:
        await bot.send_message(callback.from_user.id, f"Список специалистов пуст")


@dp.callback_query_handler(lambda c: c.data.startswith("delete_expert_"))
async def delete_place(callback: types.CallbackQuery, state: FSMContext):
    expert_id = callback.data.split("_")[-1]
    db.delete_expert(expert_id)
    await bot.send_message(callback.from_user.id, f"Успешно удалил специалиста!",
                           reply_markup=admin_markup.show_markup, parse_mode="HTML")


@dp.message_handler(content_types=types.ContentType.LOCATION, state=FSMGeo.enter_type_place)
async def get_location(message: types.Message, state: FSMContext):
    latitude = message.location.latitude
    longitude = message.location.longitude
    user_location = geopy.Point(latitude, longitude)
    await FSMGeo.get_places.set()
    async with state.proxy() as data:
        place_type = data["place_type"]
        if place_type in ("club", "bar", "cafe"):
            places = db.get_drink_places([place_type])
        else:
            places = db.get_restaurants_for_geo()

        nearest_places = []
        for index, place in enumerate(places):
            place_split = place[-1].split(" ")
            latitude_place = float(place_split[0])
            longitude_place = float(place_split[1])
            if len(nearest_places) < 3:

                nearest_places.append([index, geopy.distance.distance(user_location, geopy.Point(latitude_place, longitude_place)).m])
            else:
                distance_place = geopy.distance.distance(user_location, geopy.Point(latitude_place, longitude_place)).m
                for index_nearest, nearest_place in enumerate(nearest_places):
                    if distance_place < nearest_place[1]:
                        nearest_places[index_nearest] = [index, distance_place]
        for index, item in enumerate(nearest_places):

            place = places.pop(item[0] - index)
            if type(place[1]) in (int, ):
                place_photos = db.get_restaurant_photo_by_id(place[0])
            else:
                place_photos = db.get_place_photo_by_id(place[0])

            place_name = place[2]
            place_address = place[3]
            place_work_hours = place[4]
            place_link_to_yandex = place[5]
            caption = f"Информация о заведение - <b>{place_name}</b>:\n" \
                      f"Адрес: {place_address}\n" \
                      f"Часы работы: {place_work_hours}\n"

            if index == len(nearest_places) - 1:
                markup_ = client_markup.markup_geo
            else:
                markup_ = None

            if len(place_photos) == 0:
                if len(places) == 0:
                    await state.finish()
                    await bot.send_message(message.from_user.id, caption, parse_mode="HTML", reply_markup=client_markup.start_markup)
                else:
                    await bot.send_message(message.from_user.id, caption, parse_mode="HTML", reply_markup=markup_)

            elif len(place_photos) > 1:
                media = types.MediaGroup()

                for photo in place_photos:
                    media.attach_photo(photo[0])
                await bot.send_media_group(message.from_user.id, media=media)
                if len(places) == 0:
                    await state.finish()
                    await bot.send_message(message.from_user.id, caption, reply_markup=client_markup.start_markup, parse_mode="HTML")
                else:
                    await bot.send_message(message.from_user.id, caption, reply_markup=markup_, parse_mode="HTML")

            else:

                if len(places) == 0:
                    await state.finish()
                    await bot.send_photo(photo=place_photos[0][0], chat_id=message.from_user.id, caption=caption,
                                         parse_mode="HTML", reply_markup=client_markup.start_markup)

                else:
                    await bot.send_photo(photo=place_photos[0][0], chat_id=message.from_user.id, caption=caption,
                                         parse_mode="HTML", reply_markup=markup_)

        data["places"] = places


@dp.callback_query_handler(lambda c: c.data.startswith("delete_favorite_"), state="*")
async def delete_favorite(callback: types.CallbackQuery):
    callback_split = callback.data.split("_")
    type_place = callback_split[-2]
    place_id = callback_split[-1]
    db.delete_favorite(type_place, place_id, callback.from_user.id)
    await callback.answer("Удалено!", show_alert=True)
    markup = callback.message.reply_markup
    markup.inline_keyboard[0][0] = InlineKeyboardButton(text="Добавить в избранное", callback_data=f"add_favorite_{type_place}_{place_id}")
    await bot.edit_message_reply_markup(callback.from_user.id, callback.message.message_id, reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data.startswith("add_favorite_"), state="*")
async def add_favorite(callback: types.CallbackQuery):

    callback_split = callback.data.split("_")
    type_place = callback_split[-2]
    place_id = callback_split[-1]
    db.add_favorite(type_place, place_id, callback.from_user.id)
    await callback.answer("Заведение добавлено в избранное! Теперь ты точно его не потеряешь", show_alert=True)
    markup = callback.message.reply_markup
    markup.inline_keyboard[0][0] = InlineKeyboardButton(text="Удалить из избранного", callback_data=f"delete_favorite_{type_place}_{place_id}")
    await bot.edit_message_reply_markup(callback.from_user.id, callback.message.message_id, reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data == "more_places_geo", state=FSMGeo.enter_type_place)
async def more_places_geo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        latitude = data["latitude"]
        longitude = data["longitude"]
        user_location = geopy.Point(latitude, longitude)
        places = data["places"]
        nearest_places = []
        for index, place in enumerate(places):
            place_split = place[-1].split(" ")
            latitude_place = float(place_split[0])
            longitude_place = float(place_split[1])
            if len(nearest_places) < 3:

                nearest_places.append([index, geopy.distance.distance(user_location, geopy.Point(latitude_place, longitude_place)).m])
            else:
                distance_place = geopy.distance.distance(user_location, geopy.Point(latitude_place, longitude_place)).m
                for index_nearest, nearest_place in enumerate(nearest_places):
                    if distance_place < nearest_place[1]:
                        nearest_places[index_nearest] = [index, distance_place]
        for index, item in enumerate(nearest_places):

            place = places.pop(item[0] - index)
            if type(place[1]) in (int, ):
                place_photos = db.get_restaurant_photo_by_id(place[0])
            else:
                place_photos = db.get_place_photo_by_id(place[0])

            place_name = place[2]
            place_address = place[3]
            place_work_hours = place[4]
            place_link_to_yandex = place[5]
            caption = f"Информация о заведение - <b>{place_name}</b>:\n" \
                      f"Адрес: {place_address}\n" \
                      f"Часы работы: {place_work_hours}\n" \

            if index == len(nearest_places) - 1:
                markup_ = client_markup.markup_geo
            else:
                markup_ = None

            if len(place_photos) == 0:
                if len(places) == 0:
                    await state.finish()
                    await bot.send_message(message.from_user.id, caption, parse_mode="HTML",
                                           reply_markup=client_markup.start_markup)
                else:
                    await bot.send_message(message.from_user.id, caption, parse_mode="HTML", reply_markup=markup_)

            elif len(place_photos) > 1:
                media = types.MediaGroup()

                for photo in place_photos:
                    media.attach_photo(photo[0])
                await bot.send_media_group(message.from_user.id, media=media)
                if len(places) == 0:
                    await state.finish()
                    await bot.send_message(message.from_user.id, caption, reply_markup=client_markup.start_markup, parse_mode="HTML")
                else:
                    await bot.send_message(message.from_user.id, caption, reply_markup=markup_, parse_mode="HTML")

            else:

                if len(places) == 0:
                    await state.finish()
                    await bot.send_photo(photo=place_photos[0][0], chat_id=message.from_user.id, caption=caption,
                                         parse_mode="HTML", reply_markup=client_markup.start_markup)

                else:
                    await bot.send_photo(photo=place_photos[0][0], chat_id=message.from_user.id, caption=caption,
                                         parse_mode="HTML", reply_markup=markup_)

            data["places"] = places


@dp.message_handler(state=FSMGeo.enter_type_place)
async def get_type_place(message: types.Message, state: FSMContext):
    if message.text in (replicas.geo_club, replicas.geo_bar, replicas.geo_cafe, replicas.geo_restaurant):
        async with state.proxy() as data:
            if message.text == replicas.geo_club:
                data["place_type"] = "club"
            if message.text == replicas.geo_bar:
                data["place_type"] = "bar"
            if message.text == replicas.geo_cafe:
                data["place_type"] = "cafe"
            if message.text == replicas.geo_restaurant:
                data["place_type"] = "restaurant"
        await bot.send_message(message.from_user.id, "Отправь мне локацию", reply_markup=client_markup.geo_get_location_markup)
    elif message.text == replicas.back:
        await bot.send_message(message.from_user.id, "Назад", reply_markup=client_markup.start_markup)
        await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith("like_expert"), state=FSMClient.choice_experts)
async def like_expert(callback: types.CallbackQuery, state: FSMContext):
    if callback.data.startswith("like_expert"):
        async with state.proxy() as data:
            expert_type = callback.data.split("_")[-1]
            expert_id = callback.data.split("_")[-2]
            if data.get(expert_type) is None:
                await callback.answer("Лайкнуто!")
                markup_ = callback.message.reply_markup

                markup_.inline_keyboard[0][0] = InlineKeyboardButton(text="❤️ Лайк", callback_data=f"like_expert_{expert_id}_{expert_type}")
                await callback.message.edit_reply_markup(markup_)
                data[expert_type] = expert_id
                expert_types: list = data["expert_types"]
                expert_type_index = expert_types.index(expert_type)
                if expert_type_index != len(expert_types) - 1:
                    await show_expert(expert_types[expert_type_index + 1], callback.from_user.id)
                else:
                    await FSMClient.next()
                    data["records"] = []
                    expert_type = expert_types.pop(0)
                    data["expert_types"] = expert_types
                    expert_id = data[expert_type]
                    expert_name = db.get_expert_by_id(expert_id)[0][0]
                    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    free_times_to_record = calendar.get_free_times_for_record(current_date)
                    await bot.send_message(callback.from_user.id, f"Выбери время для записи к {expert_name}",
                                           reply_markup=client_markup.create_markup_to_record(free_times_to_record,
                                                                                              current_date, expert_id))


@dp.callback_query_handler(lambda c: c.data.startswith("previous_day_record_"), state=FSMClient.choice_times_to_record)
async def previous_day_record_(callback: types.CallbackQuery):
    callback_split = callback.data.split("_")
    expert_id = callback_split[-1]
    date = callback_split[-2]
    if date != datetime.datetime.now().strftime("%Y-%m-%d"):
        previous_date = (datetime.datetime.strptime(date, "%Y-%m-%d") - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        free_times_to_record = calendar.get_free_times_for_record(previous_date)
        await callback.message.edit_reply_markup(reply_markup=client_markup.create_markup_to_record(free_times_to_record, previous_date, expert_id))


@dp.callback_query_handler(lambda c: c.data.startswith("next_day_record_"), state=FSMClient.choice_times_to_record)
async def next_day_record_(callback: types.CallbackQuery):
    callback_split = callback.data.split("_")
    expert_id = callback_split[-1]
    date = callback_split[-2]
    if date <= (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d"):
        next_date = (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        free_times_to_record = calendar.get_free_times_for_record(next_date)
        await callback.message.edit_reply_markup(reply_markup=client_markup.create_markup_to_record(free_times_to_record, next_date, expert_id))


@dp.callback_query_handler(lambda c: c.data.startswith("record_"), state=FSMClient.choice_times_to_record)
async def record_user_to_expert(callback: types.CallbackQuery, state: FSMContext):
    callback_split = callback.data.split("_")
    expert_id = callback_split[-1]
    date = callback_split[-2]
    time = callback_split[-3]
    async with state.proxy() as data:
        data["records"].append([date, time, expert_id])
        expert_types = data["expert_types"]
        if len(expert_types) != 0:
            expert_type = expert_types.pop(0)
            data["expert_types"] = expert_types
            expert_id = data[expert_type]
            expert_name = db.get_expert_by_id(expert_id)[0][0]
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            free_times_to_record = calendar.get_free_times_for_record(current_date)
            await bot.send_message(callback.from_user.id, f"Выбери время для записи к {expert_name}",
                                   reply_markup=client_markup.create_markup_to_record(free_times_to_record,
                                                                                      current_date, expert_id))
        else:
            # Создание payment на оплату
            await FSMClient.next()
            price = 0
            for item in data["records"]:
                expert = db.get_expert_by_id(item[-1])
                price += int(expert[0][2])
            url, bill = wallet.create_payment(3)
            db.add_payment(callback.from_user.id, bill, price, datetime.datetime.now().strftime("%Y-%m-%d"))
            await bot.send_message(callback.from_user.id, "Для оплаты записи перейдите по ссылке", reply_markup=client_markup.create_markup_payment(url, bill))


@dp.callback_query_handler(lambda c: c.data.startswith("payment_successful"), state=FSMClient.payment)
async def payment_successful(callback: types.CallbackQuery, state:FSMContext):
    bill_id = callback.data.split("_")[-1]
    if wallet.check_payment(bill_id) == 'Оплачено':
        # Запись в гугл календарь
        async with state.proxy() as data:
            records = data["records"]
            for record in records:
                expert_calendar_id = db.get_expert_by_id(record[2])[0][4]
                date_from = f"{record[0]}T{record[1]}:00"
                hour_to = "10:00" if record[1] == "09:00" else f"{int(record[1].split(':')[0]) + 1}:00"
                date_to = f"{record[0]}T{hour_to}:00"
                calendar.insert_into_calendar(expert_calendar_id, date_from=date_from, date_to=date_to)
            await bot.send_message(callback.from_user.id, "Успешно записал вас!")
            await state.finish()
    else:
        await callback.answer("Не оплачено!")


@dp.message_handler(state=FSMKitchen.name)
async def get_name_kitchen(message: types.Message, state: FSMContext):
    name = message.text
    async with state.proxy() as data:
        data["name"] = name
    await bot.send_message(message.from_user.id, "Теперь пришли мне фото кухни")
    await FSMKitchen.photos.set()


@dp.message_handler(state=FSMKitchen.photos, content_types=types.ContentType.PHOTO)
async def get_photo_for_kitchen(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        photo = message.photo[-1].file_id
        name = data["name"]
        db.add_kitchen(name, photo)
    await bot.send_message(message.from_user.id, "Успешно добавил", reply_markup=admin_markup.add_markup)
    await state.finish()


@dp.message_handler()
async def all_messages(message: types.Message, state: FSMContext):
    if message.from_user.id in config.ADMINS:
        if message.text == replicas.admin_add:
            await bot.send_message(message.from_user.id, "Добавить", reply_markup=admin_markup.add_markup)
        elif message.text == replicas.admin_show:
            await bot.send_message(message.from_user.id, "Просмотр", reply_markup=admin_markup.show_markup)
        elif message.text == replicas.back_admin:
            await bot.send_message(message.from_user.id, "Назад", reply_markup=admin_markup.start_markup)
        elif message.text == replicas.add_bar or message.text == replicas.add_cafe or message.text == replicas.add_club:
            # Добавление бара, кафе, клуба
            if message.text == replicas.add_bar:
                place_type = "bar"
            elif message.text == replicas.add_cafe:
                place_type = "cafe"
            else:
                place_type = "club"
            await FSMPlace.photos.set()
            async with state.proxy() as data:
                data["place_type"] = place_type
                data["photos"] = []
            await bot.send_message(message.from_user.id, "Пришлите фотографии заведения (в сжатом виде)", reply_markup=admin_markup.next_markup)
        elif message.text == replicas.add_restaurant:
            # Добавление ресторана
            await FSMPlace.kitchen.set()
            await bot.send_message(message.chat.id, "Выберите кухню, к которой прикрепится ресторан")
            async with state.proxy() as data:
                data["place_type"] = "restaurant"
                kitchens = db.get_kitchens()
                kitchen_markup = admin_markup.generate_markup_kitchens_add(kitchens)
                await bot.send_message(message.from_user.id, "Выберите кухню", reply_markup=kitchen_markup)

        elif message.text == replicas.add_expert:
            # Выбор специалиста
            await bot.send_message(message.chat.id, "Выберите тип специалиста", reply_markup=admin_markup.markup_add_expert)
        elif message.text in (replicas.add_expert_photo_studio, replicas.add_expert_photographer, replicas.add_expert_stylist,
                              replicas.add_expert_hair_stylist, replicas.add_expert_visagiste):
            # Добавление специалиста
            if message.text == replicas.add_expert_photographer:
                expert_type = "photographer"
            elif message.text == replicas.add_expert_visagiste:
                expert_type = "visagiste"
            elif message.text == replicas.add_expert_stylist:
                expert_type = "stylist"
            elif message.text == replicas.add_expert_hair_stylist:
                expert_type = "hairstylist"
            else:
                expert_type = "photostudio"
            await FSMExpert.photos.set()
            async with state.proxy() as data:
                data["expert_type"] = expert_type
                data["photos"] = []
            await bot.send_message(message.from_user.id, "Пришлите фотографии работ (в сжатом виде)", reply_markup=admin_markup.next_markup)
        elif message.text == replicas.add_kitchen:
            await bot.send_message(message.from_user.id, "Пришли мне наименование кухни")
            await FSMKitchen.name.set()
        elif message.text == replicas.show_restaurant:
            # Просмотр ресторанов
            kitchens = db.get_kitchens()
            markup_kitchens = admin_markup.generate_markup_kitchens_show(kitchens)
            await bot.send_message(message.from_user.id, "Выберите кухню", reply_markup=markup_kitchens)
        elif message.text == replicas.show_bar or message.text == replicas.show_club or message.text == replicas.show_cafe:
            # Просмотр бара, клуба, кафе
            if message.text == replicas.show_bar:
                place_type = "bar"
            elif message.text == replicas.show_club:
                place_type = "club"
            else:
                place_type = "cafe"

            places = db.get_place_name_by_type(place_type)
            if len(places) > 0:
                markup_places = admin_markup.generate_markup_places_show(places)

                await bot.send_message(message.from_user.id, "Заведения", reply_markup=markup_places)
            else:
                await bot.send_message(message.from_user.id, "Список заведений пуст")

        elif message.text == replicas.show_expert:
            # Просмотр специалистов
            await bot.send_message(message.from_user.id, "Выберите тип специалиста", reply_markup=admin_markup.markup_show_expert)

    if message.text == replicas.food:
        await bot.send_message(message.from_user.id, "Еда", reply_markup=client_markup.food_markup)
    elif message.text == replicas.eat:
        await FSMClient.choice_kitchens.set()

        kitchens = db.get_kitchens()
        async with state.proxy() as data:
            data["kitchens"] = []
            data["kitchen_last_id"] = kitchens[-1][0]
        for index in range(len(kitchens) - 1):
            await bot.send_photo(message.from_user.id, caption=kitchens[index][1], photo=kitchens[index][2], reply_markup=client_markup.generate_markup_like_kitchens(kitchens[index][0]))
        await bot.send_photo(message.from_user.id, caption=kitchens[-1][1], photo=kitchens[-1][2], reply_markup=client_markup.generate_markup_like_kitchens(kitchens[-1][0], is_last=True))
        await bot.send_message(message.from_user.id, text="Лайкай кухни из сообщений выше и затем нажми «Получить результат»")
    elif message.text == replicas.event:
        await bot.send_message(message.from_user.id, "Мероприятия", reply_markup=client_markup.event_markup)
    elif message.text == replicas.photo_day:
        # Фото день
        await FSMClient.choice_experts.set()
        async with state.proxy() as data:
            data["photographer"] = None
            data["visagiste"] = None
            data["stylist"] = None
            data["hairstylist"] = None
            data["photostudio"] = None
            data["expert_types"] = ["photographer", "visagiste", "stylist", "hairstylist", "photostudio"]
        await show_expert("photographer", message.from_user.id)

    elif message.text == replicas.drink:
        await bot.send_message(message.from_user.id, "Категории", reply_markup=client_markup.drink_markup)
    elif message.text == replicas.places_nearby_by_geolocation:
        await bot.send_message(message.from_user.id, "Выбери тип места", reply_markup=client_markup.geo_markup)
        await FSMGeo.enter_type_place.set()
    elif message.text == replicas.back:
        await bot.send_message(message.from_user.id, "Назад", reply_markup=client_markup.start_markup)
    elif message.text == replicas.favorite:
        places = db.get_favorites_places(message.from_user.id)
        if len(places) == 0:
            await bot.send_message(message.from_user.id, "Список избранных заведений пуст!")
        else:
            for place in places:
                if place[5] == "restaurant":
                    place_photos = db.get_restaurant_photo_by_id(place[0])
                else:
                    place_photos = db.get_place_photo_by_id(place[0])
                place_name = place[1]
                place_address = place[2]
                place_work_hours = place[3]
                caption = f"Информация о заведение - <b>{place_name}</b>:\n" \
                          f"Адрес: {place_address}\n" \
                          f"Часы работы: {place_work_hours}\n"

                if len(place_photos) == 0:
                    await bot.send_message(message.from_user.id, caption, parse_mode="HTML")
                else:
                    if len(place_photos) > 1:
                        media = types.MediaGroup()
                        for photo in place_photos:
                            media.attach_photo(photo[0])
                        await bot.send_media_group(message.from_user.id, media=media)
                        await bot.send_message(message.from_user.id, caption,
                                               parse_mode="HTML")
                    else:
                        await bot.send_photo(photo=place_photos[0][0], chat_id=message.from_user.id,
                                             caption=caption, parse_mode="HTML")


async def show_expert(expert_type, user_id):
    experts = db.get_experts_info_by_type(expert_type)
    if expert_type == "photographer":
        await bot.send_message(user_id, "Выберите фотографа")
    elif expert_type == "visagiste":
        await bot.send_message(user_id, "Выберите визажиста")
    elif expert_type == "stylist":
        await bot.send_message(user_id, "Выберите стилиста")
    elif expert_type == "hairstylist":
        await bot.send_message(user_id, "Выберите стилиста по волосам")
    elif expert_type == "photostudio":
        await bot.send_message(user_id, "Выберите фото-студию")
    for expert in experts:
        expert_photos = db.get_expert_photo_by_id(expert[0])
        expert_name = expert[2]
        expert_style = expert[3]
        expert_price = expert[4]
        expert_link = expert[5]
        caption = f"Информация о специалисте - <b>{expert_name}</b>:\n" \
                  f"Описание стиля: {expert_style}\n" \
                  f"Цена: {expert_price}\n" \
                  f"Ссылка на специалиста: {expert_link}\n"
        markup_ = client_markup.markup_like_experts(expert[0], expert_type)
        if len(expert_photos) == 0:
            await bot.send_message(user_id, caption, reply_markup=markup_, parse_mode="HTML", disable_web_page_preview=True)
        elif len(expert_photos) > 1:
            media = types.MediaGroup()

            for photo in expert_photos:
                media.attach_photo(photo[0])
            await bot.send_media_group(user_id, media=media)
            await bot.send_message(user_id, caption, reply_markup=markup_, parse_mode="HTML", disable_web_page_preview=True)
        else:
            await bot.send_photo(photo=expert_photos[0][0], chat_id=expert.from_user.id, reply_markup=markup_,
                                 caption=caption, parse_mode="HTML")


async def on_startup(_):
    await set_default_commands(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)