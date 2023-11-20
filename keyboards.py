import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import CITIES as cities


passenger_button = InlineKeyboardButton(text='Пассажир', callback_data='passenger')
driver_button = InlineKeyboardButton(text='Водитель', callback_data='driver')

choose_role_kb = InlineKeyboardMarkup(inline_keyboard=[[passenger_button], [driver_button]])
go_further_or_edit_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Создать свою поездку', callback_data='create_trip')],
    [InlineKeyboardButton(text='Изменить профиль', callback_data='edit_profile')],
    [InlineKeyboardButton(text='Посмотреть существующие поездки', callback_data='all_trips')]
], resize_keyboard=True)


def create_cities_markup():
    buttons = [[]]
    i = 0
    j = 0
    for city in cities:
        i += 1
        if i % 3 == 0:
            j += 1
            buttons.append([])
        button = InlineKeyboardButton(text=city, callback_data=city)
        buttons[j].append(button)

    markup = InlineKeyboardMarkup(inline_keyboard=buttons, resize_keyboard=True)
    return markup


edit_profile_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Имя', callback_data='name'), InlineKeyboardButton(text='Телефон', callback_data='phone')],
     [InlineKeyboardButton(text='Город', callback_data='city'), InlineKeyboardButton(text='Транспорт', callback_data='vehicle')]
], resize_keyboard=True)


edit_or_delete_trip_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Редактировать', callback_data='edit_trip'), InlineKeyboardButton(text='Удалить', callback_data='delete_trip')]
], resize_keyboard=True)



choose_trip_property_for_update_driver_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Дата', callback_data='edit_date'), InlineKeyboardButton(text='Свободные места', callback_data='edit_available_seats')],
    [InlineKeyboardButton(text='Людей в компании', callback_data='edit_number_of_persons'), InlineKeyboardButton(text='Место', callback_data='edit_place')],
    [InlineKeyboardButton(text='Комментарий', callback_data='edit_comments'), InlineKeyboardButton(text='Отмена', callback_data='cancel')]
], resize_keyboard=True)


choose_trip_property_for_update_passenger_markup = InlineKeyboardMarkup(inline_keyboard=[
     [InlineKeyboardButton(text='Дата', callback_data='edit_date'),
     InlineKeyboardButton(text='Свободные места', callback_data='edit_available_seats')],
     [InlineKeyboardButton(text='Место', callback_data='edit_place'), InlineKeyboardButton(text='Комментарий', callback_data='edit_comments')],
     [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
], resize_keyboard=True)


def create_date_picker_markup():
    buttons = [[],[]]
    for i in range(7):
        button = InlineKeyboardButton(text=(datetime.date.today() + datetime.timedelta(days=i)).strftime('%d %b'),
                                      callback_data=(datetime.date.today() + datetime.timedelta(days=i)).strftime('%d %b'))
        if i > 3:
            buttons[1].append(button)
        else:
            buttons[0].append(button)
    markup = InlineKeyboardMarkup(inline_keyboard=buttons, resize_keyboard=True)
    return markup