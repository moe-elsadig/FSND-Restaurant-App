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

@app.route('/restaurant/<int:restaurant_id>/edit/')
def editRestaurant(restaurant_id):
    return render_template('editRestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/delete/')
def deleteRestaurant(restaurant_id):
    return render_template('deleteRestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu = session.query(MenuItem).filter_by(restaurant_id=restaurant.id).all()
    return render_template("menu.html", restaurant_id=restaurant_id, menu=menu)

@app.route('/restaurant/<int:restaurant_id>/menu/new/')
def newMenuItem(restaurant_id):
    return render_template('newMenuItem.html')

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit')
def editMenuItem(restaurant_id, menu_id):
    return render_template('editMenuItem.html')

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete')
def deleteMenuItem(restaurant_id, menu_id):
    return render_template('deleteMenuItem.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
