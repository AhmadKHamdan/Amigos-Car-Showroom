import mysql.connector
from werkzeug.security import generate_password_hash
from faker import Faker

fake = Faker()


myDB = mysql.connector.connect(host="localhost", user="root", password="Ahmad2003")
myCursor = myDB.cursor()

def main():
    myCursor.execute("DROP DATABASE IF EXISTS carShowroom")
    myCursor.execute("CREATE DATABASE carShowroom")
    myCursor.execute("USE carShowroom")
    creation()
    insertion()
    myDB.commit()

def creation():
    myCursor.execute(
        """CREATE TABLE EMPLOYEE (
            EMP_ID INT AUTO_INCREMENT PRIMARY KEY, 
            NAME VARCHAR(100), 
            ADDRESS VARCHAR(255), 
            CARRIER VARCHAR(50), 
            DATE_OF_BIRTH DATE, 
            START_DATE DATE, 
            BASE_SALARY DECIMAL(10, 2), 
            STATUS ENUM('CURRENT', 'FORMER') DEFAULT 'CURRENT'
        );"""
    )

    myCursor.execute(
        """CREATE TABLE SALES_EMP (
            EMP_ID INT PRIMARY KEY, 
            COMMISSION_RATE DECIMAL(5, 2), 
            FOREIGN KEY (EMP_ID) REFERENCES EMPLOYEE(EMP_ID) ON DELETE CASCADE
        );"""
    )

    myCursor.execute(
        """CREATE TABLE OTHER_SERVICE_EMP (
            EMP_ID INT PRIMARY KEY, 
            SERVICE_TYPE VARCHAR(255), 
            FOREIGN KEY (EMP_ID) REFERENCES EMPLOYEE(EMP_ID) ON DELETE CASCADE
        );"""
    )

    myCursor.execute(
        """CREATE TABLE ADMIN (
            EMP_ID INT PRIMARY KEY, 
            EMAIL VARCHAR(100) UNIQUE, 
            HASHED_PASSWORD VARCHAR(255), 
            FOREIGN KEY (EMP_ID) REFERENCES EMPLOYEE(EMP_ID) ON DELETE CASCADE
        );"""
    )

    myCursor.execute(
        """CREATE TABLE CUSTOMERS (
            CUS_ID INT AUTO_INCREMENT PRIMARY KEY, 
            CUS_NAME VARCHAR(100), 
            ADDRESS VARCHAR(255), 
            CARRIER VARCHAR(50), 
            EMAIL VARCHAR(100) UNIQUE, 
            HASHED_PASSWORD VARCHAR(255)
        );"""
    )

    myCursor.execute(
        """CREATE TABLE OPTIONS (
            OP_ID INT AUTO_INCREMENT PRIMARY KEY,
            SUNROOF BOOLEAN,
            HEATED_SEATS BOOLEAN,
            GPS_NAVIGATION BOOLEAN,
            BACKUP_CAMERA BOOLEAN
        );"""
    )

    myCursor.execute(
        """CREATE TABLE VEHICLE_MODELS (
            MODEL_ID INT AUTO_INCREMENT PRIMARY KEY,
            CAR_BRAND VARCHAR(50),
            CAR_MODEL VARCHAR(50),
            NUM_OF_DOORS TINYINT,
            CAR_COLOR VARCHAR(20),
            PETROL_TYPE VARCHAR(20),
            NUM_OF_PASS TINYINT,
            TRANSMISSION_TYPE VARCHAR(20),
            MANUFACTURE_YEAR YEAR,
            PRICE DECIMAL(10, 2),
            OP_ID INT,
            FOREIGN KEY (OP_ID) REFERENCES OPTIONS(OP_ID)
        );"""
    )

    myCursor.execute(
        """CREATE TABLE VEHICLES (
            CAR_ID INT AUTO_INCREMENT PRIMARY KEY,
            MODEL_ID INT,
            STATUS ENUM('AVAILABLE', 'SOLD', 'NOT-AVAILABLE') DEFAULT 'AVAILABLE',
            FOREIGN KEY (MODEL_ID) REFERENCES VEHICLE_MODELS(MODEL_ID)
        );"""
    )

    myCursor.execute(
        """CREATE TABLE SOLD_CARS (
            CAR_ID INT PRIMARY KEY, 
            DATE_OF_PURCHASE DATE, 
            PAYMENT_METHOD VARCHAR(50), 
            CUS_ID INT, 
            EMP_ID INT, 
            FOREIGN KEY (CAR_ID) REFERENCES VEHICLES(CAR_ID) ON DELETE CASCADE, 
            FOREIGN KEY (CUS_ID) REFERENCES CUSTOMERS(CUS_ID), 
            FOREIGN KEY (EMP_ID) REFERENCES EMPLOYEE(EMP_ID)
        );"""
    )

    myCursor.execute(
        """CREATE TABLE NON_SOLD_CARS (
            CAR_ID INT PRIMARY KEY, 
            DATE_OF_ARRIVAL DATE, 
            FOREIGN KEY (CAR_ID) REFERENCES VEHICLES(CAR_ID) ON DELETE CASCADE
        );"""
    )

