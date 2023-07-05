import sqlite3


class Database:

    def __init__(self, file_db):
        self.connection = sqlite3.connect(file_db)
        self.cursor = self.connection.cursor()


    def get_kitchens(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM kitchens").fetchall()

    def get_restaurant(self, kitchens):
        with self.connection:
            restaurants = []
            for kitchen in kitchens:
                query = self.cursor.execute("SELECT restaurants.id, restaurants.name, address, work_hours, link_to_yandex, latitude FROM restaurants LEFT JOIN kitchens ON restaurants.kitchen_id = kitchens.id WHERE kitchen_id IN (?)", (kitchen, )).fetchall()
                for item in query:
                    restaurants.append(item)
            return restaurants

    def get_drink_places(self, types_of_drink_places):
        with self.connection:
            result = []
            if "cafe" in types_of_drink_places:
                query_result = self.cursor.execute("SELECT * FROM drink_places WHERE type = 'Кафе'")
                for item in query_result:
                    result.append(item)
            if "bar" in types_of_drink_places:
                query_result = self.cursor.execute("SELECT * FROM drink_places WHERE type = 'Бары'")
                for item in query_result:
                    result.append(item)
            if "club" in types_of_drink_places:
                query_result = self.cursor.execute("SELECT * FROM drink_places WHERE type = 'Клубы'")
                for item in query_result:
                    result.append(item)
            return result

    def add_drink_place(self, photos, name, address, work_hours, link_to_yandex, latitude, place_type):
        with self.connection:
            self.cursor.execute("INSERT INTO drink_places (type, name, address, work_hours, link_to_yandex, latitude) VALUES (?, ?, ?, ?, ?, ?)", (place_type, name, address, work_hours, link_to_yandex, latitude))
            row_id = self.cursor.lastrowid
            for photo in photos:
                self.cursor.execute("INSERT INTO drink_place_photos (file_id, place_id) VALUES (?, ?)", (photo, row_id))

    def add_restaurant(self, kitchen_id, photos, name, address, work_hours, link_to_yandex, latitude):
        with self.connection:
            self.cursor.execute("INSERT INTO restaurants (kitchen_id, name, address, work_hours, link_to_yandex, latitude) VALUES (?, ?, ?, ?, ?, ?)", (kitchen_id, name, address, work_hours, link_to_yandex, latitude))
            row_id = self.cursor.lastrowid
            for photo in photos:
                self.cursor.execute("INSERT INTO restaurant_photos (file_id, restaurant_id) VALUES (?, ?)", (photo, row_id))

    def add_expert(self, expert_type, photos, name, description_style, price, link, calendar_id):
        with self.connection:
            self.cursor.execute("INSERT INTO experts (expert_type, expert_name, expert_style, expert_price, expert_link, expert_calendar_id) VALUES (?, ?, ?, ?, ?, ?)",
                                (expert_type, name, description_style, price, link, calendar_id))
            row_id = self.cursor.lastrowid
            for photo in photos:
                self.cursor.execute("INSERT INTO expert_photos (file_id, expert_id) VALUES (?, ?)", (photo, row_id))

    def get_name_restaurants(self, kitchen_id):
        with self.connection:
            return self.cursor.execute("SELECT id, name FROM restaurants WHERE kitchen_id = ?", (kitchen_id, )).fetchall()

    def get_restaurant_by_id(self, restaurant_id):
        with self.connection:
            return self.cursor.execute("SELECT name, address, work_hours, link_to_yandex, latitude FROM restaurants WHERE id = ?", (restaurant_id, )).fetchall()

    def get_restaurant_photo_by_id(self, restaurant_id):
        with self.connection:
            return self.cursor.execute("SELECT file_id FROM restaurant_photos WHERE restaurant_id = ?", (restaurant_id, )).fetchall()

    def delete_restaurant(self, restaurant_id):
        with self.connection:
            self.cursor.execute("DELETE FROM restaurant_photos WHERE restaurant_id = ?", (restaurant_id, ))
            self.cursor.execute("DELETE FROM restaurants WHERE id = ?", (restaurant_id, ))

    def get_place_name_by_type(self, type):
        with self.connection:
            return self.cursor.execute("SELECT id, name FROM drink_places WHERE type = ?", (type, )).fetchall()

    def get_place_by_id(self, place_id):
        with self.connection:
            return self.cursor.execute("SELECT name, address, work_hours, link_to_yandex, latitude FROM drink_places WHERE id = ?", (place_id, )).fetchall()

    def get_place_photo_by_id(self, place_id):
        with self.connection:
            return self.cursor.execute("SELECT file_id FROM drink_place_photos WHERE place_id = ?", (place_id, )).fetchall()

    def delete_place(self, place_id):
        with self.connection:
            self.cursor.execute("DELETE FROM drink_place_photos WHERE place_id = ?", (place_id, ))
            self.cursor.execute("DELETE FROM drink_places WHERE id = ?", (place_id, ))

    def get_experts_name_by_type(self, expert_type):
        with self.connection:
            return self.cursor.execute("SELECT expert_id, expert_name FROM experts WHERE expert_type = ?", (expert_type, )).fetchall()

    def get_experts_info_by_type(self, expert_type):
        with self.connection:
            return self.cursor.execute("SELECT * FROM experts WHERE expert_type = ?", (expert_type, )).fetchall()


    def get_expert_by_id(self, expert_id):
        with self.connection:
            return self.cursor.execute("SELECT expert_name, expert_style, expert_price, expert_link, expert_calendar_id FROM experts WHERE expert_id = ?", (expert_id, )).fetchall()

    def get_expert_photo_by_id(self, expert_id):
        with self.connection:
            return self.cursor.execute("SELECT file_id FROM expert_photos WHERE expert_id = ?", (expert_id, )).fetchall()

    def delete_expert(self, expert_id):
        with self.connection:
            self.cursor.execute("DELETE FROM expert_photos WHERE expert_id = ?", (expert_id, ))
            self.cursor.execute("DELETE FROM experts WHERE expert_id = ?", (expert_id, ))

    def get_random_3_drink_place_by_type(self, drink_place_type):
        with self.connection:
            return self.cursor.execute("SELECT * FROM drink_places WHERE type = ? ORDER BY RANDOM() LIMIT 3", (drink_place_type, )).fetchall()

    def get_restaurants_for_geo(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM restaurants").fetchall()

    def is_favorite_place(self, user_id, place_id):
        with self.connection:
            return bool(len(self.cursor.execute("SELECT * FROM favorite_drink_places WHERE user_id = ? AND drink_place_id = ?", (user_id, place_id)).fetchmany(1)))

    def is_favorite_restaurant(self, user_id, restaurant_id):
        with self.connection:
            return bool(
                len(self.cursor.execute("SELECT * FROM favorite_restaurants WHERE user_id = ? AND restaurant_id = ?",
                                        (user_id, restaurant_id)).fetchmany(1)))

    def add_favorite(self, type_place, place_id, user_id):
        with self.connection:
            if type_place == "restaurant":
                if not bool(len(self.cursor.execute("SELECT * FROM favorite_restaurants WHERE user_id = ? AND restaurant_id = ?", (user_id, place_id)).fetchmany(1))):
                    self.cursor.execute("INSERT INTO favorite_restaurants (user_id, restaurant_id) VALUES (?, ?)", (user_id, place_id))
            else:
                if not bool(len(self.cursor.execute("SELECT * FROM favorite_drink_places WHERE user_id = ? AND drink_place_id = ?", (user_id, place_id)).fetchmany(1))):
                    self.cursor.execute("INSERT INTO favorite_drink_places (user_id, drink_place_id) VALUES (?, ?)", (user_id, place_id))

    def delete_favorite(self, type_place, place_id, user_id):
        with self.connection:
            if type_place == "restaurant":
                self.cursor.execute("DELETE FROM favorite_restaurants WHERE user_id = ? AND restaurant_id = ?",
                                    (user_id, place_id))
            else:
                self.cursor.execute("DELETE FROM favorite_drink_places WHERE user_id = ? AND drink_place_id = ?",
                                    (user_id, place_id))

    def get_favorites_places(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT id, name, address, work_hours, link_to_yandex, 'place' FROM favorite_drink_places "
                                       "LEFT JOIN drink_places ON drink_places.id = favorite_drink_places.drink_place_id WHERE user_id = ? "
                                       "UNION "
                                       "SELECT id, name, address, work_hours, link_to_yandex, 'restaurant' FROM favorite_restaurants "
                                       "LEFT JOIN restaurants ON restaurants.id = favorite_restaurants.restaurant_id WHERE user_id = ?",
                                       (user_id, user_id)).fetchall()

    def add_kitchen(self, name, photo):
        with self.connection:
            self.cursor.execute("INSERT INTO kitchens (name, photo) VALUES (?, ?)", (name, photo))

    def add_payment(self, user_id, bill, price, date):
        with self.connection:
            self.cursor.execute("INSERT INTO payments (user_id, payment_id, price, date, state) VALUES (?, ?, ?, ?, 'Не оплачено')", (user_id, bill, price, date))

