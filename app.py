from datetime import datetime, date
from flask import Flask, render_template, request, flash, redirect, session
from flask_session import Session
from helpers import login_required
import sqlite3 
from werkzeug.security import check_password_hash, generate_password_hash
#Werkzeug security is used to hash password into db : generate_password_hash
#Additionnaly check_password_hash allows to read and check if the password is correct

#Inite Flask server app
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
#Configures Flask to store sessions on the local filesystem (i.e., disk) 
#as opposed to storing them inside of (digitally signed) cookies, which is Flask’s default
app.config["SESSION_TYPE"] = "filesystem"
#Allow to manage Session on server side 
Session(app)

list = ['SUV', 'Sedan', 'City']
today = date.today()

@app.route("/")  
@login_required
def main():
    #Connect Sqlite3 database
    curs = sqlite3.connect("static/main.db")
    curs.row_factory = sqlite3.Row
    db = curs.cursor()
    #Retrive ID of the session
    id = session["user_id"]

    #Get username to add name in the main page
    username = db.execute("SELECT username FROM users WHERE id = ?", (id,))
    name = username.fetchone()
    name = tuple(name)

    #Verify if previous reservation exists
    reservation = db.execute("SELECT * FROM reservations WHERE id_user = ?", (id,))
    reservation = reservation.fetchall()
    #Verify if car already exists
    car = db.execute("SELECT * FROM cars WHERE id_user = ?", (id,))
    car = car.fetchall()

    if reservation and car:
        reservation = tuple(reservation)
        car = tuple(car)
        curs.close()
        return render_template("main.html", username=name[0], reservation=reservation, car=car)

    elif car: 
        car = tuple(car)
        curs.close()
        return render_template("main.html", username=name[0], car=car)

    elif reservation:
        reservation = tuple(reservation)
        curs.close()
        return render_template("main.html", username=name[0], reservation=reservation)

    else: 
        curs.close()
        return render_template("main.html", username=name[0])


@app.route("/car", methods=["GET", "POST"])  
@login_required
def car():
    if request.method == "POST":
        #Connect Sqlite3 database
        curs = sqlite3.connect("static/main.db")
        curs.row_factory = sqlite3.Row
        db = curs.cursor()
        #Retrive ID of the session
        id_user = session["user_id"]
        
        #Retrieve information from car.html form 
        car_type = request.form.get("car_type")
        plate_number = request.form.get("plate_number")
        #Check if plate_number already exist
        existing_car = db.execute("SELECT plate_number FROM cars WHERE plate_number = ?", (plate_number,))
        existing_car = existing_car.fetchone()

        #Block the form if the user tries to force another car type
        if car_type not in list: 
            flash("Car type is not correct!") 
            curs.close()       
            return render_template("car.html", list=list)

        #Block the form is the plate number already exists
        if existing_car: 
            flash("This plate number already exists!")
            curs.close
            return render_template("car.html", list=list)

        #If everything is ok, commit info in the DB and return to main page
        db.execute("INSERT INTO cars(car_type, plate_number, id_user) VALUES(? , ?, ?)", (car_type, plate_number, id_user))
        curs.commit()
        curs.close()
        return redirect("/")

    return render_template("car.html", list=list)


@app.route("/delete_car", methods=["POST"])  
@login_required
def delete_car():
    if request.method == "POST": 
        id = request.form.get("id_car")

        #Connect Sqlite3 database
        curs = sqlite3.connect("static/main.db")
        curs.row_factory = sqlite3.Row
        db = curs.cursor()

        db.execute("DELETE FROM cars WHERE id_car = ?", (id,))
        curs.commit()
        curs.close()
        return redirect("/")