def insertion():
    insertAdmins()
    insertEmployees()
    insertCustomers()
    insertOptions()
    insertVehicleModels()
    insertVehicles()
    insertPurchases()

def insertAdmins():
    admins = [
        ("Ahmad Hamdan", "admin1@hotmail.com", "ahmad", 'Ramallah, Al-Terih', '0595940940', '2003-04-12', '2024-03-30', 135000),
        ("Diaa Badaha", "admin2@hotmail.com", "diaa", 'Ramallah, Deir Ammar', '0594431377', '2003-10-31', '2024-03-30', 135000),
        ("Omar Hussain", "admin3@hotmail.com", "omar", 'Tulkarem, Nazlet Issa', '0597246747', '2003-05-10', '2024-03-30', 135000),
        ("Nasri Attari", "admin4@hotmail.com", "nasri", 'Ramallah, Al-Berih', '0594601234', '2003-07-13', '2024-03-30', 135000),
    ]

    for name, email, password, address, carrier, dob, startDate, salary in admins:
        hashed_password = generate_password_hash(password)
        myCursor.execute(
            "INSERT INTO EMPLOYEE (NAME, ADDRESS, CARRIER, DATE_OF_BIRTH, START_DATE, BASE_SALARY, STATUS) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (name, address, carrier, dob, startDate, salary , 'CURRENT')
        )
        emp_id = myCursor.lastrowid
        myCursor.execute(
            "INSERT INTO ADMIN (EMP_ID, EMAIL, HASHED_PASSWORD) VALUES (%s, %s, %s)",
            (emp_id, email, hashed_password)
        )

def insertEmployees():
    employees = [
        ('Kevin Collins', '93032 Richmond Forge, West Laurie, PR 36868', '0593486253', '1962-11-02', '2022-01-20', 46300, 'CURRENT'),
        ('Justin Rivera', '208 Horn Hollow Apt. 338, New Susanshire, WA 57983', '0596281071', '2001-02-07', '2021-07-10', 84800, 'CURRENT'),
        ('Robert Hall', '211 Cannon Inlet, Ericfurt, MT 48193', '0597768396', '1964-04-26', '2021-02-03', 39800, 'CURRENT'),
        ('Kevin Henry', '369 Matthews Fords, East Tracyland, WA 07525', '0598527838', '1987-12-21', '2021-11-06', 87500, 'CURRENT'),
        ('Nichole Erickson', '352 Tracy Hill Apt. 973, Port Jeffreyview, LA 66914', '0593792746', '1990-11-27', '2021-07-04', 59700, 'CURRENT'),
        ('Ryan Levy', '60922 Kyle Ville, Oscarside, TX 33046', '0592479783', '1985-04-27', '2021-10-13', 88300, 'CURRENT'),
        ('Aaron Garcia', '782 Martinez Courts, Paulview, CA 15544', '0598481486', '1983-09-15', '2022-03-08', 33400, 'CURRENT'),
        ('Elizabeth Mcbride', '6621 Williams Village Suite 676, Johnsonville, IA 84531', '0594361283', '1990-04-11', '2022-07-01', 82400, 'CURRENT'),
        ('Glenn Jennings', '821 Erika Terrace Apt. 326, Anthonyside, CT 42702', '0599123557', '1978-01-14', '2021-09-07', 37000, 'CURRENT'),
        ('Timothy Woods', '94940 Pierce Place Apt. 886, North Josephchester, OK 03248', '0599380910', '1972-09-16', '2022-04-19', 73900, 'CURRENT'),
        ('Christopher Hernandez', '90413 Oliver Mountains, East Davidville, AL 86252', '0599617031', '2003-01-11', '2020-10-03', 93900, 'CURRENT'),
        ('Amy Wood', '906 Shaw Mission Suite 604, Jordanbury, DE 63801', '0592744752', '1959-06-15', '2021-02-24', 82500, 'CURRENT'),
        ('Cynthia Garner', '6299 Nicholas Cape, North Kathyville, PA 12694', '0595678704', '1993-09-11', '2022-03-31', 31200, 'CURRENT'),
        ('Francisco Brown', '73782 Nathan Burgs Apt. 646, Lake Theresa, ME 77730', '0599110340', '1960-01-29', '2023-07-22', 56000, 'CURRENT'),
        ('Tommy Dawson', '405 Christopher Street Apt. 168, North Christophermouth, VA 49872', '0593736301', '2003-01-23', '2020-05-09', 76700, 'CURRENT'),
    ]

    for employee in employees:
        myCursor.execute(
            "INSERT INTO EMPLOYEE (NAME, ADDRESS, CARRIER, DATE_OF_BIRTH, START_DATE, BASE_SALARY, STATUS) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            employee
        )

    myCursor.execute(
        """INSERT INTO SALES_EMP (EMP_ID, COMMISSION_RATE) VALUES
        (1, 0.06),  
        (2, 0.05),
        (3, 0.07),
        (4, 0.04),
        (5, 0.05),
        (6, 0.06),
        (7, 0.07),
        (8, 0.04),
        (9, 0.05);"""
    )

    myCursor.execute(
        """INSERT INTO OTHER_SERVICE_EMP (EMP_ID, SERVICE_TYPE) VALUES
        (10, 'Maintenance'),
        (11, 'Customer Support'),
        (12, 'Detailing'),
        (13, 'Repairs'),
        (14, 'Maintenance'),
        (15, 'Customer Support');"""
    )

