from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets, GoogleCredentials, OAuth2Credentials
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import client_ID

app = Flask(__name__)

# Load the client ID from the downloaded google client secret json file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Define the name of the application
APPLICATION_NAME = "Restaurant Menu Application"

# Connect to Database and create a database session
engine = create_engine('sqlite:///restaurantmenuwithusers.db',connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Route to: root and homepage of the app listing the restaurants
@app.route('/')
@app.route('/restaurants/')
def showRestaurants():

    # A variable to store the state of a user being logged in
    log_user = None
    # try to see if a user is currently logged in and assign a value
    # this will help toggle the login/logout buttons on a page
    try:
        log_user = login_session['google_user_id']
        print("User: " + str(user))
    except:
        print("No user is logged in")

    # Obtain a list of all the restaurants available from the database
    restaurants = session.query(Restaurant).all()

    # Render the page
    # restaurants: a list of the restaurants available to the app
    # log_in_stat: the id of the logged in user if available
    return render_template('restaurants.html',restaurants=restaurants, log_in_stat=log_user)

# Route to: JSON list of the restaurants available to the app
@app.route('/restaurants/JSON')
def showRestaurantsJSON():

    # Obtain a list of the restaurants available to the app
    restaurants = session.query(Restaurant).all()

    # Return a JSON version of the list of restaurants available
    return jsonify(Restaurants=[restaurant.serialize for restaurant in restaurants])

# Route to: Create a new restaurant page
@app.route('/restaurant/new/', methods=['POST', 'GET'])
def newRestaurant():
    # Check to see if a user is currently logged in to access the page
    if 'username' not in login_session:
        # If a user is not logged in redirect the user to the login page
        return redirect('/login')

    # Check to see if there is a POST request from the interface
    if request.method == 'POST':
        # Create a new restaurant and commit it to the database
        # name: the name entered in the form
        # user_id: use the id of the logged in user
        restaurant = Restaurant(name=request.form['name'], user_id = login_session['user_id'])
        session.add(restaurant)
        session.commit()

        # Flash a message to the user that the restaurant addition was sucessful
        flash('New Restaurant Created!')

        # return the user to the list of restaurants
        return redirect(url_for('showRestaurants'))

    # keep the user in the new restaurant page
    return render_template('newRestaurant.html')

# Route to: Edit a restaurant page
@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['POST', 'GET'])
def editRestaurant(restaurant_id):
    # Check to see if a user is currently logged in to access the page
    if 'username' not in login_session:
        # If a user is not logged in redirect the user to the login page
        return redirect('/login')

    # Obtain the database entry for the selected restaurant
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    # Check to see if there is a POST request from the interface
    if request.method == 'POST':

        # If a name change was provided by the user, apply the change
        if request.form['name']:
            restaurant.name = request.form['name']

        # Commit the current state of the entry to the database
        session.add(restaurant)
        session.commit()

        # Flash a message to the user that the restaurant edit was sucessful
        flash('Restaurant Successfully Edited')

        # Return the user the restaurant list
        return redirect(url_for('showRestaurants'))

    # If there is no POST request then keep the user on the edit page
    else:
        return render_template('editRestaurant.html', restaurant_id=restaurant_id, restaurant=restaurant)

# Route to: Delete Restaurant Page
@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['POST', 'GET'])
def deleteRestaurant(restaurant_id):
    # Check to see if a user is currently logged in to access the page
    if 'username' not in login_session:
        # If a user is not logged in redirect the user to the login page
        return redirect('/login')

    # Check to see if there is a POST request from the interface
    if request.method == 'POST':

        # Obtain the database entry for the selected restaurant
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

        # Delete the entry and commit the change to the database
        session.delete(restaurant)
        session.commit()

        # Flash a message to the user that the restaurant deletion was sucessful
        flash('Restaurant Successfully Deleted')

        # Return the user to the list of restaurants
        return redirect(url_for('showRestaurants'))

    # If there is no POST request then keep the user on the edit page
    else:
        return render_template('deleteRestaurant.html', restaurant_id=restaurant_id)

