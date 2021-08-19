from app import db

def fetch_shows() -> dict:
    conn = db.connect()
    query_results = conn.execute("SELECT DISTINCT ShowId, ShowName, ReleaseYear, Duration, Genre, AgeRating, Ratings \
                                  FROM Shows ORDER BY Ratings DESC, ShowName ASC LIMIT 20;").fetchall()
    conn.close()
    showList = []
    for result in query_results:
        show = {
            "ShowId": result[0],
            "ShowName": result[1][:58]+"..." if type(result[1]) == str and len(result[1]) > 59 else result[1],
            "ReleaseYear": result[2],
            "Duration": result[3],
            "Genre": result[4][:23]+"..." if type(result[4]) == str and len(result[4]) > 24 else result[4],
            "AgeRating": result[5],
            "Ratings": result[6]
        }
        showList.append(show)
    return showList

def search_shows(keywords: str, services: list) -> dict:
    # If necessary, build additional SQL args to handle
    # filtering by streaming service.
    serv = ""
    join = ""
    if len(services) > 0:
        join = " NATURAL JOIN AvailableOn"
        serv = " AND ("
        for service in services:
            serv += "ServiceId = " + service + " OR "
        serv = serv[:-4] + ")"

    conn = db.connect()
    query = 'SELECT DISTINCT ShowId, ShowName, ReleaseYear, Duration, Genre, AgeRating, Ratings \
             FROM Shows{} WHERE ShowName LIKE \'%%{}%%\'{} \
             ORDER BY Ratings DESC, ShowName ASC;'.format(join, keywords, serv)
    query_results = conn.execute(query).fetchall()
    conn.close()
    showList = []
    for result in query_results:
        show = {
            "ShowId": result[0],
            "ShowName": result[1][:58]+"..." if type(result[1]) == str and len(result[1]) > 59 else result[1],
            "ReleaseYear": result[2],
            "Duration": result[3],
            "Genre": result[4][:23]+"..." if type(result[4]) == str and len(result[4]) > 24 else result[4],
            "AgeRating": result[5],
            "Ratings": result[6]
        }
        showList.append(show)

    return showList

def execute_advanced_query() -> dict:
    conn = db.connect()
    query = 'SELECT ShowName, ReleaseYear, AvgUserRating FROM Shows s NATURAL JOIN (SELECT ShowId, AVG(UserRating) AS AvgUserRating FROM UserReviews GROUP BY ShowId) AS temp WHERE s.ReleaseYear >= 1980 AND s.ReleaseYear <= 1989 ORDER BY AvgUserRating DESC;'
    query_results = conn.execute(query).fetchall()
    conn.close()
    showList = []
    for result in query_results:
        show = {
            "ShowName": result[0],
            "ReleaseYear": result[1],
            "AvgUserRating": result[2]
        }
        showList.append(show)
    return showList

# ----------------- start watchlist db functions ----------------------

def getWatchlists(username: str) -> dict:
    conn = db.connect()
    query = f'SELECT UserId FROM Users WHERE Username="{username}";'
    query_results = conn.execute(query).fetchall()
    userid = query_results[0][0]

    query = f'SELECT ListName, ShowName, WatchType, ListId, ShowId FROM Watchlist NATURAL LEFT JOIN Contains NATURAL LEFT JOIN Shows WHERE UserId={userid};'
    query_results = conn.execute(query).fetchall()
    conn.execute(query)
    conn.close()
    watchlists = {}
    for result in query_results:
        # If Empty Watchlist
        if result[1] is None:
            watchlists[result[0]] = [result[3], None]
            continue
        showlist = watchlists.get(result[0])
        if showlist is None:
            showlist = [[],[],[],[]]
            showlist[result[2]].append([result[4], result[1]])
            watchlists[result[0]] = [result[3], showlist]
        else:
            shows = showlist[1]
            shows[result[2]].append([result[4], result[1]])
            watchlists[result[0]] = [result[3], shows]

    #Output format
    # Watchlists is a dictionary with the key as the ListName
    # The value is a list formatted as [ListId, Shows].
    # Shows is another list where there are 4 indices for
    # each Watchtype ([Watchtype 0, Watchtype 1, Watchtype 2, Watchtype 3]).
    # Each watchtype index in the shows list is another list of two-valued lists.
    # The list stores all the shows that have that specific watchtype. Each show entry
    # is a list of format [ShowId, ShowName]. 
    return watchlists

def editWatchlist(ListId: int, ListName: str) -> None:
    conn = db.connect()
    query = f'UPDATE Watchlist SET ListName="{ListName}" WHERE ListId="{ListId}";'
    conn.execute(query)
    conn.close()

def deleteWatchlist(ListId: int) -> None:
    conn = db.connect()
    query = f'DELETE FROM Watchlist WHERE ListId={ListId};'
    conn.execute(query)
    conn.close()