def insertOptions():
    myCursor.execute("INSERT INTO OPTIONS (SUNROOF, HEATED_SEATS, GPS_NAVIGATION, BACKUP_CAMERA) VALUES (0, 0, 0, 1);")
    myCursor.execute("INSERT INTO OPTIONS (SUNROOF, HEATED_SEATS, GPS_NAVIGATION, BACKUP_CAMERA) VALUES (0, 1, 1, 0);")
    myCursor.execute("INSERT INTO OPTIONS (SUNROOF, HEATED_SEATS, GPS_NAVIGATION, BACKUP_CAMERA) VALUES (1, 1, 1, 1);")
    myCursor.execute("INSERT INTO OPTIONS (SUNROOF, HEATED_SEATS, GPS_NAVIGATION, BACKUP_CAMERA) VALUES (0, 0, 0, 1);")
    myCursor.execute("INSERT INTO OPTIONS (SUNROOF, HEATED_SEATS, GPS_NAVIGATION, BACKUP_CAMERA) VALUES (0, 1, 0, 1);")
    myCursor.execute("INSERT INTO OPTIONS (SUNROOF, HEATED_SEATS, GPS_NAVIGATION, BACKUP_CAMERA) VALUES (1, 1, 0, 0);")
    myCursor.execute("INSERT INTO OPTIONS (SUNROOF, HEATED_SEATS, GPS_NAVIGATION, BACKUP_CAMERA) VALUES (0, 1, 1, 1);")
    myCursor.execute("INSERT INTO OPTIONS (SUNROOF, HEATED_SEATS, GPS_NAVIGATION, BACKUP_CAMERA) VALUES (1, 0, 1, 1);")
    myCursor.execute("INSERT INTO OPTIONS (SUNROOF, HEATED_SEATS, GPS_NAVIGATION, BACKUP_CAMERA) VALUES (0, 0, 1, 1);")
    myCursor.execute("INSERT INTO OPTIONS (SUNROOF, HEATED_SEATS, GPS_NAVIGATION, BACKUP_CAMERA) VALUES (1, 1, 0, 1);")
    myDB.commit()    


