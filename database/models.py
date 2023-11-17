from sqlalchemy import BigInteger, String, Date, ForeignKey, insert
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from config import SQLALCHEMY_URL

engine = create_async_engine(SQLALCHEMY_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass


class Person(Base):
    __tablename__ = 'persons'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(30))
    phone: Mapped[str] = mapped_column(String(30))
    city: Mapped[str] = mapped_column(String(30))
    vehicle: Mapped[str] = mapped_column(String(30), default='')
    trips = relationship("Trip", back_populates="person", cascade="all, delete", passive_deletes=True,)


class Trip(Base):
    __tablename__ = 'trips'

    id: Mapped[int] = mapped_column(primary_key=True)
    place: Mapped[str] = mapped_column(String(30))
    date = mapped_column(Date)
    is_person_driver: Mapped[bool] = mapped_column()
    available_seats: Mapped[int] = mapped_column(BigInteger)
    number_of_persons: Mapped[int] = mapped_column(BigInteger)
    comments: Mapped[str] = mapped_column()
    person_tg_id = mapped_column(BigInteger, ForeignKey('persons.tg_id', ondelete="CASCADE"))
    person = relationship("Person", back_populates="trips")


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)