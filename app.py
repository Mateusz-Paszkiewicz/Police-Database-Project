import mysql.connector
import hashlib

from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from helpers import login_required, authorisation_2_required, authorisation_3_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

cnx = mysql.connector.connect(user='funkcjonariusz', password='password123',
                              host='127.0.0.1',
                              database='policedb')
db = cnx.cursor()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/osoby", methods=["GET", "POST"])
@login_required
@authorisation_2_required
def osoby():
    if request.method == "POST":
        osoba = {
            "imie": request.form.get("imie"),
            "nazwisko": request.form.get("nazwisko"),
            "przezwisko": request.form.get("przezwisko"),
            "wiek": request.form.get("wiek"),
            "wyglad": request.form.get("wyglad"),
            "wzrost": request.form.get("wzrost"),
            "znaki": request.form.get("znaki"),
            "inne": request.form.get("inne")
        }

        arguments = []
        values = {}
        for key, dana in osoba.items():
            if dana:
                arguments.append(key + "=%(" + key + ")s")
                values[key] = dana
        
        query = "SELECT * FROM osoba"
        if arguments:
            query += " WHERE " + " AND ".join(arguments)
        
        db.execute(query, values)
        osoby = db.fetchall()

        return render_template("osoby.html", osoby=osoby)
    
    else:
        db.execute("SELECT * FROM osoba")
        osoby = db.fetchall()

        return render_template("osoby.html", osoby=osoby)


@app.route("/osoba_info")
@login_required
@authorisation_2_required
def osoba_info():
    id = request.args.get("id")
    
    query = "SELECT * FROM osoba WHERE id=%(id)s"
    
    db.execute(query, {'id': id})
    osoba = db.fetchall()[0]

    return render_template("osoba_info.html", osoba=osoba)


@app.route("/osoby_add", methods=["GET", "POST"])
@login_required
@authorisation_3_required
def osoby_add():
    if request.method == "POST":
        osoba = {}
        osoba["imie"] = request.form.get("imie")
        osoba["nazwisko"] = request.form.get("nazwisko")
        osoba["przezwisko"] = request.form.get("przezwisko")
        osoba["wiek"] = request.form.get("wiek")
        osoba["wyglad"] = request.form.get("wyglad")
        osoba["wzrost"] = request.form.get("wzrost")
        osoba["znaki"] = request.form.get("znaki")
        osoba["inne"] = request.form.get("inne")

        columns = "("
        values = " VALUES("
        for key, dana in osoba.items():
            if dana:
                if key == "wiek" or key == "wzrost":
                    columns = columns + key + ", "
                    values = values + dana + ", "
                else:
                    columns = columns + key + ", "
                    values = values + "'" + dana + "', "
        columns = columns.rstrip(", ") + ")"
        values = values.rstrip(", ") + ");"

        query = "INSERT INTO osoba" + columns + values
        db.execute(query)
        cnx.commit()

        return render_template("osoby_add.html", success=1)

    else:
        return render_template("osoby_add.html")


