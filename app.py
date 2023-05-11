from flask import Flask, render_template, request, redirect, session, url_for #url_for lets me redirect to a function (the url for a route) in case the 
import os
import psycopg2
from flask_bcrypt import Bcrypt #i was having problems with other bcrypt, searched solution stack overflow they said use this library instead


app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config["SECRET_KEY"] = "My secret key"



@app.route('/')
#TODO: work out how much of the below we can move to a model
#TODO: overall vision for this page is a screenshot of the media library and prompt a sign in.
#navigation on this page is login/sign up/add new, navigation to sort by media type
 
def index():
 
    # NEW: Grab their user_id and username from the session cookie
    user_id = session.get("user_id")
    username = session.get("username")
 
    # NEW: If user_id exists, it means they're logged in
    if user_id:
        connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM items WHERE userid = (%s)", ([user_id])) # NEW: Only pull the logged-in-user's DB entries
 
        media_items = []
        for item in cursor.fetchall():
            media_items.append({"id": item[0], "userid": item[1], "title": item[2], "type":item[3], "genre":item[4], "summary":item[5], "image":item[6]})
        connection.close()
        return render_template("home.html", media_items=media_items, username=username) # NEW: Pass the username to the template too
 
    else:
        return render_template("welcome.html") # NEW: User isn't logged in, so show a welcome template.
 
if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))


@app.route('/type/<type>')

def list_type(type):

    user_id = session.get("user_id", "")
    username = session.get("username")

    if user_id:
        if type == None:
            return redirect(url_for('index'))
        else:
            connection = psycopg2.connect(os.getenv("DATABASE_URL"))        
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM items WHERE user_id = (%s) AND type = '{type}';", ([user_id])) 
            media_items = []
            for item in cursor.fetchall():
                media_items.append({"id": item[0], "user_id": item[1], "title": item[2], "type":item[3], "genre":item[4], "summary":item[5], "image":item[6]})
            connection.close()
            return render_template("home.html", media_items=media_items, username=username)

    else:
        return render_template("welcome.html") # NEW: User isn't logged in, so show a welcome template.

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))


@app.route('/add')
def add_form():
    username = session.get("username") # NEW: Get their username from the session
    
    if username: # NEW: If a username exists, it means they're logged in
        return render_template("add.html", username=username) # NEW: Pass the username to the template
    else: 
        return redirect(url_for('login_error', notification="error")) # NEW: User isn't logged in, so send them to the login page along with an error
    
# title, type, genre, summary, image
@app.route("/api/add", methods=["POST"])
def add_media():
    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = connection.cursor()
    user_id = session.get("user_id", "") # NEW: Grab the user_id from the session and add it to any media item they submit to the DB
    media_title = request.form.get("title")
    media_type = request.form.get("type")
    media_genre = request.form.get("genre")
    media_summary = request.form.get("summary")
    media_image = request.form.get("image")

    # Insert the new data into the DB, NEW: Add their user_id to any items they submit
    cursor.execute("INSERT INTO items(user_id, title, type, genre, summary, image) VALUES(%s, %s, %s, %s, %s, %s);", [user_id, media_title, media_type, media_genre, media_summary, media_image])
    connection.commit()
    connection.close()

    return redirect("/") # Media has been added, redirect to homepage (TODO: with a success alert)


@app.route('/edit/<media_id>')
@app.route('/edit')
def edit_form(media_id):
 
    if not media_id:
        return redirect(url_for('index'))
 
    username = session.get("username") # NEW: Get their username from the session
    user_id = session.get("user_id")
 
    if username: # NEW: If a username exists, it means they're logged in
        connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM items WHERE id = (%s)", ([media_id]))
        media_items = cursor.fetchone()
        connection.close()
 
        media_title = media_items[2]
        media_type = media_items[3]
        media_genre = media_items[4]
        media_summary = media_items[5]
        media_image = media_items[6]
 
        return render_template("edit.html", username=username, user_id=user_id, media_title=media_title, media_type=media_type, media_genre=media_genre, media_summary=media_summary, media_image=media_image, media_id=media_id)
    else: 
        return redirect(url_for('login_error', notification="error")) # NEW: User isn't logged in, so send them to the login page along with an error
 
