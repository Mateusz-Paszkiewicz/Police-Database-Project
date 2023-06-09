﻿import mysql.connector
import hashlib
import datetime
from datetime import datetime 

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
                              database='bazy_data')
db = cnx.cursor()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html')

@app.errorhandler(404)
def server_error(error):
    return render_template('404.html')


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
        query += " ORDER BY imie"
        
        db.execute(query, values)
        osoby = db.fetchall()
        
        db.execute("SELECT * FROM osoba ORDER BY imie")
        all = db.fetchall()

        return render_template("osoby.html", osoby=osoby, all=all)
    
    else:
        db.execute("SELECT * FROM osoba ORDER BY imie")
        osoby = db.fetchall()

        return render_template("osoby.html", osoby=osoby, all=osoby)


@app.route("/osoba_info")
@login_required
@authorisation_2_required
def osoba_info():
    id = request.args.get("id")
    
    query = "SELECT * FROM osoba WHERE id=%(id)s ORDER BY imie"
    
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
        values = []
        values_v = {}
        for key, dana in osoba.items():
            if dana:
                columns = columns + key + ", "
                values.append("%(" + key + ")s")
                values_v[key] = dana
        columns = columns.rstrip(", ") + ")"

        query = "INSERT INTO osoba" + columns + " VALUES(" + ", ".join(values) + ")"
        db.execute(query, values_v)
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

        arguments = []
        values = {}
        for key, dana in miejsce.items():
            if dana:
                arguments.append(key + "=%(" + key + ")s")
                values[key] = dana

        if len(arguments) >= 1:
            query = "SELECT * FROM miejsce WHERE " + " AND ".join(arguments)
            db.execute(query, values)
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

        arguments = []
        values = {}
        if data:
            arguments.append("data_wyd=%(data_wyd)s")
            values["data_wyd"] = data
        if rodzaj:
            arguments.append("rodzaj=%(rodzaj)s")
            values["rodzaj"] = rodzaj
        if miejsce_id:
            arguments.append("miejsce_id=%(miejsce_id)s")
            values["miejsce_id"] = miejsce_id

        zdarzenia = []
        query = "SELECT * FROM baza_wydarzen"
        if len(arguments) >= 1:
            query += " WHERE " + " AND ".join(arguments)
        query += " ORDER BY data_wyd"
        db.execute(query, values)
        wydarzenia = db.fetchall()

        for wydarzenie in wydarzenia:
            db.execute("SELECT region FROM miejsce WHERE id = " + str(wydarzenie[3]))
            region = db.fetchall()[0][0]
            zdarzenia.append([wydarzenie[0], wydarzenie[1], wydarzenie[2], region])
            
        db.execute("SELECT * FROM baza_wydarzen ORDER BY data_wyd")
        wydarzenia = db.fetchall()

        all = []
        for wydarzenie in wydarzenia:
            db.execute("SELECT * FROM miejsce WHERE id = " + str(wydarzenie[3]))
            miejsce = db.fetchall()
            all.append([wydarzenie[0], wydarzenie[1], wydarzenie[2], miejsce[0][1], miejsce[0][2], miejsce[0][3]])

        return render_template("wydarzenia.html", wydarzenia=zdarzenia, all=all)

    else:
        db.execute("SELECT * FROM baza_wydarzen ORDER BY data_wyd")
        wydarzenia = db.fetchall()

        zdarzenia = []
        for wydarzenie in wydarzenia:
            db.execute("SELECT * FROM miejsce WHERE id = " + str(wydarzenie[3]))
            miejsce = db.fetchall()
            zdarzenia.append([wydarzenie[0], wydarzenie[1], wydarzenie[2], miejsce[0][1], miejsce[0][2], miejsce[0][3]])

        return render_template("wydarzenia.html", wydarzenia=zdarzenia, all=zdarzenia)


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
        imie_parts = [part for part in [osoba[3], osoba[6], osoba[4]] if part is not None]
        imie = " ".join(imie_parts)
        
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

        arguments = []
        values = {}
        for key, dana in wydarzenie.items():
            if dana:
                arguments.append(key + "=%(" + key + ")s")
                values[key] = dana

        if len(arguments) >= 1:
            query = "SELECT * FROM miejsce WHERE " + " AND ".join(arguments)
            db.execute(query, values)
            miejsce = db.fetchall()
            if len(miejsce) >= 1:
                miejsce_id = miejsce[0][0]
            else:
                columns = "("
                values = []
                values_q = []
                values_v = {}
                for key, dana in wydarzenie.items():
                    if dana:
                        columns = columns + key + ", "
                        values.append("%(" + key + ")s")
                        values_q.append(key + "=%(" + key + ")s")
                        values_v[key] = dana
                columns = columns.rstrip(", ") + ") "

                query = "INSERT INTO miejsce" + columns + "VALUES(" + ", ".join(values) + ")"
                db.execute(query, values_v)

                query = "SELECT * FROM miejsce WHERE " + " AND ".join(values_q)
                db.execute(query, values_v)
                miejsce = db.fetchall()
                miejsce_id = miejsce[0][0]
        else:
            miejsce_id = None

        columns = "("
        values = []
        values_v = {}
        if data:
            columns = columns + "data_wyd, "
            values.append("%(data_wyd)s")
            values_v["data_wyd"] = data
        if rodzaj:
            columns = columns + "rodzaj, "
            values.append("%(rodzaj)s")
            values_v["rodzaj"] = rodzaj

        columns = columns + "miejsce_id, funkcjonariusz_id)"
        values_v["miejsce_id"] = str(miejsce_id)
        values_v["funkcjonariusz_id"] = str(session["user_id"])
        fin = "INSERT INTO baza_wydarzen" + columns + " VALUES(" + ", ".join(values) + ", %(miejsce_id)s, %(funkcjonariusz_id)s)"
        db.execute(fin, values_v)
        cnx.commit()

        return render_template("wydarzenia_add.html", success=1)
    else:
        db.execute("SELECT * FROM baza_wydarzen ORDER BY data_wyd")
        wydarzenia = db.fetchall()

        all = []
        for wydarzenie in wydarzenia:
            db.execute("SELECT * FROM miejsce WHERE id = " + str(wydarzenie[3]))
            miejsce = db.fetchall()
            all.append([wydarzenie[0], wydarzenie[1], wydarzenie[2], miejsce[0][1], miejsce[0][2], miejsce[0][3]])

        return render_template("wydarzenia_add.html", all=all)


