from flask import render_template, request, jsonify, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import quote
import json
import decimal
from decimal import Decimal
from app import app
from app import User
from app import login_manager as lm
from app import database as db_helper

# --------------- UserReview CRUD Operation URLs ------------------

@app.route("/review/edit/<int:showid>/<int:uid>", methods=['POST'])
def review_edit(showid, uid):
    """ recieved post requests for entry updates """

    data = request.get_json()
    rating = 10

    try:
        if "rating" in data:
            rating = data["rating"]
        if "description" in data:
            print("review:", data["description"])
            db_helper.sql_update_review(showid, uid, rating, data["description"])
            result = {'success': True, 'response': 'Review Updated'}
        else:
            result = {'success': True, 'response': 'Nothing Updated'}
    except:
        result = {'success': False, 'response': 'Something went wrong'}

    return jsonify(result)


@app.route("/review/create/<int:showid>/<int:uid>", methods=['POST'])
def review_create(showid, uid):
    """ recieves post requests to add new task """
    data = request.get_json()
    rating = 10
    
    try:
        if "rating" in data:
            rating = data["rating"]
        if "description" in data:
            db_helper.sql_create_review(showid, uid, rating, data["description"])
            result = {'success': True, 'response': 'Review Created'}
        else:
            result = {'success': True, 'response': 'Nothing Updated'}
    except:
        result = {'success': False, 'response': 'Something went wrong'}

    return jsonify(result)


@app.route("/review/delete/<int:showid>/<int:uid>", methods=['POST'])
def review_delete(showid, uid):
    """ recieved post requests for entry delete """

    try:
        db_helper.sql_delete_review(showid, uid)
        result = {'success': True, 'response': 'Review Deleted'}
    except:
        result = {'success': False, 'response': 'Something went wrong'}

    return jsonify(result)


# ----------------- End UserReview CRUD Operations ---------------------


# --------------------- Leftover Advanced Query ------------------------
@app.route("/advanced-query")
def advanced_query():
    shows = db_helper.execute_advanced_query()
    return render_template("advanced.html", shows=shows)


# ---------------------- Individual Show Pages -------------------------
@app.route("/show/<int:showId>")
def show(showId):
    details = db_helper.get_show_details(showId)
    userRatings = db_helper.get_user_ratings(showId)
    if current_user.is_authenticated:
        userId = db_helper.get_userid_from_username(current_user.id)
        watchlists = db_helper.getWatchlists(current_user.id)
        authUserReview = db_helper.getAuthUserReview(current_user.id, showId)
        return render_template("show.html", details = details, userRatings = userRatings, auth = True, userId = userId, watchlists = watchlists, authUserReview = authUserReview, url=quote(f'/user/{current_user.id}'), username=current_user.id)
    else:
        return render_template("show.html", details = details, userRatings = userRatings, auth = False, userId = None, watchlists = None, authUserReview = None, url=None, username=None)


# ---------------------- Recommendations Get --------------------------

@app.route("/search/recommendations", methods=['GET'])
@login_required
def recommendations():
    userId = db_helper.get_userid_from_username(current_user.id)
    recs = db_helper.get_rec_shows(userId)
    return jsonify(recs)


# ------------------------- Search Page --------------------------------

# Global variables for storing ongoing search info.
# Likely need to make into cookies to avoid conflicts.
init_search = ""
init_services = []

@app.route('/search', methods=['GET', 'POST'])
def search():
    global init_search, init_services

    # Code modified to handle for issues with jQuery not handling
    # redirect, and HTML form being unable to process the streaming
    # service checkboxes. Code uses POST as a means of storing the
    # search, then allows jQuery to call GET on the page to retrieve
    # the data. Alternative is to add query to search url or store
    # search in cookies somehow.

    if request.method == 'POST':
        data = request.get_json()
        init_search = data["keywords"]
        init_services = data["services"]
        return ""
    elif len(init_search) > 0:
        shows = db_helper.search_shows(init_search, init_services)
    else:
        shows = db_helper.fetch_shows()
    if current_user.is_authenticated:
        return render_template("search.html", shows=shows, logged_in=True, url=quote(f'/user/{current_user.id}'), username=current_user.id, services=db_helper.get_user_services(db_helper.get_userid_from_username(current_user.id)))
    else:
        return render_template("search.html", shows=shows, logged_in=False, url=None, username=None, services=[])

@app.route('/user/<string:username>', methods=['GET', 'POST'])
@login_required
def userpage(username):
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return
        username = data['username']
        password = data['password']
        email = data['email']
        age = data['age']
        name = data['name']
        services = [int(x) for x in data['services']]


        if not age:
            age = 0

        db_helper.update_user(username, password, email, age, name, services)
        return redirect('/user/' + quote(username))
    if current_user.id != username:
        return render_template("userpage.html", userinfo=None, auth=False)
    else:
        userinfo = db_helper.get_user_by_username(username)[0]
        watchlists = db_helper.getWatchlists(username)
        services = db_helper.get_user_services(userinfo["UserId"])
        return render_template("userpage.html", userinfo=userinfo, watchlists=watchlists, services=services, auth=True)

