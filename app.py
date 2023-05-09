from flask import Flask, render_template, request, redirect, session
import os
import psycopg2, bcrypt

# test JL update2

app = Flask(__name__)

# setting secret key used to 'sign' session values
app.config["SECRET_KEY"] = "My secret key"

@app.route('/')
#TODO: work out how much of the below we can move to a model
#TODO: overall vision for this page is a screenshot of the media library and prompt a sign in.
#navigation on this page is login/sign up/add new, navigation to sort by media type
def index():
    # connection = psycopg2.connect(host=os.getenv("PGHOST"), user=os.getenv("PGUSER"), password=os.getenv("PGPASSWORD"), port=os.getenv("PGPORT"), dbname=os.getenv("PGDATABASE"))
    # connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    # cursor = connection.cursor()
    # cursor.execute("SELECT * FROM mytable;")
    # results = cursor.fetchall()
    # connection.close()
    # return f"THIS IS A TEST {results[0]}"
    user_id = session.get("user_id", "")
    if user_id:
        return f"hello {session.get('user_id', '')}, you have access!"
    else:
        return f"You need to login"

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))


@app.route('/add')
#add new item
def add_form():
  return f"""
  <h1>ADD MEDIA</h1>
  <form actions="/api/add" method="POST">
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
    <textarea id="summary" type="text" name="summary">

    <label for="image">Image</label>
    <input id="image" type="text" name="image">

    <input type="submit">
  </form>
  """
# title, type, genre, summary, image
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
    # TODO: commit the SQL commands
    connection.commit()

    # TODO: close the connection
    connection.close()

    # return render_template("fanx.html", food_name=food_name, food_price=food_price, food_img=food_img, food_vegan=food_vegan)


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
        return redirect("/") #this is successfully logged in
    
    else:
        return redirect("/login") #this is not successfully logged in. maybe create a new user if not valid?


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
    # TODO: commit the SQL commands
    connection.commit()

    # TODO: close the connection
    connection.close()

    return redirect("/login")


@app.route("/logout")
def logout():
    session["user_id"] = None
    # or session.clear() to clear cookie completely
    return redirect("/")