@app.route("/reservation", methods=["GET", "POST"])  
@login_required
def reservation():
    #Connect Sqlite3 database
    curs = sqlite3.connect("static/main.db")
    curs.row_factory = sqlite3.Row
    db = curs.cursor()
    #Retrive ID of the session
    id_user = session["user_id"]

    #Verify if a car exists 
    car = db.execute("SELECT plate_number FROM cars WHERE id_user = ?", (id_user,))
    car = car.fetchall()
    car = tuple(car)

    #If car doesn't exist, redirect to car registration
    if not car:
        curs.close()
        flash("Please add your car before booking!")
        return redirect("car")

    #Action when form is send 
    if request.method == "POST":

        #Get & manipulate date from the form (transform date string into date format)
        date_in = request.form.get("date_in")
        date_out = request.form.get("date_out")
        date_in = datetime.strptime(date_in,"%Y-%m-%d")
        date_out = datetime.strptime(date_out,"%Y-%m-%d")
        date_in = datetime.date(date_in)
        date_out = datetime.date(date_out)
        diff = date_out - date_in
        
        #Get data from the form 
        plate_number = request.form.get("plate_number")

        #Get data if user already has a parking for this date
        my_booking = db.execute("SELECT * FROM reservations WHERE id_user = ? AND date_in = ?", (id_user, date_in))
        my_booking = my_booking.fetchone()

        #If my booking exists, return error msg
        if my_booking: 
            flash("You already have a parking for this date!")
            curs.close
            return redirect("/")

        #If date in is before today, return error msg
        elif date_in < today:
            flash("You can't select a date before today, please retry!")
            curs.close
            return render_template("reservation.html", car=car)

        #If date out is before date in, return error msg
        elif date_in > date_out: 
            flash("Date out is before date in")
            curs.close()
            return render_template("reservation.html", car=car)
        
        #If difference between date in and date out is greater than 0 day, return error msg
        elif diff.days > 0: 
            flash("You can only book 1 day at a time, please retry!")
            curs.close()
            return render_template("reservation.html", car=car)

        #Else book a parking
        else:
            #Get all parking_number booked for the date_in
            booking = db.execute("SELECT id_parking_number FROM reservations WHERE date_in = ?", (date_in,))
            booking = booking.fetchall()
            booking = tuple(booking)
            booking_buffer_list=[]
            for x in booking:
                for y in x:
                    booking_buffer_list.append(y)

            #Get all parking_number available
            parking = db.execute("SELECT parking_number FROM parking")
            parking = parking.fetchall()
            parking = tuple(parking)
            parking_buffer_list=[]
            for x in parking:
                for y in x:
                    parking_buffer_list.append(y)
            
            #Compare the two lists to detect discrepencies 
            set_difference = set(parking_buffer_list) - set(booking_buffer_list)
            list_difference = tuple(set_difference)

            #If discrepencies detected choose the first value in the list and attribute the parking slot
            if len(list_difference) > 0:
                id_parking_number = list_difference[0]
                db.execute("INSERT INTO reservations(id_parking_number, date_in, date_out, plate_number, id_user) VALUES(?, ?, ?, ?, ?)", (id_parking_number, date_in, date_out, plate_number, id_user,))
                curs.commit()
                curs.close()
                return redirect("/")

            #Else return error messages
            else:
                flash("Sorry, all parking are booked for your date!")
                curs.close
                return redirect("/")

    curs.close()
    return render_template("reservation.html", car=car)

    
@app.route("/delete_reservation", methods=["POST"])  
@login_required
def delete_resevation():
    if request.method == "POST": 
        id = request.form.get("id_reservation")

        #Connect Sqlite3 database
        curs = sqlite3.connect("static/main.db")
        curs.row_factory = sqlite3.Row
        db = curs.cursor()

        db.execute("DELETE FROM reservations WHERE id_reservation = ?", (id,))
        curs.commit()
        curs.close()
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST": 

        email = request.form.get("email")
        password = request.form.get("password")

        #Connect Sqlite3 database
        curs = sqlite3.connect("static/main.db")
        curs.row_factory = sqlite3.Row
        db = curs.cursor()

        # Query database for email
        row = db.execute("SELECT * FROM users WHERE email = ?", (email,))
        row_login = row.fetchone()
        if row_login:
            row_login = tuple(row_login)
            # Ensure password is correct
            if check_password_hash(row_login[2], password) == False:
                #Close the db 
                curs.close()
                flash("Password is not correct!")    
                return redirect("/login")
            else: 
                # Remember which user has logged in
                session["user_id"] = row_login[0]
                #Close the db 
                curs.close()
                return redirect("/")
        else: 
            #Close the db 
            curs.close()
            flash("Account doesn't exist!")        
            return redirect("/login")
    
    return render_template("login.html")


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == 'POST':
        # Forget any user_id
        session.clear()

        #Get all data from the form at signup.html
        name = request.form.get("uname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
    
        #Connect Sqlite3 database
        curs = sqlite3.connect("static/main.db")
        curs.row_factory = sqlite3.Row
        #Create a cursor to execute Queries
        db = curs.cursor()

        #Check if username already exists
        row = db.execute("SELECT username FROM users WHERE username = ?", (name,))
        row_username = row.fetchone()
        if row_username:
            flash("Username already exists!")
            return redirect("/sign_up")

        #Check if email already exists
        row =  db.execute("SELECT email FROM users WHERE email = ?", (email,))
        row_email = row.fetchone()
        if row_email:
            flash("Email already exists!")
            return redirect("/sign_up")     

        #Check if password matchs with confirmation
        if password != confirmation:
            flash("Passwords don't match!")
            return redirect("/sign_up")

        #Check if password match the min. required length
        if len(password) < 8:
            flash("Password is not long enough (min. 8 caracters)")
            return redirect("/sign_up")

        if password == confirmation:
            #Hash password
            password = generate_password_hash(password)
            #Save into the db
            db.execute("INSERT INTO users(username, password, email) VALUES(?, ?, ?)", (name, password, email))
            #Commit / Save the change on the object
            curs.commit()

            #Login with the new user
            row = db.execute("SELECT id FROM users WHERE email = ?", (email,))
            row_login = row.fetchone()
            session["user_id"] = row_login[0]
            
            #Close the db 
            curs.close()
            return redirect("/car")

        #Close the db 
        curs.close()
        
    return render_template("sign_up.html")


@app.route("/logout")
@login_required
def logout():
    # Forget any user_id
    session.clear()
    return redirect("/login")

