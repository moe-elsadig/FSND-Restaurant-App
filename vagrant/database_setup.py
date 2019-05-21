# Configuration - import all of the necessary modules
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

# Class - represent the data in python
class Restaurant(Base):

    # Table - represents the specific table in the database
    __tablename__ = 'restaurant'

    # Mapping - connects the columns of the table to the class that represents it
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)

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

    @property
    def serialize(self):
        #Returns object data in easily serializeable format
        return {
            'name' : self.name,
            'description' : self.description,
            'id' : self.id,
            'price' : self.price,
            'course' : self.course,
        }


# Configuration - End of file
engine = create_engine('sqlite:///restaurantmenu.db')

# Base.metadata.create_all(engine)

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

myFirstRestaurant = Restaurant(name = "Pizza Palace")

session.add(myFirstRestaurant)
session.commit()
session.query(Restaurant).all()

cheesepizza = MenuItem(name = "Cheese Pizza", description = "Made with all natural ingredients and fresh mozzarella", course = "Entree", price = "$8.99", restaurant = myFirstRestaurant)

session.add(cheesepizza)
session.commit()
session.query(Restaurant).all()

firstResult = session.query(Restaurant).first()
print (firstResult.name)

# items = session.query(MenuItem).all()
# for item in items:
#     print (item.name)
# #
# veggieBurgers = session.query(MenuItem).filter_by(name = 'Veggie Burger')
# for veggieBurger in veggieBurgers:
#     print (veggieBurger.id)
#     print (veggieBurger.price)
#     print (veggieBurger.restaurant.name)
#     print ("\n")
#
# UrbanVeggieBurger = session.query(MenuItem).filter_by(id = 10).one()
# print(UrbanVeggieBurger.price)
# UrbanVeggieBurger.price = '$2.99'
# session.add(UrbanVeggieBurger)
# session.commit()
#
# print(UrbanVeggieBurger.price)
#
# def restaurant_list():
#
#     all_restaurants = session.query(Restaurant.id).all()
#     print (all_restaurants)
#     return all_restaurants
#
#
# restaurant_list()
