# Parking Manager
#### Video Demo:  https://www.youtube.com/watch?v=evlm_6FK-AQ
#### Description:
A web-based application which allows users to book and manage parking slots themselves automatically. v1.0
Developed in Python with Flask Framework.

### Login.html
In order first to use the web-app, you must either login or sign up. 
If you don't have an account, you must sign up with a Username (it is possible to use alphanumeric caracters - lower or upper case are accepted), a password strong enough with 8 caracters minimum and a valid email adress.
The email adress will be used for authentication purposes.
If you already have an account, you can login with your email adress and your password.
All the information are stored in the users table in main.db, with a hash system to prevent any leak of the passwords. 

### Index.html
In the Index you will find 2 different lists:
- Parking
- Car
In order to be able to book a new parking slot, the users must first register a car. You can register as many car as you need.
You the have the possibility to perform a new booking : redirects you to booking.html
Or you have the ability to Add a new car : redirects you to car.html

### Rerservation.html
You can book only one day at a time and only for a one specific car.
The system is also designed to block any hijacking such as : 
- If the user tries to book a parking with a date out before the date in 
- If the user tries to book a parking with a date for which he already has a parking number 
- If the user tries to book a parking for more than one day
- Finally if the user tries to book a parking if he doesn't have cars previously registered 

### car.html
The page allows the user to add a new car based on 2 different criterias : 
- Car type (choice between 3 types): SUV, Sedan, City
- Plate number 
The car type will be used to automatically atribute adapted parking slots depending on the size of the vehicle. SUV shall be considered as bigger vehicle than a city car. 
This improvement of the system will be planned in v2.0

### Main.db
In the DB you will find 4 different table:
- users : Store all users data
- cars :Store all cars data
- reservations :Store every reservations made
- parking : Location where you can implement the number of parking slots needed. Parking slots are limited by the system to 20. It can be augmented by modifying the parking table in the database. In this table are only 2 columns, ID (autoincremented not null integer) and Parking number (not null integer), currently from 1 to 20.

### Miscealaneous
For praticity reasons, most of the protection have been set on client side. Meaning that this app shall be used only on local network. 
This version doesn't include
- Admin access 
- Mail notification (currently I didn't find any sustainable solution with Flask to use easily mail notification - based on the CS50 course, the lib used for mailing is Flask-Mail, unfortunately Google is blocking its "Less Secure App" system, in order to reinforce users protection. https://support.google.com/accounts/answer/6010255?hl=en) 
- Management of the history 
- Password reset : This must be implemented jointly with mail notification.

### Used framework and code
The currenct project has been set up with : 
- Python
- CSS 
- HTML 
- Javascript
Framework : 
- Flask
- Bootstrap

### How to launch application

Clone the code: git clone https://github.com/Guyyom/parking_manager
Once installed initiate a virutal environment with Flask, more here: https://flask.palletsprojects.com/en/2.0.x/installation/
In your browser go to localhost:5000
You are ready to go!