# Route to: Restaurant's menu page
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):

    # Obtain the current menu database entry from the database
    menu = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()

    # Render the restaurant menu page
    # restaurant_id: the id of the restaurant the user clicked
    # menu: the obtained database entry of the menu containing the menu items
    return render_template("menu.html", restaurant_id=restaurant_id, menu=menu)

# Route to: JSON list of the restaurant's menu items
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def showMenuJSON(restaurant_id):

    # Obtain the menu items for the selected restaurant
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()

    # Return a JSON version of the list of menu items available
    return jsonify(MenuItems=[item.serialize for item in items])

# Route to: Add a new menu item page
@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['POST', 'GET'])
def newMenuItem(restaurant_id):
    # Check to see if a user is currently logged in to access the page
    if 'username' not in login_session:
        # If a user is not logged in redirect the user to the login page
        return redirect('/login')

    # Check to see if there is a POST request from the interface
    if request.method == 'POST':

        # Check to see if the user entered a name and price
        if request.form['name'] and request.form['price']:

            # create a new menu item with the given data
            menuItem = MenuItem(name=request.form['name'],course=request.form['course'],description=request.form['description'],price= "$"+request.form['price'], restaurant_id=restaurant_id, user_id=login_session['user_id'])

            # add and commit the new item to the database
            session.add(menuItem)
            session.commit()

            # Flash a message to the user that the item addition was sucessful
            flash('Menu Item Created!')

        # return the user to the restaurant menu page
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))

    # If there is no POST request then keep the user on the new page
    else:
        return render_template('newMenuItem.html', restaurant_id=restaurant_id)

# Route to: Edit menu item page
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['POST', 'GET'])
def editMenuItem(restaurant_id, menu_id):
    # Check to see if a user is currently logged in to access the page
    if 'username' not in login_session:
        # If a user is not logged in redirect the user to the login page
        return redirect('/login')

    # Obtain the database entry of the selected menu item
    menu = session.query(MenuItem).filter_by(id=menu_id).one()

    # Check to see if there is a POST request from the interface
    if request.method == 'POST':

        # If the user entered a new name, update it
        if request.form['name']:
            menu.name = request.form['name']

        # If the user changed the course, update it
        if request.form['course']:
            menu.course = request.form['course']

        # If the user changed the description, update it
        if request.form['description']:
            menu.description = request.form['description']

        # If the user changed the price, update it
        if request.form['price']:
            menu.price = "$" + request.form['price']

        # Add and commit the changes to the database
        session.add(menu)
        session.commit()

        # Flash a message to notify the user that the edit was succesfful
        flash('Menu Item Successfully Edited')

        # Return the user to the restaurant's menu page
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))

    # If there is no POST request then keep the user on the edit page
    else:
        return render_template('editMenuItem.html',restaurant_id=restaurant_id, menu_id=menu_id, menu=menu)

# Route to: delete menu item page
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['POST', 'GET'])
def deleteMenuItem(restaurant_id, menu_id):
    # Check to see if a user is currently logged in to access the page
    if 'username' not in login_session:
        # If a user is not logged in redirect the user to the login page
        return redirect('/login')

    # Check to see if there is a POST request from the interface
    if request.method == 'POST':

        # Obtain the menu item entry selected from the database
        menuItem = session.query(MenuItem).filter_by(id=menu_id).one()

        # Delete the item and commit the change to the database
        session.delete(menuItem)
        session.commit()

        # Flash a message to the user that the item was deleted Successfully
        flash('Menu Item Successfully Deleted')

        # Return the user to the restaurant's menu page
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))

    # If there is no POST request then keep the user on the delete page
    else:
        return render_template('deleteMenuItem.html', restaurant_id=restaurant_id, menu_id=menu_id)

# Route to: JSON page for a specific menu Item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def MenuItemJSON(restaurant_id, menu_id):

    # Obtain the database entry for the selected item
    item = session.query(MenuItem).filter_by(id=menu_id).one()

    # Return a JSON version of the item to the user
    return jsonify(MenuItem=[item.serialize])