@app.route("/api/edit", methods=["POST"])
def edit_media():
    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = connection.cursor()
    user_id = session.get("user_id", "") # NEW: Grab the user_id from the session and add it to any media item they submit to the DB
    media_title = request.form.get("title")
    media_type = request.form.get("type")
    media_genre = request.form.get("genre")
    media_summary = request.form.get("summary")
    media_image = request.form.get("image")
    media_id = request.form.get("media_id")
 
    cursor.execute("UPDATE items SET (title, type, genre, summary, image) = (%s, %s, %s, %s, %s) WHERE id = %s;", [media_title, media_type, media_genre, media_summary, media_image, media_id])
    connection.commit()
    connection.close()
 
    redirect_url = "/edit/" + media_id
    return redirect(redirect_url) # Media has been added, redirect to homepage (TODO: with a success alert)
 
 
@app.route('/del/<media_id>')
@app.route('/del')
def del_form(media_id):
 
    if not media_id:
        return redirect(url_for('index'))
 
    username = session.get("username") # NEW: Get their username from the session
    user_id = session.get("user_id")
 
    if username: # NEW: If a username exists, it means they're logged in
        
        connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM items WHERE id = (%s)", ([media_id]))
        media_items = cursor.fetchone()
        connection.close()
 
        media_title = media_items[2]
        media_type = media_items[3]
        media_genre = media_items[4]
        media_summary = media_items[5]
        media_image = media_items[6]
 
        return render_template("del.html", media_title=media_title, media_image=media_image, media_id=media_id)
    else: 
        return redirect(url_for('login_error', notification="error"))
 
@app.route("/api/del", methods=["POST"])
def del_media():
    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = connection.cursor()
 
    user_id = session.get("user_id", "") # NEW: Grab the user_id from the session and add it to any media item they submit to the DB
    media_title = request.form.get("title") # TODO: Use this later for a "<TITLE> was deleted!" alert.
    media_id = request.form.get("media_id")
 
    cursor.execute("DELETE FROM items WHERE id = %s;", [media_id])
 
    connection.commit()
    connection.close()
 
    return redirect("/") # Media has been deleted, redirect to homepage (TODO: with a success alert)
 

@app.route("/login") # NEW: Normal login page, now combined with signup page
def login_form():
        return render_template("login.html")

@app.route("/login/<notification>") # NEW: A duplicate of the login route that can be pased errors/notifications
def login_error(notification): # NEW: Pass the notification type into the function
    return render_template("login.html", notification=notification) # NEW: Pass the notification type into the template


@app.route("/api/login", methods=["POST"])
def login_action():
    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = connection.cursor()
    username = request.form.get("username")
    cursor.execute("SELECT * FROM users WHERE username=%s;", [username])
    result = cursor.fetchone()
 
    pw_hash = result[2] # Get the saved PW from the DB
    password = request.form.get("password").encode('utf-8') # Get their PW attempt from the form
 
    connection.close()
 
    if bcrypt.check_password_hash(pw_hash, password):
        session["user_id"] = result[0]
        session["username"] = result[1]
 
        return redirect(url_for('login_error', notification="loggedin")) # NEW: Redirect to login page with success muessage
 
    else:
        return redirect(url_for('login_error', notification="badlogin")) # NEW: Redirect to login page with fail message (this one shouldn't ever happen)

@app.route("/api/signup", methods=["POST"])
def signup_action():
    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = connection.cursor()
    sign_name = request.form.get("username")
    sign_pw = request.form.get("password")
    hash_pw = bcrypt.generate_password_hash(sign_pw).decode('utf-8')
    cursor.execute("INSERT INTO users(username, password) VALUES(%s, %s);", [sign_name, hash_pw])
    connection.commit()
    connection.close()

    return redirect("/login") # NEW: Redirect to the normal login page after they sign up (TODO: Make them auto-login after signup and redirect to homepage?)


@app.route("/logout")
def logout():
    session.clear() # NEW: Clear entire session of all fields
    return redirect("/") # TODO: "Logged Out" alert on homepage