def addWatchlist(Username: str, ListName: str) -> int:
    UserId = get_userid_from_username(Username)
    conn = db.connect()
    query = f'INSERT INTO Watchlist(UserId, ListName) VALUES ({UserId}, "{ListName}");'
    conn.execute(query)
    query_results = conn.execute("SELECT LAST_INSERT_ID();")
    query_results = [x for x in query_results]
    ListId = query_results[0][0]
    conn.close()
    return ListId

def deleteWatchlistEntry(ListId: int, ShowId: int) -> None:
    conn = db.connect()
    query = f'DELETE FROM Contains WHERE ListId={ListId} AND ShowId={ShowId};'
    conn.execute(query)
    conn.close()

def editWatchlistEntry(ListId: int, ShowId: int, Watchtype: int, newListId: int) -> None:
    conn = db.connect()
    query = f'UPDATE Contains SET ListId={newListId}, Watchtype={Watchtype} WHERE ListId={ListId} AND ShowId={ShowId};'
    conn.execute(query)
    conn.close()

def addWatchlistEntry(ListId: int, ShowId: int, Watchtype: int) -> int:
    conn = db.connect()
    query = f'INSERT INTO Contains(ListId, ShowId, Watchtype) VALUES ({ListId}, {ShowId}, {Watchtype});'
    conn.execute(query)
    query_results = conn.execute("SELECT LAST_INSERT_ID();")
    query_results = [x for x in query_results]
    ListId = query_results[0][0]
    conn.close()
    return ListId 
# ------------------ end watchlist db functions ----------------------
# ----------------- start user login db functions ----------------------

def get_user_from_id(userid: int) -> dict:
    conn = db.connect()
    query = f'SELECT * FROM Users WHERE UserId={userid};'
    query_results = conn.execute(query).fetchall()
    conn.execute(query)
    conn.close()
    users = []
    for result in query_results:
        user = {
            "UserId": result[0],
            "Username": result[1],
            "Password": result[2],
            "Email": result[3],
            "Age": result[4],
            "Name": result[5]
        }
        users.append(user)
    return users 

def get_userid_from_username(username: str) -> int:
    conn = db.connect()
    query = f'SELECT UserId FROM Users WHERE Username="{username}";'
    query_results = conn.execute(query).fetchall()
    conn.execute(query)
    conn.close()
    return query_results[0][0]

def get_user_by_username(username: str) -> list:
    conn = db.connect()
    query = f'SELECT * FROM Users WHERE Username="{username}";'
    query_results = conn.execute(query).fetchall()
    conn.execute(query)
    conn.close()
    users = []
    for result in query_results:
        user = {
            "UserId": result[0],
            "Username": result[1],
            "Password": result[2],
            "Email": result[3],
            "Age": result[4],
            "Name": result[5]
        }
        users.append(user)
    return users 

def insert_user(username: str, password: str, email: str, age: int, name: str, services: list):
    conn = db.connect()
    query = f'INSERT INTO Users(Username, Password, Email, Age, Name) VALUES ("{username}", "{password}", "{email}", {age}, "{name}");'
    conn.execute(query)
    query_results = conn.execute("SELECT LAST_INSERT_ID();")
    query_results = [x for x in query_results]
    UserId = query_results[0][0]
    conn.close()

    update_user_services(username, services)

    return UserId

def delete_user(username: str) -> None:
    conn = db.connect()
    query = f'DELETE FROM Users WHERE Username="{username}";'
    conn.execute(query)
    conn.close()

def update_user(username: str, password: str, email: str, age: int, name: str, services: list):

    userid = get_userid_from_username(username)

    conn = db.connect()
    query = f'UPDATE Users SET Password="{password}", Email="{email}", Age={age}, Name="{name}" WHERE UserId="{userid}";'
    conn.execute(query)
    conn.close()

    update_user_services(username, services)

def get_user_services(userid: int) -> list:
    conn = db.connect()
    query = f'SELECT ServiceId FROM Uses WHERE UserId={userid}'
    query_results = conn.execute(query)
    conn.close()

    return [x[0] for x in query_results]

def update_user_services(username: str, services: list):
    userid = get_userid_from_username(username)
    old_services = get_user_services(userid)
    
    conn = db.connect()

    for service in services:
        if service not in old_services:
            query = f'INSERT INTO Uses(UserId, ServiceID) VALUES ({userid}, {service})'
            conn.execute(query)
    for old_service in old_services:
        if old_service not in services:
            query = f'DELETE FROM Uses WHERE UserId={userid} AND ServiceId={old_service}'
            conn.execute(query)

    conn.close()

# -------------------- end user login db functions --------------------