# -------------------------- Root Page --------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    global init_search, init_services

    # Code modified to enable passing multiple items
    # of data, which HTML form didn't allow without
    # drastic alteration of code.

    if request.method == 'POST':
        data = request.get_json()
        
        init_search = data['keywords']
        init_services = data['services']
        return redirect(url_for('search'))

    if current_user.is_authenticated:
        return render_template("index.html", logged_in=True, url=quote(f'/user/{current_user.id}'), username=current_user.id, services=db_helper.get_user_services(db_helper.get_userid_from_username(current_user.id)))
    else:
        return render_template("index.html", logged_in=False, url=None, username=None, services=[])
    
#-------------------- user login --------------------------
@lm.user_loader
def user_loader(username):
    users = db_helper.get_user_by_username(username)

    if not users:
        return
    
    user = User()
    user.id = username
    
    return user

@lm.request_loader
def request_loader(request):
    data = request.get_json()
    if not data:
        return
    username = data['Username']
    password = data['Password']

    results = db_helper.get_user_by_username(username)
    if not results or len(results) > 1:
        return

    stored_pass = results[0]['Password']

    user = User()
    user.id = username
    user.is_authenticated = stored_pass == password

    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return
        username = data['username']
        password = data['password']

        results = db_helper.get_user_by_username(username)
        if not results or len(results) > 1:
            return "Invalid Username/Password"
        
        stored_pass = results[0]['Password']
        if stored_pass == password:
            user = User()
            user.id = username
            login_user(user)
            return '<h2 class="model-title">Login Successful.</h2>'

        return "Invalid Username/Password"

@app.route('/new', methods=['GET', 'POST'])
def new_user():
    if request.method == 'GET':
        return render_template("newuser.html")
    else:
        data = request.get_json()
        if not data:
            return
        username = data['username']
        password = data['password']
        email = data['email']
        age = data['age']
        name = data['name']
        services = [int(x) for x in data['services']]

        if username is None or username == '' or password is None or password == '':
            return '<h2 class="modal-title">Error: Username and Password fields must filled out.</h2>'

        results = db_helper.get_user_by_username(username)
        if len(results) > 0:
            return '<h2 class="modal-title">Error: Could not add user. Username already exists.</h2>'
        
        if not age:
            age = 0

        userid = db_helper.insert_user(username, password, email, age, name, services)
        if userid > 0:
            return '<h2 class="modal-title">Success: Added user!</h2>'

# --------------------- watchlist -------------------------    
@app.route('/editwt', methods=['POST'])
def editwt():
    data = request.get_json()
    if not data:
        return
    ListName = data['ListName']
    ListId = data['ListId']

    db_helper.editWatchlist(ListId, ListName)
    return "Success!"

@app.route('/deletewt', methods=['POST'])
def deletewt():
    data = request.get_json()
    if not data:
        return
    ListId = data['ListId']

    db_helper.deleteWatchlist(ListId)
    return "Success!"

@app.route('/deletewtentry', methods=['POST'])
def deletewtentry():
    data = request.get_json()
    if not data:
        return
    ListId = data['ListId']
    ShowId = data['ShowId']

    db_helper.deleteWatchlistEntry(ListId, ShowId)
    return "Success!"

@app.route('/editwtentry', methods=['POST'])
def editwtentry():
    data = request.get_json()
    if not data:
        return
    ListId = data['ListId']
    newListId = data['newListId']
    ShowId = data['ShowId']
    Watchtype = data['Watchtype']

    db_helper.editWatchlistEntry(ListId, ShowId, Watchtype, newListId)
    return "Success!"

@app.route('/addwtentry', methods=['POST'])
def addwtentry():
    data = request.get_json()
    if not data:
        return
    ListId = data['ListId']
    ShowId = data['ShowId']
    Watchtype = data['Watchtype']

    db_helper.addWatchlistEntry(ListId, ShowId, Watchtype)
    return "Success!"

@app.route('/addwt', methods=['POST'])
def addwt():
    data = request.get_json()
    if not data:
        return
    ListName = data['ListName']

    if current_user.is_authenticated:
        ListId = db_helper.addWatchlist(current_user.id, ListName)
        return "Success!" if ListId > 0 else "Failure!"
    else:
        return "Failure!"


@app.route('/logout')
def logout():
    logout_user()
    return render_template("logout.html")

@lm.unauthorized_handler
def unauthorized_login():
    return 'Unauthorized.'