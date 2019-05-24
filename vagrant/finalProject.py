from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db', connect_args={'check_same_thread': False})

Base.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html',restaurants=restaurants)

@app.route('/restaurant/new/', methods=['POST', 'GET'])
def newRestaurant():
    if request.method == 'POST':
        restaurant = Restaurant(name=request.form['name'])
        session.add(restaurant)
        session.commit()
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['POST', 'GET'])
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            restaurant.name = request.form['name']
        session.add(restaurant)
        session.commit()
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant_id=restaurant_id, restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['POST', 'GET'])
def deleteRestaurant(restaurant_id):
    if request.method == 'POST':
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        session.delete(restaurant)
        session.commit()
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleteRestaurant.html', restaurant_id=restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    menu = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return render_template("menu.html", restaurant_id=restaurant_id, menu=menu)

@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['POST', 'GET'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        if request.form['name']:
            menuItem = MenuItem(name=request.form['name'],course=request.form['course'],description=request.form['description'],price= "$"+request.form['price'], restaurant_id=restaurant_id)
            session.add(menuItem)
            session.commit()
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newMenuItem.html', restaurant_id=restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['POST', 'GET'])
def editMenuItem(restaurant_id, menu_id):
    menu = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            menu.name = request.form['name']

        if request.form['course']:
            menu.course = request.form['course']

        if request.form['description']:
            menu.description = request.form['description']

        if request.form['price']:
            menu.price = "$" + request.form['price']
        session.add(menu)
        session.commit()
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editMenuItem.html',restaurant_id=restaurant_id, menu_id=menu_id, menu=menu)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['POST', 'GET'])
def deleteMenuItem(restaurant_id, menu_id):
    if request.method == 'POST':
        menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
        session.delete(menuItem)
        session.commit()
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html', restaurant_id=restaurant_id, menu_id=menu_id)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