@app.route("/wydarzenia", methods=["GET", "POST"])
@login_required
@authorisation_2_required
def wydarzenia():
    if request.method == "POST":
        data = request.form.get("data")
        rodzaj = request.form.get("rodzaj")
        miejsce = {}
        miejsce["region"] = request.form.get("region")
        miejsce["miasto"] = request.form.get("miasto")
        miejsce["ulica"] = request.form.get("ulica")
        miejsce["numer"] = request.form.get("numer")
        miejsce["mieszkanie"] = request.form.get("mieszkanie")

        arguments = ""
        for key, dana in miejsce.items():
            if dana:
                if key == "numer" or key == "mieszkanie":
                    arguments = arguments + key + "=" + dana + " AND "
                else:
                    arguments = arguments + key + "='" + dana + "' AND "
        arguments = arguments.rstrip(" AND ")

        if len(arguments) >= 1:
            query = "SELECT * FROM miejsce WHERE " + arguments
            db.execute(query)
            miejsce = db.fetchall()
            if len(miejsce) >= 1:
                miejsce_id = miejsce[0][0]
                region = miejsce[0][1]
            else:
                miejsce_id = None
                region = None
        else:
            miejsce_id = None
            region = None

        arguments = ""
        if data:
            arguments = arguments + "data_wyd='" + data + "' AND "
        if rodzaj:
            arguments = arguments + "rodzaj='" + rodzaj + "' AND "
        if miejsce_id:
            arguments = arguments + "miejsce_id=" + str(miejsce_id) + " AND "
        arguments = arguments.rstrip(" AND ")

        zdarzenia = []
        query = "SELECT * FROM baza_wydarzen"
        if len(arguments) >= 1:
            query += " WHERE " + arguments
        db.execute(query)
        wydarzenia = db.fetchall()
        for wydarzenie in wydarzenia:
            db.execute("SELECT region FROM miejsce WHERE id = " + str(wydarzenie[3]))
            region = db.fetchall()[0][0]
            zdarzenia.append([wydarzenie[0], wydarzenie[1], wydarzenie[2], region])

        return render_template("wydarzenia.html", wydarzenia=zdarzenia)

    else:
        db.execute("SELECT * FROM baza_wydarzen")
        wydarzenia = db.fetchall()

        zdarzenia = []
        for wydarzenie in wydarzenia:
            db.execute("SELECT region FROM miejsce WHERE id = " + str(wydarzenie[3]))
            miejsce = db.fetchall()
            zdarzenia.append([wydarzenie[0], wydarzenie[1], wydarzenie[2], miejsce[0][0]])

        return render_template("wydarzenia.html", wydarzenia=zdarzenia)


@app.route("/wydarzenie_info")
@login_required
@authorisation_2_required
def wydarzenie_info():
    id = request.args.get("id")
    
    query = "SELECT * FROM baza_wydarzen WHERE id=%(id)s"
    
    db.execute(query, {'id': id})
    wydarzenie = db.fetchall()[0]
    
    query = "SELECT * FROM funkcjonariusz WHERE id=%(id)s"
    
    db.execute(query, {'id': wydarzenie[4]})
    funkcjonariusz_info = db.fetchall()[0]
    funkcjonariusz = funkcjonariusz_info[1] + " " + funkcjonariusz_info[2]
    
    info = []
    info.append(wydarzenie[1])
    info.append(wydarzenie[2])
    info.append(funkcjonariusz)
    
    query = "SELECT * FROM powiazania WHERE id_zdarzenia=%(id)s"
    
    db.execute(query, {'id': id})
    osoby_id = db.fetchall()
    
    podejrzani = []
    swiadkowie = []
    for powiazana_osoba in osoby_id:
        query = "SELECT * FROM osoba WHERE id=%(id)s"
    
        db.execute(query, {'id': powiazana_osoba[0]})
        osoba = db.fetchall()[0]
        print(osoba)
        imie = osoba[3] + " '" + osoba[6] + "' " + osoba[4]
        
        if powiazana_osoba[2] == "swiadek":
            swiadkowie.append([imie, osoba[0]])
        else:
            podejrzani.append([imie, osoba[0]])
        
    info.append(podejrzani)
    info.append(swiadkowie)

    return render_template("wydarzenie_info.html", info=info)


