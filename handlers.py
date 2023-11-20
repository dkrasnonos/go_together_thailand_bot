import keyboards as kb
import utils

from database import requests
from datetime import datetime
from time import strptime, mktime
from aiogram.fsm.context import FSMContext
from aiogram.methods import EditMessageText
from aiogram.utils.formatting import Bold, Text, as_list, as_marked_section
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from states import *

router = Router()
person_profile = None

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    person_profile = await requests.get_profile(message.from_user.id)
    if person_profile is None:
        await state.set_state(PersonDataForm.is_driver)
        await message.answer('Выберите свою роль в поездке', reply_markup=kb.choose_role_kb)
    else:
        await message.answer('У вас уже есть профиль 🎫')
        await process_show_profile(message)


@router.callback_query(F.data == 'passenger')
@router.callback_query(F.data == 'driver')
async def person(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'passenger':
        await state.update_data(is_driver=False)
    else:
        await state.update_data(is_driver=True)
    await callback.message.answer('А теперь давайте заполним небольшую инфоромацию о себе. В дальнейшем вам нужно будет выбрать только детали поездки')
    if callback.from_user.full_name == '':
        await callback.message.answer('Введите имя')
        await state.set_state(PersonDataForm.name)
    else:
        await state.set_state(PersonDataForm.name)
        await state.update_data(name=callback.from_user.full_name)
        await state.set_state(PersonDataForm.phone)
        await callback.message.answer('Укажите ваш контактный номер')

@router.message(PersonDataForm.name)
async def process_person_name(message: Message, state: FSMContext):
    if utils.is_name_field_valid(message.text):
        await state.update_data(name=message.text)
        await state.set_state(PersonDataForm.phone)
        await message.answer('Укажите ваш контактный номер')
    else:
        await message.answer('Имя должно состоять из букв и быть от 2 до 30 символов')



@router.message(PersonDataForm.phone)
async def process_person_phone(message: Message, state: FSMContext):
    if utils.is_phone_field_valid(message.text):
        await state.update_data(phone=message.text)
        await state.set_state(PersonDataForm.city)
        await message.answer('Отлично, теперь выбери свой город из списка ниже. Если такого нет, напишите @d_krasnonos для его добавления', reply_markup=kb.create_cities_markup())
    else:
        await message.answer('Номер телефона должен быть от 6 до 16 символов и не содержать в себе буквы')


@router.callback_query(PersonDataForm.city)
async def process_person_city(callback: CallbackQuery, state: FSMContext):
    data = await state.update_data(city=callback.data)
    if data['is_driver'] is False:
        await requests.create_person_profile(tg_id=callback.from_user.id, name=data['name'], username=callback.from_user.username, phone=data['phone'], city=data['city'])
        person_profile = await requests.get_profile(tg_id=callback.from_user.id)
        text = as_list(
            as_marked_section(
                'Ваш профиль успешно создан!',
                '',
                Bold('👤Имя: ') + person_profile.name,
                Bold('🕶️Ссылка на профиль: ') + person_profile.username,
                Bold('📱Телефон: ') + person_profile.phone,
                Bold('🌇Город: ') + person_profile.city,
                marker=' '
            ),
            sep='\n\n'
        )
        await callback.message.answer(**text.as_kwargs())
        await callback.message.answer(text='Теперь укажите данные по поездке или скорректируйте профиль',
            reply_markup=kb.go_further_or_edit_markup)
        await state.clear()
    else:
        await callback.message.answer('Укажите ваше транспортное средство')
        await state.set_state(PersonDataForm.vehicle)



@router.message(PersonDataForm.vehicle)
async def process_person_vehicle(message: Message, state: FSMContext):
    if utils.is_vehicle_field_valid(message.text):
        data = await state.update_data(vehicle=message.text)
        await requests.create_person_profile(tg_id=message.from_user.id, name=data['name'],
                                             username=message.from_user.username, phone=data['phone'], city=data['city'],
                                             vehicle=data['vehicle'])
        person_profile = await requests.get_profile(tg_id=message.from_user.id)
        text = as_list(
            as_marked_section(
                'Ваш профиль успешно создан!',
                '',
                Bold('👤Имя: ') + person_profile.name,
                Bold('🕶️Ссылка на профиль: ') + person_profile.username,
                Bold('📱Телефон: ') + person_profile.phone,
                Bold('🛵Транспортное средство: ') + person_profile.vehicle,
                Bold('🌇Город: ') + person_profile.city,
                marker=' '
            ),
            sep='\n\n'
        )
        await message.answer(**text.as_kwargs())
        await message.answer(text='Теперь укажите данные по поездке или скорректируйте профиль',
                             reply_markup=kb.go_further_or_edit_markup)
        await state.clear()
    else:
        await message.answer('Название должно содержать от 2 до 30 символов и не содержать в себе ссылки')


@router.message(Command('create_trip'))
async def process_create_trip(message: Message, state: FSMContext):
    person_profile = await requests.get_profile(tg_id=message.from_user.id)
    if person_profile is None:
        await message.answer(
            'Ваш профиль пока не создан, заполните небольшую анкету по кнопке /start, это займет меньше минуты 😉')
    else:
        await message.answer(text='Куда хотите поехать?')
        await state.set_state(CreateTripDataForm.place)


@router.callback_query(F.data == 'create_trip')
async def process_create_trip(callback: CallbackQuery, state: FSMContext):
    person_profile = await requests.get_profile(tg_id=callback.from_user.id)
    if person_profile is None:
        await callback.message.answer(
            'Ваш профиль пока не создан, заполните небольшую анкету по кнопке /start, это займет меньше минуты 😉')
    else:
        await callback.message.answer(text='Куда хотите поехать?')
        await state.set_state(CreateTripDataForm.place)


@router.message(CreateTripDataForm.place)
async def process_enter_place(message: Message, state: FSMContext):
    if utils.is_place_field_valid(message.text):
        await state.update_data(place=message.text)
        await message.answer(text='Выберите дату поездки', reply_markup=kb.create_date_picker_markup())
        await state.set_state(CreateTripDataForm.date)
    else:
        await message.answer('Название места должно содержать от 3 до 15 символов и не включать в себя ссылки')


@router.callback_query(CreateTripDataForm.date)
async def process_enter_date(callback: CallbackQuery, state: FSMContext):
    date = strptime(f'{callback.data}-{datetime.now().year}', '%d %b-%Y')
    python_fromatted_date = datetime.fromtimestamp(mktime(date)).date()
    await state.update_data(date=python_fromatted_date)
    await callback.message.answer(text='Напишите количество человек, которые едут вместе с вами (0, если вы один)')
    await state.set_state(CreateTripDataForm.number_of_persons)


@router.message(CreateTripDataForm.number_of_persons)
async def process_enter_number_of_persons(message: Message, state: FSMContext):
    if utils.is_number_field_valid(message.text):
        await state.update_data(number_of_persons=message.text)
        person_profile = await requests.get_profile(tg_id=message.from_user.id)
        if person_profile.vehicle != '':
            await state.update_data(is_person_driver=True)
            await message.answer(text='Укажите количество свободных мест')
            await state.set_state(CreateTripDataForm.available_seats)
        else:
            await state.update_data(is_person_driver=False)
            await state.update_data(available_seats=0)
            await message.answer(text='Дополнительные комментарии к поездке')
            await state.set_state(CreateTripDataForm.comments)
    else:
        await message.answer('Необходимо ввести число от 0 до 9')



@router.message(CreateTripDataForm.available_seats)
async def process_enter_available_seats(message: Message, state: FSMContext):
    if utils.is_number_field_valid(message.text):
        await state.update_data(available_seats=int(message.text))
        await state.set_state(CreateTripDataForm.comments)
        await message.answer('Дополнительные комментарии к поездке')
    else:
        await message.answer('Необходимо ввести число от 0 до 9')



@router.message(CreateTripDataForm.comments)
async def process_enter_comments(message: Message, state: FSMContext):
    data = await state.update_data(comments=message.text)
    await requests.create_trip(message.from_user.id, data)
    await message.answer(text='Поездка успешно создана! Ниже представлен список попутчиков на ближайшие даты')
    await get_all_trips(message)
    await state.clear()


@router.message(Command('all_trips'))
async def get_all_trips(message: Message):
    profile = await requests.get_profile(message.from_user.id)
    if profile is None:
        await message.answer('Чтобы посмотреть актуальные поездки, заполните небольшую анкету по кнопке /start, это займет меньше минуты 😉')
    else:
        trip_items = await requests.get_all_trips(city=profile.city, tg_id=profile.tg_id)
        if len(trip_items) == 0:
            await message.answer(text='Поездок на ближайшую неделю из вашего города не найдено.\nПопробуйте изменить город в настройках /edit_profile')
        else:
            for item in trip_items:
                if item['person'].vehicle != '':
                    text = as_list(
                        as_marked_section(
                            Bold(item['trip'].date.strftime('%d %b')),
                            '',
                            Bold('👤Имя: ') + item['person'].name,
                            Bold('🕶️Ссылка на профиль: ') + item['person'].username,
                            Bold('📱Телефон: ') + item['person'].phone,
                            Bold('🛵Транспортное средство: ') + item['person'].vehicle,
                            Bold('👥Свободных мест: ') + item['trip'].available_seats,
                            Bold('👨‍👩‍👧‍👦Со мной в компании: ') + item['trip'].number_of_persons,
                            Bold('🏖Место: ') + item['trip'].place,
                            Bold('📝Комментарий к поездке: ') + item['trip'].comments,
                            marker=' '
                        ),
                        sep='\n\n'
                    )
                    await message.answer(**text.as_kwargs())
                else:
                    text = as_list(
                        as_marked_section(
                            Bold(item['trip'].date.strftime('%d %b')),
                            '',
                            Bold('👤Имя: ') + (item['person'].name),
                            Bold('🕶️Ссылка на профиль: ') + item['person'].username,
                            Bold('📱Телефон: ') + item['person'].phone,
                            Bold('👨‍👩‍👧‍👦Со мной в компании: ') + item['trip'].number_of_persons,
                            Bold('🏖Место: ') + item['trip'].place,
                            Bold('📝Комментарий к поездке: ') + item['trip'].comments,
                            marker=' '
                        ),
                        sep='\n\n'
                    )
                    await message.answer(**text.as_kwargs())


@router.callback_query(F.data == 'all_trips')
async def process_get_all_trips(callback: CallbackQuery):
    profile = await requests.get_profile(callback.from_user.id)
    if profile is None:
        await callback.message.answer('Чтобы посмотреть актуальные поездки, заполните небольшую анкету по кнопке /start, это займет меньше минуты 😉')
    else:
        trip_items = await requests.get_all_trips(city=profile.city, tg_id=profile.tg_id)
        if len(trip_items) == 0:
            await callback.message.answer(text='Поездок на ближайшую неделю из вашего города не найдено.\nПопробуйте изменить город в настройках /edit_profile')
        else:
            for item in trip_items:
                if item['person'].vehicle != '':
                    text = as_list(
                        as_marked_section(
                            Bold(item['trip'].date.strftime('%d %b')),
                            '',
                            Bold('👤Имя: ') + item['person'].name,
                            Bold('🕶️Ссылка на профиль: ') + item['person'].username,
                            Bold('📱Телефон: ') + item['person'].phone,
                            Bold('🛵Транспортное средство: ') + item['person'].vehicle,
                            Bold('👥Свободных мест: ') + item['trip'].available_seats,
                            Bold('👨‍👩‍👧‍👦Со мной в компании: ') + item['trip'].number_of_persons,
                            Bold('🏖Место: ') + item['trip'].place,
                            Bold('📝Комментарий к поездке: ') + item['trip'].comments,
                            marker=' '
                        ),
                        sep='\n\n'
                    )
                    await callback.message.answer(**text.as_kwargs())
                else:
                    text = as_list(
                        as_marked_section(
                            Bold(item['trip'].date.strftime('%d %b')),
                            '',
                            Bold('👤Имя: ') + (item['person'].name),
                            Bold('🕶️Ссылка на профиль: ') + item['person'].username,
                            Bold('📱Телефон: ') + item['person'].phone,
                            Bold('👨‍👩‍👧‍👦Со мной в компании: ') + item['trip'].number_of_persons,
                            Bold('🏖Место: ') + item['trip'].place,
                            Bold('📝Комментарий к поездке: ') + item['trip'].comments,
                            marker=' '
                        ),
                        sep='\n\n'
                    )
                    await callback.message.answer(**text.as_kwargs())


@router.message(Command('edit_profile'))
async def process_edit_profile(message: Message):
    person_profile = await requests.get_profile(tg_id=message.from_user.id)
    if person_profile is None:
        await message.answer('Ваш профиль пока не создан, заполните небольшую анкету по кнопке /start, это займет меньше минуты 😉')
    else:
        await message.answer(text='Выберите раздел профиля, который хотите поменять', reply_markup=kb.edit_profile_markup)


@router.callback_query(F.data == 'edit_profile')
async def process_edit_profile(callback: CallbackQuery):
    await callback.message.answer(text='Выберите раздел профиля, который хотите поменять', reply_markup=kb.edit_profile_markup)


@router.callback_query(F.data == 'name')
async def process_edit_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите новое имя')
    await state.set_state(EditProfileDataForm.name)


@router.message(EditProfileDataForm.name)
async def process_set_new_name(message: Message, state: FSMContext):
    if utils.is_name_field_valid(message.text):
        await requests.edit_name(tg_id=message.from_user.id, value=message.text)
        await message.answer(text='Имя успешно изменено')
        await state.clear()
    else:
        await message.answer('Имя должно состоять из букв и быть от 2 до 30 символов')


@router.message(Command('profile'))
async def process_show_profile(message: Message):
    person_profile = await requests.get_profile(tg_id=message.from_user.id)
    if person_profile is None:
        await message.answer('Ваш профиль пока не создан, заполните небольшую анкету по кнопке /start, это займет меньше минуты 😉')
    else:
        if person_profile.vehicle != '':
            text = as_list(
                as_marked_section(
                    'Для редактирования введите /edit_profile\n',
                    Bold('👤Имя: ') + person_profile.name,
                    Bold('🕶️Ссылка на профиль: ') + person_profile.username,
                    Bold('📱Телефон: ') + person_profile.phone,
                    Bold('🛵Транспортное средство: ') + person_profile.vehicle,
                    Bold('🌇Город: ') + person_profile.city,
                    marker=' '
                ),
                sep='\n\n'
            )
            await message.answer(**text.as_kwargs())
        else:
            text = as_list(
                as_marked_section(
                    'Для редактирования введите /edit_profile\n',
                    Bold('👤Имя: ') + person_profile.name,
                    Bold('🕶️Ссылка на профиль: ') + person_profile.username,
                    Bold('📱Телефон: ') + person_profile.phone,
                    Bold('🌇Город: ') + person_profile.city,
                    marker=' '
                ),
                sep='\n\n'
            )
            await message.answer(**text.as_kwargs())


@router.callback_query(F.data == 'phone')
async def process_edit_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите новый номер')
    await state.set_state(EditProfileDataForm.phone)


@router.message(EditProfileDataForm.phone)
async def process_set_new_name(message: Message, state: FSMContext):
    if utils.is_phone_field_valid(message.text):
        await requests.edit_phone(tg_id=message.from_user.id, value=message.text)
        await message.answer(text='Номер успешно изменен')
        await state.clear()
    else:
        await message.answer('Номер телефона должен быть от 6 до 16 символов и не содержать в себе буквы')


@router.callback_query(F.data == 'vehicle')
async def process_edit_name(callback: CallbackQuery, state: FSMContext):
    person_profile = await requests.get_profile(callback.from_user.id)
    await callback.message.answer('Введите новое траснпортное средство (для удаления введите /delete)')
    await state.set_state(EditProfileDataForm.vehicle)


@router.message(EditProfileDataForm.vehicle)
async def process_set_new_name(message: Message, state: FSMContext):
    if message.text == '/delete':
        await requests.edit_vehicle(tg_id=message.from_user.id, value='')
    elif utils.is_vehicle_field_valid(message.text):
        await requests.edit_vehicle(tg_id=message.from_user.id, value=message.text)
        await message.answer(text='Информация о транспортном средстве изменена')
        await state.clear()
    else:
        await message.answer('Название должно содержать от 2 до 30 символов и не содержать в себе ссылки')


@router.callback_query(F.data == 'city')
async def process_edit_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Выберите город из списка ниже. Если такого нет, напишите @d_krasnonos для его добавления', reply_markup=kb.create_cities_markup())
    await state.set_state(EditProfileDataForm.city)


@router.callback_query(EditProfileDataForm.city)
async def process_set_new_name(callback: CallbackQuery, state: FSMContext):
    await requests.edit_city(tg_id=callback.from_user.id, value=callback.data)
    await callback.message.answer(text='Город успешно изменен')
    await state.clear()


@router.message(Command('my_trips'))
async def process_get_my_trips(message: Message):
    person_profile = await requests.get_profile(tg_id=message.from_user.id)
    if person_profile is None:
        await message.answer(
            'Ваш профиль пока не создан, заполните небольшую анкету по кнопке /start, это займет меньше минуты 😉')
    else:
        my_trips = await requests.get_my_trips(message.from_user.id)
        text = ''
        if len(my_trips) == 0:
            await message.answer(
                'У вас пока нет актуальных созданных поездок. Создайте свою поездку с командой /create_trip 🛵')
        else:
            for trip in my_trips:
                if trip.is_person_driver is True:
                    text = as_list(
                        as_marked_section(
                            Bold('#' + str(trip.id)),
                            '',
                            Bold('📆Дата: ') + trip.date.strftime('%d %b'),
                            Bold('👥Свободных мест: ') + trip.available_seats,
                            Bold('👨‍👩‍👧‍👦Со мной в компании: ') + trip.number_of_persons,
                            Bold('🏖Место: ') + trip.place,
                            Bold('📝Комментарий к поездке: ') + trip.comments,
                            marker=' '
                        ),
                        sep='\n\n'
                    )
                else:
                    text = as_list(
                        as_marked_section(
                            Bold('#' + str(trip.id)),
                            '',
                            Bold('📆Дата: ') + trip.date.strftime('%d %b'),
                            Bold('👨‍👩‍👧‍👦Со мной в компании: ') + trip.number_of_persons,
                            Bold('🏖Место: ') + trip.place,
                            Bold('📝Комментарий к поездке: ') + trip.comments,
                            marker=' '
                        ),
                        sep='\n\n'
                    )
                await message.answer(**text.as_kwargs(), reply_markup=kb.edit_or_delete_trip_markup)


@router.callback_query(F.data == 'edit_trip')
async def process_edit_trip(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditTripDataForm.id)
    await state.update_data(id=callback.message.text[1:3])
    trip = await requests.get_trip_by_id(trip_id=callback.message.text[1:3])
    if trip.is_person_driver:
        await callback.message.answer('Какую информацию вы хотите изменить?', reply_markup=kb.choose_trip_property_for_update_driver_markup)
    else:
        await callback.message.answer('Какую информацию вы хотите изменить?', reply_markup=kb.choose_trip_property_for_update_passenger_markup)


@router.callback_query(F.data == 'edit_date', EditTripDataForm.id)
async def process_edit_date(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text='Выберите новую дату поездки', reply_markup=kb.create_date_picker_markup())
    await state.set_state(EditTripDataForm.date)


@router.callback_query(EditTripDataForm.date)
async def process_enter_new_date(callback: CallbackQuery, state: FSMContext):
    date = strptime(f'{callback.data}-{datetime.now().year}', '%d %b-%Y')
    python_fromatted_date = datetime.fromtimestamp(mktime(date)).date()
    data = await state.update_data(date=python_fromatted_date)
    await requests.update_date(data)
    await callback.message.answer(text='Дата успешно изменена ✅')
    await state.clear()


@router.callback_query(F.data == 'edit_place', EditTripDataForm.id)
async def process_edit_place(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditTripDataForm.place)
    await callback.message.answer('Введите новое место, которое хотите посетить')


@router.message(EditTripDataForm.place)
async def process_enter_new_place(message: Message, state: FSMContext):
    if utils.is_place_field_valid(message.text):
        data = await state.update_data(place=message.text)
        await requests.update_place(data)
        await message.answer('Место для посещения успешно обновлено ✅')
        await state.clear()
    else:
        await message.answer('Название место должно содержать от 5 до 15 символов и не включать в себя ссылки')


@router.callback_query(F.data == 'edit_available_seats', EditTripDataForm.id)
async def process_edit_available_seats(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditTripDataForm.available_seats)
    await callback.message.answer('Введите новое количество свободных мест')


@router.message(EditTripDataForm.available_seats)
async def process_enter_new_available_seats(message: Message, state: FSMContext):
    if utils.is_number_field_valid(message.text):
        data = await state.update_data(available_seats=int(message.text))
        await requests.update_available_seats(data)
        await message.answer('Количество свободных мест успешно обновлено ✅')
        await state.clear()
    else:
        await message.answer('Необходимо ввести число от 0 до 9')


@router.callback_query(F.data == 'edit_number_of_persons', EditTripDataForm.id)
async def process_edit_number_of_persons(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditTripDataForm.number_of_persons)
    await callback.message.answer('Введите новое количество человек в поездке с вами')


@router.message(EditTripDataForm.number_of_persons)
async def process_enter_new_number_of_persons(message: Message, state: FSMContext):
    if utils.is_number_field_valid(message.text):
        data = await state.update_data(number_of_persons=int(message.text))
        await requests.update_number_of_persons(data)
        await message.answer('Количество человек в поездке с вами успешно обновлено ✅')
        await state.clear()
    else:
        await message.answer('Необходимо ввести число от 0 до 9')

@router.callback_query(F.data == 'edit_comments', EditTripDataForm.id)
async def process_edit_comments(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditTripDataForm.comments)
    await callback.message.answer('Введите новый комментарий к поездке')


@router.message(EditTripDataForm.comments)
async def process_enter_new_comments(message: Message, state: FSMContext):
    if utils.is_comments_field_valid(message.text):
        data = await state.update_data(comments=message.text)
        await requests.update_comments(data)
        await message.answer('Комментарий успешно обновлен ✅')
        await state.clear()
    else:
        await message.answer('Данное поле должно содержать не более 30 символов и не включать в себя ссылки')


@router.callback_query(F.data == 'cancel', EditTripDataForm.id)
async def process_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer('Редактирование отменено. Список остальных команд доступен в меню')


@router.callback_query(F.data == 'delete_trip')
async def process_delete_trip(callback: CallbackQuery):
    trip_id = int(callback.message.text[1:3])
    await requests.delete_trip(trip_id)
    if await requests.is_trip_deleted(trip_id):
        return EditMessageText(text='Поездка удалена ✅', message_id=callback.message.message_id, chat_id=callback.message.chat.id)
    else:
        await callback.message.answer('❗️Что-то пошло не так. Попробуйте получить список своих поездок заново /my_trips')


@router.message(Command('find_trip'))
async def find_trips(message: Message, state: FSMContext):
    person_profile = await requests.get_profile(tg_id=message.from_user.id)
    if person_profile is None:
        await message.answer(
            'Ваш профиль пока не создан, заполните небольшую анкету по кнопке /start, это займет меньше минуты 😉')
    else:
        await message.answer('Выберите дату, по которой хотите совершить поиск, из списка ниже', reply_markup=kb.create_date_picker_markup())
        await state.set_state(FindTripByDateForm.city)
        await state.update_data(city=person_profile.city)
        await state.set_state(FindTripByDateForm.date)

@router.callback_query(FindTripByDateForm.date)
async def process_find_trips_by_date(callback: CallbackQuery, state: FSMContext):
    date = strptime(f'{callback.data}-{datetime.now().year}', '%d %b-%Y')
    python_fromatted_date = datetime.fromtimestamp(mktime(date)).date()
    data = await state.update_data(date=python_fromatted_date)
    trip_items = await requests.find_trips_by_date(data=data, tg_id=callback.from_user.id)
    await state.clear()
    if len(trip_items) == 0:
        await callback.message.answer('Поездок на данную дату из вашего города не найдено. Попробуйте выполнить поиск по другой дате или изменить свой город через /edit_profile')
    else:
        for item in trip_items:
            if item['person'].vehicle != '':
                text = as_list(
                    as_marked_section(
                        Bold(item['trip'].date.strftime('%d %b')),
                        '',
                        Bold('👤Имя: ') + item['person'].name,
                        Bold('🕶️Ссылка на профиль: ') + item['person'].username,
                        Bold('📱Телефон: ') + item['person'].phone,
                        Bold('🛵Транспортное средство: ') + item['person'].vehicle,
                        Bold('👥Свободных мест: ') + item['trip'].available_seats,
                        Bold('👨‍👩‍👧‍👦Со мной в компании: ') + item['trip'].number_of_persons,
                        Bold('🏖Место: ') + item['trip'].place,
                        Bold('📝Комментарий к поездке: ') + item['trip'].comments,
                        marker=' '
                    ),
                    sep='\n\n'
                )
                await callback.message.answer(**text.as_kwargs())
            else:
                text = as_list(
                    as_marked_section(
                        Bold(item['trip'].date.strftime('%d %b')),
                        '',
                        Bold('👤Имя: ') + (item['person'].name),
                        Bold('🕶️Ссылка на профиль: ') + item['person'].username,
                        Bold('📱Телефон: ') + item['person'].phone,
                        Bold('👨‍👩‍👧‍👦Со мной в компании: ') + item['trip'].number_of_persons,
                        Bold('🏖Место: ') + item['trip'].place,
                        Bold('📝Комментарий к поездке: ') + item['trip'].comments,
                        marker=' '
                    ),
                    sep='\n\n'
                )
                await callback.message.answer(**text.as_kwargs())

# Handler for unknown commands
@router.message(F.text)
async def process_unknown_command(message: Message):
    await message.answer('❗️Неизвестная команда. Выберите команду из списка меню')