def insertVehicleModels():
    myCursor.execute(
        """INSERT INTO VEHICLE_MODELS (CAR_BRAND, CAR_MODEL, NUM_OF_DOORS, CAR_COLOR, PETROL_TYPE, NUM_OF_PASS, TRANSMISSION_TYPE, MANUFACTURE_YEAR, PRICE, OP_ID) VALUES 
        ('Nissan', 'Altima', 4, 'Gray', 'GASOLINE', 4, 'automatic', 2023, 70000, 1),
        ('Kia', 'Sorento', 4, 'Blue', 'HYBRID', 4, 'automatic', 2024, 85000, 2),
        ('Chevrolet', 'Corvette', 2, 'Yellow', 'PETROL', 2, 'manual', 2023, 120000, 3),
        ('Honda', 'Civic', 4, 'Black', 'GASOLINE', 4, 'automatic', 2022, 75000, 4),
        ('Mazda', '6', 4, 'Red', 'HYBRID', 4, 'automatic', 2021, 78000, 5),
        ('Toyota', 'Corolla', 4, 'Blue', 'GASOLINE', 4, 'automatic', 2023, 72000, 6),
        ('BMW', '3 Series', 4, 'Black', 'HYBRID', 4, 'automatic', 2022, 95000, 7),
        ('Audi', 'A6', 4, 'Blue', 'HYBRID', 4, 'automatic', 2021, 87000, 8),
        ('Ford', 'Mustang', 2, 'Red', 'PETROL', 2, 'manual', 2020, 110000, 9),
        ('Mercedes', 'C-Class', 4, 'White', 'GASOLINE', 4, 'automatic', 2022, 98000, 10),
        ('Lexus', 'RX 350', 4, 'Gray', 'ELECTRICAL', 4, 'automatic', 2021, 90000, 2),
        ('Jaguar', 'F-Type', 2, 'Blue', 'PETROL', 2, 'automatic', 2023, 150000, 3),
        ('Volvo', 'XC90', 4, 'White', 'ELECTRICAL', 4, 'automatic', 2022, 100000, 4),
        ('Subaru', 'Outback', 4, 'Green', 'HYBRID', 4, 'automatic', 2023, 80000, 5),
        ('Hyundai', 'Sonata', 4, 'Blue', 'GASOLINE', 4, 'automatic', 2022, 77000, 6),
        ('Alfa Romeo', 'Giulia', 4, 'Red', 'PETROL', 4, 'manual', 2021, 95000, 7),
        ('Audi', 'Q5', 4, 'Silver', 'HYBRID', 4, 'automatic', 2018, 80000, 8),
        ('Chevrolet', 'Impala', 4, 'Blue', 'GASOLINE', 4, 'automatic', 2015, 70000, 9),
        ('Chevrolet', 'Malibu', 4, 'Red', 'PETROL', 4, 'automatic', 2014, 72000, 10),
        ('Chevrolet', 'Silverado', 4, 'Black', 'PETROL', 2, 'manual', 2018, 85000, 2),
        ('Ford', 'Explorer', 4, 'White', 'ELECTRICAL', 4, 'automatic', 2024, 95000, 3),
        ('Honda', 'CRV', 4, 'Red', 'HYBRID', 4, 'automatic', 2023, 80000, 4),
        ('Mercedes', 'GLE', 4, 'White', 'PETROL', 4, 'automatic', 2020, 110000, 5),
        ('Nissan', 'Sentra', 4, 'Blue', 'GASOLINE', 4, 'automatic', 2021, 70000, 6),
        ('Tesla', 'Model S', 4, 'Silver', 'ELECTRICAL', 4, 'automatic', 2016, 120000, 7),
        ('Tesla', 'Model Y', 4, 'Black', 'ELECTRICAL', 4, 'automatic', 2023, 95000, 8),
        ('Toyota', 'Camry', 4, 'White', 'HYBRID', 4, 'automatic', 2019, 85000, 9),
        ('Toyota', 'Prius', 4, 'Green', 'ELECTRICAL', 4, 'automatic', 2015, 72000, 10),
        ('Toyota', 'Rav4', 4, 'Blue', 'HYBRID', 4, 'automatic', 2023, 80000, 1),
        ('Volkswagen', 'Golf', 4, 'Yellow', 'GASOLINE', 4, 'automatic', 2015, 75000, 2);"""
    )
    myDB.commit()
    
