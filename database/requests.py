from datetime import datetime
from database.models import Person, Trip, async_session
from sqlalchemy import select, delete


async def get_profile(tg_id):
    async with async_session() as session:
        result = await session.scalar(select(Person).where(Person.tg_id == tg_id))
        return result


async def create_person_profile(tg_id, name, username, phone, city, vehicle=''):
    async with async_session() as session:
        person = Person(tg_id=tg_id, name=name, username=f'@{username}', phone=phone, city=city, vehicle=vehicle)
        session.add(person)
        await session.commit()
        await session.close()


async def create_trip(tg_id, data):
    async with async_session() as session:
        trip = Trip(place=data['place'], date=data['date'], is_person_driver=data['is_person_driver'],
                    available_seats=data['available_seats'], number_of_persons=data['number_of_persons'],
                    comments=data['comments'], person_tg_id=tg_id)
        session.add(trip)
        await session.commit()
        await session.close()


async def get_trip_by_id(trip_id):
    async with async_session() as session:
        trip = await session.scalar(select(Trip).where(Trip.id == trip_id))
        return trip


async def get_all_trips(city, tg_id):
    async with async_session() as session:
        items = list()
        trips = await session.scalars(select(Trip).where(Trip.date >= datetime.now().date()).where(Trip.person_tg_id != tg_id))
        for trip in trips:
            person = await session.scalar(select(Person).where(Person.tg_id == trip.person_tg_id).where(Person.city == city))
            if person is not None:
                items.append({'person': person, 'trip': trip})
        return sorted(items, key=lambda item: item['trip'].date)


async def get_my_trips(tg_id):
    async with async_session() as session:
        trips = await session.scalars(select(Trip).where(Trip.date >= datetime.now().date()).where(Trip.person_tg_id == tg_id))
        return sorted(trips, key=lambda trip: trip.date)


async def is_trip_deleted(trip_id):
    async with async_session() as session:
        trip = await session.scalar(select(Trip).where(Trip.id == trip_id))
        if trip is None:
            return True
        else:
            return False


async def delete_trip(trip_id):
    async with async_session() as session:
        await session.execute(delete(Trip).where(Trip.id == trip_id))
        await session.commit()
        await session.close()

async def edit_name(tg_id, value):
    async with async_session() as session:
        pesron = await session.scalar(select(Person).where(Person.tg_id == tg_id))
        pesron.name = value
        await session.commit()
        await session.close()


async def edit_phone(tg_id, value):
    async with async_session() as session:
        pesron = await session.scalar(select(Person).where(Person.tg_id == tg_id))
        pesron.phone = value
        await session.commit()
        await session.close()


async def edit_city(tg_id, value):
    async with async_session() as session:
        pesron = await session.scalar(select(Person).where(Person.tg_id == tg_id))
        pesron.city = value
        await session.commit()
        await session.close()


async def edit_vehicle(tg_id, value):
    async with async_session() as session:
        pesron = await session.scalar(select(Person).where(Person.tg_id == tg_id))
        pesron.vehicle = value
        await session.commit()
        await session.close()

async def update_date(data):
    async with async_session() as session:
        trip = await session.scalar(select(Trip).where(Trip.id == data['id']))
        trip.date = data['date']
        await session.commit()
        await session.close()


async def update_place(data):
    async with async_session() as session:
        trip = await session.scalar(select(Trip).where(Trip.id == data['id']))
        trip.place = data['place']
        await session.commit()
        await session.close()


async def update_available_seats(data):
    async with async_session() as session:
        trip = await session.scalar(select(Trip).where(Trip.id == data['id']))
        trip.available_seats = data['available_seats']
        await session.commit()
        await session.close()


async def update_number_of_persons(data):
    async with async_session() as session:
        trip = await session.scalar(select(Trip).where(Trip.id == data['id']))
        trip.number_of_persons = data['number_of_persons']
        await session.commit()
        await session.close()


async def update_comments(data):
    async with async_session() as session:
        trip = await session.scalar(select(Trip).where(Trip.id == data['id']))
        trip.comments = data['comments']
        await session.commit()
        await session.close()


async def find_trips_by_date(data, tg_id):
    async with async_session() as session:
        items = list()
        trips = await session.scalars(select(Trip).where(Trip.date == data['date']).where(Trip.person_tg_id != tg_id))
        for trip in trips:
            person = await session.scalar(
                select(Person).where(Person.tg_id == trip.person_tg_id).where(Person.city == data['city']))
            if person is not None:
                items.append({'person': person, 'trip': trip})
        return sorted(items, key=lambda item: item['trip'].date)
