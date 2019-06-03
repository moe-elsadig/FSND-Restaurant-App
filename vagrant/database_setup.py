# Configuration - import all of the necessary modules
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


# Class - represent the data in python
class User(Base):

    # Table - represents the specific table in the database
    __tablename__ = 'user'

    # Mapping - connects the columns of the table to the class that represents it
    name = Column(String(250), nullable = False)
    id = Column(Integer, primary_key = True)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))


# Class - represent the data in python
class Restaurant(Base):

    # Table - represents the specific table in the database
    __tablename__ = 'restaurant'

    # Mapping - connects the columns of the table to the class that represents it
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


    @property
    def serialize(self):
        #Returns object data in easily serializeable format
        return {
            'name' : self.name,
            'id' : self.id,
            'user_id' : self.user_id
        }

# Class - represent the data in python
class MenuItem(Base):

    # Table - represents the specific table in the database
    __tablename__ = 'menu_item'

    # Mapping - connects the columns of the table to the class that represents it
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        #Returns object data in easily serializeable format
        return {
            'name' : self.name,
            'description' : self.description,
            'id' : self.id,
            'price' : self.price,
            'course' : self.course,
            'user_id' : self.user_id
        }


# Configuration - End of file
engine = create_engine('sqlite:///restaurantmenuwithusers.db')


Base.metadata.create_all(engine)

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()