def insertVehicles():
    myCursor.execute(
        """INSERT INTO VEHICLES (MODEL_ID, STATUS) VALUES 
        (1, 'AVAILABLE'),
        (2, 'AVAILABLE'),
        (3, 'AVAILABLE'),
        (4, 'AVAILABLE'),
        (5, 'AVAILABLE'),
        (6, 'AVAILABLE'),
        (7, 'AVAILABLE'),
        (8, 'AVAILABLE'),
        (9, 'AVAILABLE'),
        (10, 'AVAILABLE'),
        (11, 'AVAILABLE'),
        (12, 'AVAILABLE'),
        (13, 'AVAILABLE'),
        (14, 'AVAILABLE'),
        (15, 'AVAILABLE'),
        (16, 'AVAILABLE'),
        (17, 'AVAILABLE'),
        (18, 'AVAILABLE'),
        (19, 'AVAILABLE'),
        (20, 'AVAILABLE'),
        (21, 'AVAILABLE'),
        (22, 'AVAILABLE'),
        (23, 'AVAILABLE'),
        (24, 'AVAILABLE'),
        (25, 'AVAILABLE'),
        (26, 'AVAILABLE'),
        (27, 'AVAILABLE'),
        (28, 'AVAILABLE'),
        (29, 'AVAILABLE'),
        (30, 'AVAILABLE'),
        (12, 'AVAILABLE'),
        (21, 'AVAILABLE'),
        (7, 'AVAILABLE'),
        (19, 'AVAILABLE'),
        (30, 'AVAILABLE'),
        (3, 'AVAILABLE')"""
    )
    myDB.commit()
    
def insertCustomers():
    myCursor.execute(
        """INSERT INTO CUSTOMERS (CUS_NAME, ADDRESS, CARRIER, EMAIL, HASHED_PASSWORD) VALUES 
        ('John Doe', '123 Elm Street', '0593248929', 'johndoe@example.com', %s),
        ('Jane Smith', '456 Oak Avenue', '0596407250', 'janesmith@example.com', %s),
        ('Alice Johnson', '789 Pine Road', '0598366212', 'alicejohnson@example.com', %s),
        ('Bob Brown', '321 Maple Lane', '0594804440', 'bobbrown@example.com', %s),
        ('Charlie Davis', '654 Cedar Street', '0598032479', 'charliedavis@example.com', %s),
        ('Eve Black', '101 Birch Street', '0594768492', 'eveblack@example.com', %s),
        ('Frank White', '202 Pine Avenue', '0594056492', 'frankwhite@example.com', %s)""",
        (
            generate_password_hash("John"),
            generate_password_hash("Jane"),
            generate_password_hash("Alice"),
            generate_password_hash("Bob"),
            generate_password_hash("Charlie"),
            generate_password_hash("Eve"),
            generate_password_hash("Frank")
        )
    )


def insertPurchases():
    # Insert purchases directly
    myCursor.execute(
        """INSERT INTO SOLD_CARS (CAR_ID, DATE_OF_PURCHASE, PAYMENT_METHOD, CUS_ID, EMP_ID) VALUES 
        (1, '2023-05-15', 'cash', 1,5),
        (2, '2023-06-20', 'yearly payments', 2, 7),
        (3, '2023-07-25', 'monthly payments', 3, 8),
        (4, '2023-08-30', 'checks', 4, 6),
        (5, '2023-09-10', 'cash', 5, 5),
        (6, '2023-10-05', 'yearly payments', 5, 9);"""
    )

    # Update vehicle statuses directly
    myCursor.execute("UPDATE VEHICLES SET STATUS = 'SOLD' WHERE CAR_ID = 1;")
    myCursor.execute("UPDATE VEHICLES SET STATUS = 'SOLD' WHERE CAR_ID = 2;")
    myCursor.execute("UPDATE VEHICLES SET STATUS = 'SOLD' WHERE CAR_ID = 3;")
    myCursor.execute("UPDATE VEHICLES SET STATUS = 'SOLD' WHERE CAR_ID = 4;")
    myCursor.execute("UPDATE VEHICLES SET STATUS = 'SOLD' WHERE CAR_ID = 5;")
    myCursor.execute("UPDATE VEHICLES SET STATUS = 'SOLD' WHERE CAR_ID = 6;")

    # Insert non-sold cars with random arrival dates
    myCursor.execute(
        "SELECT CAR_ID FROM VEHICLES WHERE STATUS = 'AVAILABLE'"
    )
    available_cars = myCursor.fetchall()

    for car_id in available_cars:
        arrival_date = fake.date_this_decade()
        myCursor.execute(
            "INSERT INTO NON_SOLD_CARS (CAR_ID, DATE_OF_ARRIVAL) VALUES (%s, %s)",
            (car_id[0], arrival_date)
        )


main()
myCursor.close()
myDB.close()