@app.route("/radiowozy", methods=["GET", "POST"])
@login_required
def radiowoz():
    # updating elasped time for each radiowoz
    query = "SELECT id, rental_date, dostepnosc FROM radiowoz"
    db.execute(query)
    all_cars = db.fetchall()

    for car in all_cars:
        radiowoz_id = car[0]
        rental_date = car[1]
        current_dostepnosc = car[2]
        
        if current_dostepnosc != 0:
            rental_datetime = rental_date
            current_datetime = datetime.now()
            elapsed_time = current_datetime - rental_datetime
            dostepnosc = max(int( current_dostepnosc - (elapsed_time.total_seconds()/3600)+1), 0)

            if dostepnosc == 0:
                query = "UPDATE radiowoz SET rental_date = NULL WHERE id = %(radiowoz_id)s"
                db.execute(query, {'radiowoz_id': radiowoz_id})
                query = "UPDATE funkcjonariusz SET radiowoz_id = NULL WHERE radiowoz_id = %(radiowoz_id)s"
                db.execute(query, {'radiowoz_id': radiowoz_id})

            update_query = "UPDATE radiowoz SET dostepnosc = %(dostepnosc)s WHERE id = %(radiowoz_id)s"
            db.execute(update_query, {'dostepnosc': dostepnosc, 'radiowoz_id': radiowoz_id})
            cnx.commit()

    # actual radiowozy endpoint
    rented_id = -1

    query = "SELECT radiowoz_id FROM funkcjonariusz WHERE id = %(cop_id)s"
    db.execute(query, {'cop_id': session["user_id"]})
    result = db.fetchone()
    if result:
        rented_id = result[0]

    if request.method == "POST":
        radiowoz = {}
        radiowoz["model"] = request.form.get("model")
        radiowoz["dostepnosc"] = request.form.get("dostepnosc")
        radiowoz["moc"] = request.form.get("moc")
        radiowoz["kolor"] = request.form.get("kolor")

        arguments = ""
        arguments = []
        values = {}
        for key, dana in radiowoz.items():
            if dana:
                arguments.append(key + "=%(" + key + ")s")
                values[key] = dana
                if key == "dostepnosc":
                    values[key] = 0

        query = "SELECT * FROM radiowoz"
        if arguments:
            query += " WHERE " + " AND ".join(arguments)

        query += " ORDER BY dostepnosc"
        db.execute(query, values)
        radiowozy = db.fetchall()
        
        db.execute("SELECT * FROM radiowoz")
        all = db.fetchall()

        return render_template("radiowozy.html", radiowozy=radiowozy, rented_id=rented_id, all=all)
    else:
        db.execute("SELECT * FROM radiowoz ORDER BY dostepnosc")
        radiowozy = db.fetchall()

        return render_template("radiowozy.html", radiowozy=radiowozy, rented_id=rented_id, all=radiowozy)
    

@app.route("/radiowozy_wynajmij", methods=["GET", "POST"])
@login_required
@authorisation_3_required
def radiowoz_wynajem():
    id = request.args.get("id")

    query = "SELECT * FROM radiowoz WHERE id=%(id)s"
    db.execute(query, {'id': id})
    radiowoz = db.fetchall()[0]

    if request.method == "POST":
        rent = request.form.get("rent")
        if rent:
            query = "UPDATE radiowoz SET dostepnosc=%(rent)s WHERE id=%(id)s"
            db.execute(query, {'rent': rent, 'id': id})
            query = "UPDATE funkcjonariusz SET radiowoz_id=%(id)s WHERE id=%(cop_id)s"
            db.execute(query, {'id': id, 'cop_id': session["user_id"]})

            current_time = datetime.now()

            query = "UPDATE radiowoz SET rental_date=%(rental_date)s WHERE id=%(id)s"
            db.execute(query, {'rental_date': current_time, 'id': id})
            cnx.commit()
            return render_template("radiowozy_wynajem.html", radiowoz=radiowoz, rent=rent)

    return render_template("radiowozy_wynajem.html", radiowoz=radiowoz)

@app.route("/radiowozy_release", methods=["GET"])
@login_required
def release_radiowoz():
    rented_id = None

    query = "SELECT radiowoz_id FROM funkcjonariusz WHERE id = %(cop_id)s"
    db.execute(query, {'cop_id': session["user_id"]})
    result = db.fetchone()
    if result:
        rented_id = result[0]

    query = "UPDATE funkcjonariusz SET radiowoz_id = NULL WHERE id = %(cop_id)s"
    db.execute(query, {'cop_id': session["user_id"]})

    query = "UPDATE radiowoz SET dostepnosc = 0, rental_date = NULL WHERE id = %(rented_id)s"
    db.execute(query, {'rented_id': rented_id})
    cnx.commit()

    rented_id = None

    db.execute("SELECT * FROM radiowoz")
    radiowozy = db.fetchall()

    return render_template("radiowozy.html", radiowozy=radiowozy, rented_id=rented_id)


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