def get_show_details(showId: int) -> dict:
    conn = db.connect()
    query = f'SELECT ShowId, ShowName, ReleaseYear, Duration, Genre, Ratings, AgeRating, Description, ServiceName FROM Shows s NATURAL JOIN AvailableOn NATURAL JOIN StreamingServices \
             WHERE s.ShowId = {showId}'
    query_results = conn.execute(query).fetchall()
    conn.close()

    show = {
        "ShowId": query_results[0][0],
        "ShowName": query_results[0][1],
        "ReleaseYear": query_results[0][2],
        "Duration": query_results[0][3],
        "Genre": query_results[0][4],
        "Ratings": query_results[0][5],
        "AgeRating": query_results[0][6],
        "Description": query_results[0][7],
        "ServiceName": [],
        "ServiceCSSTag": [],
        "NumServices": 0
    }

    for result in query_results:
        if result[8] == "Netflix":
            show["ServiceName"].append("Netflix")
            show["ServiceCSSTag"].append("cb-netflix")
        elif result[8] == "Prime Video":
            show["ServiceName"].append("Prime")
            show["ServiceCSSTag"].append("cb-prime")
        elif result[8] == "Hulu":
            show["ServiceName"].append("Hulu")
            show["ServiceCSSTag"].append("cb-hulu")
        elif result[8] == "Disney+":
            show["ServiceName"].append("Disney+")
            show["ServiceCSSTag"].append("cb-disney")
    
    show["NumServices"] = len(show["ServiceName"])

    return show
    

# ----------------- UserReviews CRUD operations --------------------
def sql_update_review(showid: int, uid:int, rating: int, text: str) -> None:
    """ Updates a review by a given user on a given show

    Args:
        showid (int):   id of the review's show
        uid (int):      id of the review's user
        rating (int):   user's rating of the show
        text (str):     updated review text

    Returns:
        None
    """

    conn = db.connect()
    query = f'UPDATE UserReviews SET ReviewText="{text}",UserRating={rating} WHERE UserId={uid} AND ShowId={showid};'
    conn.execute(query)
    conn.close()



def sql_create_review(showid: int, uid: int, rating: int, text: str) ->  int:
    """ Create a review by given user on a given show

    Args:
        showid (int):   id of the review's show
        uid (int):      id of the review's user
        rating (int):   user's rating of the show
        text (str):     new review text

    Returns: None
    """
    conn = db.connect()
    query = f'INSERT INTO UserReviews (UserId, ShowId, UserRating, ReviewText) VALUES ({uid}, {showid}, {rating}, "{text}");'
    conn.execute(query)
    conn.close()



def sql_delete_review(showid: int, uid: int) -> None:
    """ Delete a review by given user on a given show

    Args:
        uid (int):      id of the review's user
        showid (int):   id of the review's show
    
    Returns: None
    """
    conn = db.connect()
    query = f'DELETE FROM UserReviews WHERE UserId={uid} AND ShowId={showid};'
    conn.execute(query)
    conn.close()

def get_user_ratings(showId: int) -> dict:
    conn = db.connect()
    query = f'SELECT UserRating, ReviewText FROM UserReviews WHERE ShowId={showId};'
    query_results = conn.execute(query).fetchall()
    conn.close()
    userRatings = []
    for result in query_results:
        rating = {
            "UserRating": result[0],
            "ReviewText": result[1]
        }
        userRatings.append(rating)
    return userRatings

def getAuthUserReview(username: str, showId: int) -> dict:
    conn = db.connect()
    id_query = f'SELECT UserId FROM Users WHERE Username="{username}";'
    id_query_results = conn.execute(id_query).fetchall()
    userid = id_query_results[0][0]
    
    query = f'SELECT UserRating, ReviewText FROM UserReviews WHERE UserId={userid} AND ShowId={showId};'
    query_results = conn.execute(query).fetchall()
    conn.close()
    authUserReview = {}
    if len(query_results) > 0:
        authUserReview = {
            "UserRating": query_results[0][0],
            "ReviewText": query_results[0][1],
        }
    
    return authUserReview



# ----- Recommendations Function -----
def get_rec_shows(userid: int) -> list:
    reset = f'CALL recsSoftWipe({userid});'
    proc = f'CALL newRecs({userid});'

    connection = db.raw_connection()
    cursor = connection.cursor()
    cursor.execute(reset)
    connection.commit()
    cursor.execute(proc)
    connection.commit()
    connection.close()

    conn = db.connect()
    query = f"SELECT DISTINCT s.ShowId, s.ShowName, ReleaseYear, Duration, Genre, AgeRating, Ratings, Reason \
              FROM Shows s JOIN Recs r ON s.ShowId = r.ShowId \
              WHERE r.UserId={userid} \
              ORDER BY Ratings DESC,s.ShowName ASC;"
    query_results = conn.execute(query).fetchall()
    conn.close()

    recsList = []
    for result in query_results:
        show = {
            "ShowId": result[0],
            "ShowName": result[1][:58]+"..." if type(result[1]) == str and len(result[1]) > 59 else result[1],
            "ReleaseYear": result[2] if result[2] != None else "None",
            "Duration": result[3] if result[3] != None else "None",
            "Genre": result[4][:23]+"..." if type(result[4]) == str and len(result[4]) > 24 else result[4] if result[4] != None else "None",
            "AgeRating": result[5] if result[5] != None else "None",
            "Ratings": float(result[6]),
            "Reason": result[7]
        }
        recsList.append(show)

    return recsList