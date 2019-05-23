from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db', connect_args={'check_same_thread': False})

Base.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


"""
Routings:

ShowRestaurants()   :   /
                    :   /Restaurants

newRestaurant()     :   /restaurant/new

editRestaurant()    :   /restaurant/restaurant_id/edit

deleteRestaurant()  :   /restaurant/restaurant_id/delete

showMenu()          :   /restaurant/restaurant_id
                    :   /restaurant/restaurant_id/menu

newMenuItem()       :   /restaurant/restaurant_id/menu/new

editMenuItem()      :   /restaurant/restaurant_id/menu/menu_id/edit

deleteMenuItem()      :   /restaurant/restaurant_id/menu/menu_id/delete
"""

@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html',restaurants=restaurants)

@app.route('/restaurant/new/')
def newRestaurant():
    return render_template('newRestaurant.html')

@app.route('/restaurant/restaurant_id/edit/')
def editRestaurant():
    return "edit restaurant"

@app.route('/restaurant/restaurant_id/delete/')
def deleteRestaurant():
    return "delete restaurant"

@app.route('/restaurant/restaurant_id/')
@app.route('/restaurant/restaurant_id/menu/')
def showMenu():
    return "menu"

@app.route('/restaurant/restaurant_id/menu/new/')
def newMenuItem():
    return "new Menu Item"

@app.route('/restaurant/restaurant_id/menu/menu_id/edit')
def editMenuItem():

    return render_template('editMenuItem.html',restaurants="")

@app.route('/restaurant/restaurant_id/menu/menu_id/delete')
def deleteMenuItem():
    return "delete Menu Item"


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