@app.route("/wydarzenia_add", methods=["GET", "POST"])
@login_required
@authorisation_3_required
def wydarzenia_add():
    if request.method == "POST":
        data = request.form.get("data")
        rodzaj = request.form.get("rodzaj")
        wydarzenie = {}
        wydarzenie["region"] = request.form.get("region")
        wydarzenie["miasto"] = request.form.get("miasto")
        wydarzenie["ulica"] = request.form.get("ulica")
        wydarzenie["numer"] = request.form.get("numer")
        wydarzenie["mieszkanie"] = request.form.get("mieszkanie")

        arguments = ""
        for key, dana in wydarzenie.items():
            if dana:
                if key == "numer" or key == "mieszkanie":
                    arguments = arguments + key + "=" + dana + " AND "
                else:
                    arguments = arguments + key + "='" + dana + "' AND "
        arguments = arguments.rstrip(" AND ")

        if len(arguments) >= 1:
            query = "SELECT * FROM miejsce WHERE " + arguments
            db.execute(query)
            miejsce = db.fetchall()
            if len(miejsce) >= 1:
                miejsce_id = miejsce[0][0]
            else:
                columns = "("
                values = " VALUES("
                for key, dana in wydarzenie.items():
                    if dana:
                        columns = columns + key + ", "
                        if key == "numer" or key == "mieszkanie":
                            values = values + dana + ", "
                        else:
                            values = values + "'" + dana + "', "
                columns = columns.rstrip(", ") + ") "
                values = values.rstrip(", ") + ")"

                query = "INSERT INTO miejsce" + columns + values
                db.execute(query)

                query = "SELECT * FROM miejsce WHERE " + arguments
                db.execute(query)
                miejsce = db.fetchall()
                miejsce_id = miejsce[0][0]
        else:
            miejsce_id = None

        columns = "("
        values = " VALUES("
        if data:
            columns = columns + "data_wyd, "
            values = values + "'" + data + "', "
        if rodzaj:
            columns = columns + "rodzaj, "
            values = values + "'" + rodzaj + "', "
        columns = columns + "miejsce_id, funkcjonariusz_id)"
        values = values + str(miejsce_id) + ", " + str(session["user_id"]) + ")"
        fin = "INSERT INTO baza_wydarzen" + columns + values
        db.execute(fin)
        cnx.commit()

        return render_template("wydarzenia_add.html", success=1)
    else:
        return render_template("wydarzenia_add.html")


@app.route("/radiowozy", methods=["GET", "POST"])
@login_required
@authorisation_3_required
def radiowoz():
    if request.method == "POST":
        radiowoz = {}
        radiowoz["model"] = request.form.get("model")
        radiowoz["dostepnosc"] = request.form.get("dostepnosc")
        radiowoz["moc"] = request.form.get("moc")
        radiowoz["kolor"] = request.form.get("kolor")

        arguments = ""
        for key, dana in radiowoz.items():
            if dana:
                if key == "dostepnosc" or key == "moc":
                    arguments += key + " = " + dana + " AND "
                else:
                    arguments += key + " = '" + dana + "' AND "
        arguments = arguments.rstrip(" AND ")

        query = "SELECT * FROM radiowoz"
        if arguments:
            query += " WHERE " + arguments

        db.execute(query)
        radiowozy = db.fetchall()

        return render_template("radiowozy.html", radiowozy=radiowozy)
    else:
        db.execute("SELECT * FROM radiowoz")
        radiowozy = db.fetchall()

        return render_template("radiowozy.html", radiowozy=radiowozy)


@app.route("/radiowozy_wynajmij", methods=["GET", "POST"])
@login_required
@authorisation_3_required
def radiowoz_wynajem():
    id = request.args.get("id")
    rent = request.args.get("rent")

    if rent:
        # query = "UPDATE radiowoz SET dostepnosc=%(rent)s WHERE id=%(id)s"
        # db.execute(query, {'rent': rent, 'id': id})
        # query = "UPDATE funkcjonariusz SET radiowoz_id=%(id)s WHERE id=%(cop_id)s"
        # db.execute(query, {'id': id, 'cop_id': session[user_id]})
        return render_template("radiowozy_wynajem.html", radiowoz=radiowoz, rent=rent)
    else:
        query = "SELECT * FROM radiowoz WHERE id=%(id)s"
    
        db.execute(query, {'id': id})
        radiowoz = db.fetchall()[0]

        return render_template("radiowozy_wynajem.html", radiowoz=radiowoz)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure password was submitted
        if not request.form.get("password") or not request.form.get("login"):
            return render_template("login.html", wrong=1)

        # Query database for username
        login_imie = request.form.get("login")[0]
        login_nazwisko = request.form.get("login")[1:]
        
        query = "SELECT * FROM funkcjonariusz WHERE nazwisko='" + login_nazwisko + "' AND imie LIKE '" + login_imie + "%'"
        db.execute(query)
        
        login_valid = db.fetchall()
        
        # Ensure password is correct
        md5_hash = hashlib.md5()
        md5_hash.update(request.form.get("password").encode())

        hashed_string = md5_hash.hexdigest()
        
        # 7 column is password
        if len(login_valid) == 0 or login_valid[0][7] != hashed_string:
            return render_template("login.html", wrong=2)

        # Remember which user has logged in, 0 column is id
        session["user_id"] = login_valid[0][0]
        session["authorisation"] = login_valid[0][4]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")