# Route to: Application login page
@app.route('/login')
def showLogin():

    # Create a local state token to implement an anti-session-forgery check
    # randomise an alphanumeric code to represent the current session
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))

    # assign the state token to the state param of login_session variable
    login_session['state'] = state

    # Render the login Page
    # state: the state token for the current session
    # CLIENT_ID: the client id of the application available in the client secrets file
    return render_template('login.html', STATE=state, client_ID=CLIENT_ID)

# Route to: CONNECT - for 3rd party login with Google
@app.route('/gconnect', methods=['POST'])
def gconnect():

    # Validate state token received from Google against the available token
    if request.args.get('state') != login_session['state']:

        # Create and return a 401 error to the user that the tokens are not the same
        response = make_response(json.dumps('Invalid state token'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # If this request does not have `X-Requested-With` header, this could be a CSRF
    if not request.headers.get('X-Requested-With'):
        abort(403)

    # Obtain the authorization code received from Google
    code = request.data

    # Try to obtain a credentials object from the authorization code received from Google
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    # notify the user that a credentials object could not be obtained from the authorization code provided by the server
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid by using it to make a call to Google
    access_token = credentials.access_token

    # Assemble the url, call Google's servers, and save the result
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # Check the resul of the call, if there was an error in the access token info, abort.
    if result.get('error') is not None:

        # Notify the user of the Google Server error, 500
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # obtain the user id within the credentials object used to make the connection request
    google_user_id = credentials.id_token['sub']

    # Verify that the access token is used by the intended user
    if result['user_id'] != google_user_id:

        # notify the user that the user id of the request maker and of the information received don't match
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:

        # notify the user that the id of the client does not match the application's
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify if there's a stored access token and whether the user id is already stored, this means the user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_google_user_id = login_session.get('google_user_id')
    if stored_access_token is not None and google_user_id == stored_google_user_id:

        # notify the user that they're already logged in
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['google_user_id'] = google_user_id

    # Assemble the request, Get the user info data
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    # Assign the user info data received to the login session
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # the return variable containing the final connection/login information the user will see
    output = ''

    # get the user id associated with email from the database
    user_id = getUserID(login_session['email'])

    # if the user is not in the database
    if not user_id:

        # create a new user and obtain the id
        user_id = createUser(login_session)

        # notify the user that a new account has been created for them
        output += '<h2>A new user account has been created for you with the following information: %s </h2> </br></br></br></br>' % getUserInfo(user_id)

    # update/set the user id of the login session
    login_session['user_id'] = user_id

    # print the login info to the user
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    # flash a message to the user in the landing page to confirm the login
    flash("you are now logged in as %s" % login_session['username'])

    # return the html code to the login.html page for rendering
    return output

# Route to: DISCONNECT - Revoke a current user's token and reset their login-session with google
@app.route('/gdisconnect/')
def gdisconnect():

    # Obtain the current access token of the login session
    access_token = login_session.get('access_token')

    # If there's no token notify the user that no one is currently connected
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'

        # Redirect the user to the list of restaurants
        return redirect(url_for('showRestaurants'))

    # Verify the current login session access token with the Google server and revoke it
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # if the token is Successfully revoked, remove the associated local information
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['google_user_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        # build a Successfully disconnected response and code
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'

        # Redirect the user to the list of restaurants page
        return redirect(url_for('showRestaurants'))

    # if the token is not succes revoked, inform the user
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'

        # Redirect the user to the list of restaurants page
        return redirect(url_for('showRestaurants'))

# This function is used to create a new user and commit them to the database
def createUser(login_session):
    newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    return newUser.id

# This function is used to get the info of a user from the database
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

# This function is used to get the id of a user if it exists in the database
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        print("User ID is already available")
        return user.id
    except:
        print("User ID is not available")
        return None

# This is currently a debugging function to delete users
def deleteUser(email):
    users = session.query(User).filter_by(email=email).all()
    print (users)
    for user in users:

        session.delete(user)
        session.commit()

    users = session.query(User).filter_by(email=email).all()
    print (users)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
