from flask import Flask, render_template, request, redirect, session
import os
import psycopg2, bcrypt

app = Flask(__name__)

# setting secret key used to 'sign' session values
app.config["SECRET_KEY"] = "My secret key"

@app.route('/')
#TODO: work out how much of the below we can move to a model
#TODO: overall vision for this page is a screenshot of the media library and prompt a sign in.
#navigation on this page is login/sign up/add new, navigation to sort by media type
def index():
    user_id = session.get("user_id") #pulls out these values from the session and puts them in local variables
    username = session.get("username") #i can use this later to say "hey username!"

    if user_id:
        cursor.execute("SELECT * FROM items WHERE userid = (%s)", ([user_id])) #we can now pull the userID out of the session and stick it in SQL. we can then pull out only hte logged in users items
        connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM items")

        media_items = []
        for item in cursor.fetchall():
            media_items.append({"id": item[0], "user id": item[1], "title": item[2], "type":item[3], "genre":item[4], "summary":item[5], "image":item[6]})
        connection.close()
        return render_template("home.html", media_items=media_items, username=username)

    else:
        return f"Sign up or log in to view your media library!"

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))


@app.route('/add')
#add new item
def add_form():
  return f"""
  <h1>ADD MEDIA</h1>
  <form action="/api/add" method="POST">
    <label for="title">title</label>
    <input id="title" type="text" name="title">
    
    <label for="type">Type</label>
    <select name="type" id="type">
        <option value="movie">Movie</option>
        <option value="game">Game</option>
        <option value="book">Book</option>
        <option value="music">Music</option>
    </select>

    <label for="genre">Genre</label>
    <input id="genre" type="text" name="genre">

    <label for="summary">Summary</label>
    <textarea id="summary" type="text" name="summary"></textarea>

    <label for="image">Image</label>
    <input id="image" type="text" name="image">

    <input type="submit">
  </form>
  """
@app.route("/api/add", methods=["POST"])
def add_media():
    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = connection.cursor()
    media_title = request.form.get("title")
    media_type = request.form.get("type")
    media_genre = request.form.get("genre")
    media_summary = request.form.get("summary")
    media_image = request.form.get("image")

    cursor.execute("INSERT INTO items(title, type, genre, summary, image) VALUES(%s, %s, %s, %s, %s);", [media_title, media_type, media_genre, media_summary, media_image])
    connection.commit()
    connection.close()
    return redirect("/")

@app.route("/login")
def login_form():
  return f"""
  <h1>LOGIN PAGE</h1>
  <form action="/api/login" method="POST">
    <label for="username">Username</label>
    <input id="username" type="text" name="username">

    <label for="password">Password</label>
    <input id="password" type="password" name="password">

    <input type="submit">
  </form>
  """
@app.route("/api/login", methods=["POST"])
def login_action():
    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = connection.cursor()
    username = request.form.get("username")
    password = request.form.get("password")
    cursor.execute(f"SELECT id FROM users WHERE username='{username}';")
    result = cursor.fetchall()
    print(result)
    connection.close()

    if len(result):
        session["user_id"] = result[0][0]
        session["username"] = result[0][1]
        return redirect("/") #this is successfully logged in
    
    else:
        return redirect("/login") #this is not successfully logged in


@app.route("/signup")
def signup_form():
  return f"""
  <h1>SIGNUP PAGE</h1>
  <form action="/api/signup" method="POST">

  <label for="username">Username</label>
    <input id="username" type="text" name="username">

    <label for="password">Password</label>
    <input id="password" type="password" name="password">

    <input type="submit">
  </form>
  """

@app.route("/api/signup", methods=["POST"])
def signup_action():
    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = connection.cursor()
    sign_name = request.form.get("username")
    sign_pw = request.form.get("password")
    hash_pw = bcrypt.hashpw(sign_pw.encode(), bcrypt.gensalt())
    print(hash_pw)
    cursor.execute("INSERT INTO users(username, password) VALUES(%s, %s);", [sign_name, hash_pw])
    connection.commit()
    connection.close()
    return redirect("/login")


@app.route("/logout")
def logout():
    session.clear() # we need to clear cookie completely because we are using username and userid now
    return redirect("/")