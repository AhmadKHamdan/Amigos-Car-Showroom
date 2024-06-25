from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    SubmitField,
    SelectField,
    SelectMultipleField,
)
from wtforms.validators import DataRequired, NumberRange
import random
from flask import redirect, url_for
import mysql.connector
import datetime
from flask_login import (
    UserMixin,
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

if __name__ == "__main__":
    app.run(debug=True, host="192.168.1.5", port=1234)


app.config["SECRET_KEY"] = "my key"
app.app_context()

#-------------------- LOGIN ROUTES -----------------#
#-------------------- LOGIN ROUTES -----------------#
#-------------------- LOGIN ROUTES -----------------#
#-------------------- LOGIN ROUTES -----------------#
#-------------------- LOGIN ROUTES -----------------#
#-------------------- LOGIN ROUTES -----------------#

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, email, name, password, isAdmin=False):
        self.id = email
        self.name = name
        self.password_hash = password
        self.isAdmin = isAdmin

    def checkPassword(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def cusFromDB(cls, email, name, password, isAdmin=False):
        user = cls(email, name, password, isAdmin)
        user.password_hash = password
        return user

    @classmethod
    def adminFromDB(cls, email, name, password):
        user = cls(email, name, password, True)
        user.password_hash = password
        return user

@login_manager.user_loader
def load_user(user_id):
    db = mysql.connector.connect(
        host="localhost", user="root", password="Ahmad2003", database="carShowroom"
    )
    cursor = db.cursor()

    cursor.execute(
        "SELECT E.NAME, A.EMAIL, A.HASHED_PASSWORD FROM ADMIN A JOIN EMPLOYEE E ON A.EMP_ID = E.EMP_ID WHERE A.EMAIL = %s", (user_id,)
    )
    admin_data = cursor.fetchone()
    if admin_data:
        cursor.close()
        db.close()
        return User.adminFromDB(admin_data[1], admin_data[0], admin_data[2])

    cursor.execute(
        "SELECT EMAIL, HASHED_PASSWORD, CUS_NAME FROM CUSTOMERS WHERE EMAIL = %s",
        (user_id,),
    )
    user_data = cursor.fetchone()
    cursor.close()
    db.close()

    if user_data:
        return User.cusFromDB(
            user_data[0], user_data[2].split(" ")[0].title(), user_data[1]
        )
    return None

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = mysql.connector.connect(
            host="localhost", user="root", password="Ahmad2003", database="carShowroom"
        )
        cursor = db.cursor()

        cursor.execute(
            "SELECT E.NAME, A.EMAIL, A.HASHED_PASSWORD FROM ADMIN A JOIN EMPLOYEE E ON A.EMP_ID = E.EMP_ID WHERE A.EMAIL = %s", (email,)
        )
        admin_data = cursor.fetchone()
        if admin_data:
            if check_password_hash(admin_data[2], password):
                user = User.adminFromDB(admin_data[1], admin_data[0], admin_data[2])
                login_user(user)
                cursor.close()
                db.close()
                return redirect(url_for("index"))
            else:
                flash("Invalid password for admin!", "error")
                cursor.close()
                db.close()
                return render_template("login.html")

        cursor = db.cursor()
        cursor.execute(
            "SELECT EMAIL, HASHED_PASSWORD, CUS_NAME FROM CUSTOMERS WHERE EMAIL = %s",
            (email,),
        )
        user_data = cursor.fetchone()
        cursor.close()
        db.close()

        if user_data:
            if check_password_hash(user_data[1], password):
                user = User.cusFromDB(
                    user_data[0], user_data[2].split(" ")[0], user_data[1]
                )
                login_user(user)
                return redirect(url_for("index"))
            else:
                flash("Invalid password for customer!", "error")
        else:
            flash("Invalid email or password!", "error")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        address = request.form["address"]
        password = request.form["password"]
        email = request.form["email"]
        phone = request.form["phone"]

        db = mysql.connector.connect(
            host="localhost", user="root", password="Ahmad2003", database="carShowroom"
        )
        cursor = db.cursor()

        cursor.execute("SELECT * FROM CUSTOMERS WHERE EMAIL = %s", (email,))
        if cursor.fetchone():
            flash("This email is taken!", "error")
            return render_template("register.html")

        hashedPassword = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO CUSTOMERS (CUS_NAME, ADDRESS, CARRIER, EMAIL, HASHED_PASSWORD) VALUES (%s, %s, %s, %s, %s)",
            (username, address, phone, email, hashedPassword),
        )
        db.commit()
        cursor.close()
        db.close()

        flash("User registered successfully!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if current_user.isAdmin:
        flash("Admins do not have a profile page.", "info")
        return redirect(url_for("index"))

    db = mysql.connector.connect(
        host="localhost", user="root", password="Ahmad2003", database="carShowroom"
    )
    cursor = db.cursor()

    # Get the logged-in user information
    user_email = current_user.id

    if request.method == "POST":
        # Update user information
        new_name = request.form["name"]
        new_address = request.form["address"]
        new_phone = request.form["phone"]

        cursor.execute(
            "UPDATE CUSTOMERS SET CUS_NAME = %s, ADDRESS = %s, CARRIER = %s WHERE EMAIL = %s",
            (new_name, new_address, new_phone, user_email),
        )
        db.commit()
        flash("Profile updated successfully!", "success")

    cursor.execute(
        "SELECT CUS_NAME, ADDRESS, CARRIER FROM CUSTOMERS WHERE EMAIL = %s",
        (user_email,),
    )
    user_data = cursor.fetchone()

    cursor.execute(
        """
        SELECT 
            vm.CAR_BRAND, 
            vm.CAR_MODEL, 
            sc.DATE_OF_PURCHASE, 
            e.NAME, 
            e.CARRIER, 
            sc.PAYMENT_METHOD 
        FROM SOLD_CARS sc
        JOIN VEHICLES v ON sc.CAR_ID = v.CAR_ID 
        JOIN VEHICLE_MODELS vm ON v.MODEL_ID = vm.MODEL_ID
        JOIN EMPLOYEE e ON sc.EMP_ID = e.EMP_ID 
        WHERE sc.CUS_ID = (SELECT CUS_ID FROM CUSTOMERS WHERE EMAIL = %s)
        """,
        (user_email,),
    )
    purchased_cars = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "profile.html", user_data=user_data, purchased_cars=purchased_cars
    )

#-------------------- ADMIN ROUTES -----------------#
#-------------------- ADMIN ROUTES -----------------#
#-------------------- ADMIN ROUTES -----------------#
#-------------------- ADMIN ROUTES -----------------#
#-------------------- ADMIN ROUTES -----------------#
#-------------------- ADMIN ROUTES -----------------#

# Create a route decorator
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/allcars", methods=["GET","POST"])
@login_required
def allCars():
    if not current_user.isAdmin:
        return redirect(url_for("index"))

    if request.method == "POST":
        # Process form data and redirect to a clean URL
        return redirect(url_for("allcars"))

    db = mysql.connector.connect(
        host="localhost", user="root", password="Ahmad2003", database="carShowroom"
    )
    cursor = db.cursor()
    # Construct the query dynamically based on provided filters
    conditions = []
    parameters = []
    status = request.args.get("status")
    brand = request.args.get("brand")
    color = request.args.get("color")
    petrol_type = request.args.get("petrol_type")
    num_of_doors = request.args.get("num_of_doors")
    transmission_type = request.args.get("transmission_type")

    if status:
        conditions.append("v.STATUS = %s")
        parameters.append(status)
    if brand:
        conditions.append("vm.CAR_BRAND = %s")
        parameters.append(brand)
    if color:
        conditions.append("vm.CAR_COLOR = %s")
        parameters.append(color)
    if petrol_type:
        conditions.append("vm.PETROL_TYPE = %s")
        parameters.append(petrol_type)
    if num_of_doors:
        conditions.append("vm.NUM_OF_DOORS = %s")
        parameters.append(num_of_doors)
    if transmission_type:
        conditions.append("vm.TRANSMISSION_TYPE = %s")
        parameters.append(transmission_type)

    query = """
    SELECT v.CAR_ID, vm.CAR_BRAND, vm.CAR_MODEL, vm.CAR_COLOR, vm.PETROL_TYPE, 
           vm.NUM_OF_DOORS, vm.NUM_OF_PASS, vm.TRANSMISSION_TYPE, vm.MANUFACTURE_YEAR, vm.PRICE, 
           v.STATUS, o.SUNROOF, o.HEATED_SEATS, o.GPS_NAVIGATION, o.BACKUP_CAMERA
    FROM VEHICLES v
    JOIN VEHICLE_MODELS vm ON v.MODEL_ID = vm.MODEL_ID
    JOIN OPTIONS o ON o.OP_ID = vm.OP_ID
    """
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, parameters)
    cars = cursor.fetchall()

    cursor.execute("SELECT DISTINCT CAR_BRAND FROM VEHICLE_MODELS")
    brands = [brand[0] for brand in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT CAR_COLOR FROM VEHICLE_MODELS")
    colors = [color[0] for color in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT PETROL_TYPE FROM VEHICLE_MODELS")
    petrol_types = [pt[0] for pt in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT TRANSMISSION_TYPE FROM VEHICLE_MODELS")
    transmission_types = [tt[0] for tt in cursor.fetchall()]

    cursor.close()
    db.close()

    return render_template(
        "allCars.html",
        cars=cars,
        brands=brands,
        colors=colors,
        petrol_types=petrol_types,
        transmission_types=transmission_types,
        selected_filters=request.args,
    )

@app.route("/duplicatecar/<int:car_id>", methods=["POST"])
@login_required
def duplicate_car_route(car_id):
    if not current_user.isAdmin:
        return redirect(url_for("index"))

    db = mysql.connector.connect(
        host="localhost", user="root", password="Ahmad2003", database="carShowroom"
    )
    cursor = db.cursor()

    # Fetch the details of the car to be duplicated
    cursor.execute("SELECT MODEL_ID FROM VEHICLES WHERE CAR_ID = %s", (car_id,))
    car_data = cursor.fetchone()
    
    if car_data:
        model_id = car_data[0]
        # Insert a new car with the same model_id and status set to 'AVAILABLE'
        cursor.execute(
            "INSERT INTO VEHICLES (MODEL_ID, STATUS) VALUES (%s, %s)",
            (model_id, 'AVAILABLE')
        )
        db.commit()
    
    cursor.close()
    db.close()
    flash("Car duplicated successfully!", "success")
    return redirect(url_for("allCars"))

@app.route("/updatestatus/<int:car_id>/<string:action>", methods=["POST"])
@login_required
def updateCarStatus(car_id, action):
    if not current_user.isAdmin:
        return redirect(url_for("index"))
    
    db = mysql.connector.connect(
        host="localhost", user="root", password="Ahmad2003", database="carshowroom"
    )
    cursor = db.cursor()
    
    # Check the current status of the car
    cursor.execute("SELECT STATUS FROM VEHICLES WHERE CAR_ID = %s", (car_id,))
    result = cursor.fetchone()
    
    if result:
        current_status = result[0]
        
        if action == "delete" and current_status == "AVAILABLE":
            # Update the status to 'NOT-AVAILABLE'
            cursor.execute("UPDATE VEHICLES SET STATUS = 'NOT-AVAILABLE' WHERE CAR_ID = %s", (car_id,))
            flash("Car status updated to 'NOT-AVAILABLE' successfully!", "success")
        elif action == "retrieve" and current_status == "NOT-AVAILABLE":
            # Update the status to 'AVAILABLE'
            cursor.execute("UPDATE VEHICLES SET STATUS = 'AVAILABLE' WHERE CAR_ID = %s", (car_id,))
            flash("Car status updated to 'AVAILABLE' successfully!", "success")
        else:
            flash("Invalid action or car status!", "danger")
    else:
        flash("Car not found!", "danger")
    
    db.commit()
    cursor.close()
    db.close()
    
    return redirect(url_for("allCars"))

@app.route("/soldCars")
@login_required
def soldCars():
    if not current_user.isAdmin:
        flash("Access denied.", "danger")
        return redirect(url_for("index"))

    db = mysql.connector.connect(
        host="localhost", user="root", password="Ahmad2003", database="carShowroom"
    )

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT 
            vm.CAR_BRAND, 
            vm.CAR_MODEL, 
            sc.DATE_OF_PURCHASE, 
            c.CUS_NAME, 
            c.ADDRESS, 
            c.CARRIER, 
            vm.PRICE,
            e.NAME,
            e.CARRIER
        FROM 
            SOLD_CARS sc
        JOIN VEHICLES v ON sc.CAR_ID = v.CAR_ID
        JOIN VEHICLE_MODELS vm ON v.MODEL_ID = vm.MODEL_ID
        JOIN CUSTOMERS c ON sc.CUS_ID = c.CUS_ID
        JOIN EMPLOYEE e ON sc.EMP_ID = e.EMP_ID
        """
    )

    soldCars = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("soldCars.html", soldCars=soldCars)

@app.route("/addnewcar", methods=["GET", "POST"])
@login_required
def addNewCar():
    if not current_user.isAdmin:
        return redirect(url_for("index"))
    
    db = mysql.connector.connect(
        host="localhost", user="root", password="Ahmad2003", database="carShowroom"
    )
    cursor = db.cursor()

    form = vehicleForm()
    if form.validate_on_submit():
        options = [opt for opt in form.options.data if opt]

        addVehicleToDataBase(
            db=db,
            cursor=cursor,
            brand=form.brand.data,
            numOfDoors=form.numOfDoors.data,
            carColor=form.carColor.data,
            carModel=form.carModel.data,
            petrolType=form.petrolType.data,
            numOfPass=form.numOfPass.data,
            transmissionType=form.transmissionType.data,
            manufactureYear=form.manufactureYear.data,
            price=form.price.data,
            options=options,
            status=form.status.data,
        )
        flash("Vehicle added successfully!", "success")

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for("addNewCar"))
    
    return render_template("addNewCar.html", form=form)

#-------------------- ADMIN ROUTES FOR EMPLOYEES -----------------#
#-------------------- ADMIN ROUTES FOR EMPLOYEES -----------------#
#-------------------- ADMIN ROUTES FOR EMPLOYEES -----------------#
#-------------------- ADMIN ROUTES FOR EMPLOYEES -----------------#
#-------------------- ADMIN ROUTES FOR EMPLOYEES -----------------#
#-------------------- ADMIN ROUTES FOR EMPLOYEES -----------------#

@app.route("/employees")
@login_required
def viewEmployees():
    if not current_user.isAdmin:
        return redirect(url_for("index"))

    db = mysql.connector.connect(
        host="localhost", user="root", password="Ahmad2003", database="carShowroom"
    )
    cursor = db.cursor()

    # First query: Get all sales employee information
    cursor.execute(
        """
        SELECT e.EMP_ID, e.NAME, e.ADDRESS, e.CARRIER, e.DATE_OF_BIRTH, e.START_DATE, e.BASE_SALARY, s.COMMISSION_RATE, e.STATUS
        FROM EMPLOYEE e
        JOIN SALES_EMP s ON e.EMP_ID = s.EMP_ID
        """
    )
    salesEmployees = cursor.fetchall()

    # Second query: Get the sum of sales amounts for each employee
    cursor.execute(
        """
        SELECT sc.EMP_ID, SUM(vm.PRICE) AS TOTAL_SALES
        FROM SOLD_CARS sc
        JOIN VEHICLES v ON sc.CAR_ID = v.CAR_ID
        JOIN VEHICLE_MODELS vm ON v.MODEL_ID = vm.MODEL_ID
        GROUP BY sc.EMP_ID
        """
    )
    salesTotals = cursor.fetchall()
    salesTotalsDict = {emp_id: total_sales if total_sales is not None else 0 for emp_id, total_sales in salesTotals}

    # Combine the results
    combinedSalesEmployees = []
    for emp in salesEmployees:
        emp_id = emp[0]
        total_sales = salesTotalsDict.get(emp_id, 0)
        combinedSalesEmployees.append(emp + (total_sales,))

    # Query for other service employees
    cursor.execute(
        """
        SELECT e.EMP_ID, e.NAME, e.ADDRESS, e.CARRIER, e.DATE_OF_BIRTH, e.START_DATE, e.BASE_SALARY, o.SERVICE_TYPE, e.STATUS
        FROM EMPLOYEE e
        JOIN OTHER_SERVICE_EMP o ON e.EMP_ID = o.EMP_ID
        """
    )
    otherEmployees = cursor.fetchall()

    cursor.close()
    db.close()
    return render_template(
        "employees.html", salesEmployees=combinedSalesEmployees, otherEmployees=otherEmployees
    )

@app.route("/addEmployee", methods=["GET", "POST"])
@login_required
def addEmployee():
    if not current_user.isAdmin:
        return redirect(url_for("index"))

    today = datetime.datetime.today().strftime("%Y-%m-%d")
    if request.method == "POST":
        emp_type = request.form.get("employeeType")
        name = request.form["name"]
        address = request.form["address"]
        phone = request.form["phone"]
        dob = request.form["dob"]
        start_date = request.form["startDate"]
        salary = request.form["salary"]

        db = mysql.connector.connect(
            host="localhost", user="root", password="Ahmad2003", database="carShowroom"
        )
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO EMPLOYEE (NAME, ADDRESS, CARRIER, DATE_OF_BIRTH, START_DATE, BASE_SALARY) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, address, phone, dob, start_date, salary),
        )
        emp_id = cursor.lastrowid

        if emp_type == "Sales":
            commission_rate = request.form.get("commissionRate", type=float)
            cursor.execute(
                "INSERT INTO SALES_EMP (EMP_ID, COMMISSION_RATE) VALUES (%s, %s)",
                (emp_id, commission_rate),
            )
        else:
            service_type = request.form.get("serviceType")
            cursor.execute(
                "INSERT INTO OTHER_SERVICE_EMP (EMP_ID, SERVICE_TYPE) VALUES (%s, %s)",
                (emp_id, service_type),
            )

        db.commit()
        cursor.close()
        db.close()
        flash("Employee added successfully!", "success")
        return redirect(url_for("viewEmployees"))

    return render_template("addEmployee.html", today=today)

@app.route("/updateemployeestatus/<int:emp_id>/<string:action>")
@login_required
def updateEmployeeStatus(emp_id, action):
    if not current_user.isAdmin:
        return redirect(url_for("index"))

    db = mysql.connector.connect(
        host="localhost", user="root", password="Ahmad2003", database="carShowroom"
    )
    cursor = db.cursor()

    # Check the current status of the employee
    cursor.execute("SELECT STATUS FROM EMPLOYEE WHERE EMP_ID = %s", (emp_id,))
    result = cursor.fetchone()

    if result:
        current_status = result[0]

        if action == "delete" and current_status == "CURRENT":
            # Update the status to 'FORMER'
            cursor.execute("UPDATE EMPLOYEE SET STATUS = 'FORMER' WHERE EMP_ID = %s", (emp_id,))
            flash("Employee status updated to 'FORMER' successfully!", "success")
        elif action == "retrieve" and current_status == "FORMER":
            # Update the status to 'CURRENT'
            cursor.execute("UPDATE EMPLOYEE SET STATUS = 'CURRENT' WHERE EMP_ID = %s", (emp_id,))
            flash("Employee status updated to 'CURRENT' successfully!", "success")
        else:
            flash("Invalid action or employee status!", "danger")
    else:
        flash("Employee not found!", "danger")

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for("viewEmployees"))

@app.route("/updateemployee/<int:emp_id>", methods=["GET", "POST"])
@login_required
def updateEmployee(emp_id):
    if not current_user.isAdmin:
        return redirect(url_for("index"))

    db = mysql.connector.connect(
        host="localhost", user="root", password="Ahmad2003", database="carShowroom"
    )
    cursor = db.cursor()
    
    if request.method == "POST":
        name = request.form["name"]
        address = request.form["address"]
        phone = request.form["phone"]
        dob = request.form["dob"]
        start_date = request.form["start_date"]
        salary = request.form["salary"]
        emp_type = request.form["emp_type"]
        
        cursor.execute(
            "UPDATE EMPLOYEE SET NAME=%s, ADDRESS=%s, CARRIER=%s, DATE_OF_BIRTH=%s, START_DATE=%s, BASE_SALARY=%s WHERE EMP_ID=%s",
            (name, address, phone, dob, start_date, salary, emp_id)
        )
        
        if emp_type == "sales":
            commission_rate = request.form["commission_rate"]
            cursor.execute(
                "UPDATE SALES_EMP SET COMMISSION_RATE=%s WHERE EMP_ID=%s",
                (commission_rate, emp_id)
            )
        elif emp_type == "non_sales":
            service_type = request.form["service_type"]
            cursor.execute(
                "UPDATE OTHER_SERVICE_EMP SET SERVICE_TYPE=%s WHERE EMP_ID=%s",
                (service_type, emp_id)
            )
        
        db.commit()
        cursor.close()
        db.close()
        flash("Employee information updated successfully!", "success")
        return redirect(url_for("viewEmployees"))
    else:
        cursor.execute("SELECT * FROM EMPLOYEE WHERE EMP_ID = %s", (emp_id,))
        employee = cursor.fetchone()
        
        cursor.execute("SELECT * FROM SALES_EMP WHERE EMP_ID = %s", (emp_id,))
        sales_employee = cursor.fetchone()
        
        cursor.execute("SELECT * FROM OTHER_SERVICE_EMP WHERE EMP_ID = %s", (emp_id,))
        non_sales_employee = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        return render_template(
            "updateEmployee.html",
            employee=employee,
            sales_employee=sales_employee,
            non_sales_employee=non_sales_employee
        )

#-------------------- CUSTOMER ROUTES  -----------------#
#-------------------- CUSTOMER ROUTES  -----------------#
#-------------------- CUSTOMER ROUTES  -----------------#
#-------------------- CUSTOMER ROUTES  -----------------#
#-------------------- CUSTOMER ROUTES  -----------------#
#-------------------- CUSTOMER ROUTES  -----------------#


@app.route("/buycar", methods=["GET", "POST"])
def buyCar():
    db = mysql.connector.connect(
        host="localhost", user="root", password="Ahmad2003", database="carShowroom"
    )
    cursor = db.cursor()

    # Construct the query dynamically based on provided filters
    conditions = []
    parameters = []
    brand = request.args.get("brand")
    color = request.args.get("color")
    petrol_type = request.args.get("petrol_type")
    num_of_doors = request.args.get("num_of_doors")
    transmission_type = request.args.get("transmission_type")
    sort_by = request.args.get("sort_by", "vm.CAR_BRAND")
    order = request.args.get("order", "ASC")

    if brand:
        conditions.append("vm.CAR_BRAND = %s")
        parameters.append(brand)
    if color:
        conditions.append("vm.CAR_COLOR = %s")
        parameters.append(color)
    if petrol_type:
        conditions.append("vm.PETROL_TYPE = %s")
        parameters.append(petrol_type)
    if num_of_doors:
        conditions.append("vm.NUM_OF_DOORS = %s")
        parameters.append(num_of_doors)
    if transmission_type:
        conditions.append("vm.TRANSMISSION_TYPE = %s")
        parameters.append(transmission_type)

    query = """
    SELECT 
        MIN(v.CAR_ID), vm.CAR_BRAND, vm.CAR_MODEL, vm.MANUFACTURE_YEAR, vm.PRICE
    FROM 
        VEHICLES v
    JOIN 
        VEHICLE_MODELS vm ON v.MODEL_ID = vm.MODEL_ID
    WHERE 
        v.STATUS = 'AVAILABLE'
    """
    if conditions:
        query += " AND " + " AND ".join(conditions)
    query += f" GROUP BY vm.CAR_BRAND, vm.CAR_MODEL, vm.MANUFACTURE_YEAR, vm.PRICE ORDER BY {sort_by} {order}"

    cursor.execute(query, parameters)
    cars = cursor.fetchall()

    cursor.execute("SELECT DISTINCT CAR_BRAND FROM VEHICLE_MODELS")
    brands = [brand[0] for brand in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT CAR_COLOR FROM VEHICLE_MODELS")
    colors = [color[0] for color in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT PETROL_TYPE FROM VEHICLE_MODELS")
    petrol_types = [pt[0] for pt in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT TRANSMISSION_TYPE FROM VEHICLE_MODELS")
    transmission_types = [tt[0] for tt in cursor.fetchall()]

    cursor.close()
    db.close()

    # Pre-format image filenames
    cars = [
        {
            "id": car[0],
            "brand": car[1],
            "model": car[2],
            "manufacture_year": car[3],
            "price": car[4],
            "image_filename": f"{car[1]}_{car[2]}_{car[3]}.jpg"
        }
        for car in cars
    ]

    return render_template(
        "buyCar.html",
        cars=cars,
        brands=brands,
        colors=colors,
        petrol_types=petrol_types,
        transmission_types=transmission_types,
        selected_filters=request.args,
    )

@app.route("/car/<int:car_id>")
def carDetails(car_id):
    db = mysql.connector.connect(
        host="localhost", user="root", password="Ahmad2003", database="carShowroom"
    )
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT v.CAR_ID, m.CAR_BRAND, m.CAR_MODEL, m.CAR_COLOR, m.PETROL_TYPE, m.NUM_OF_DOORS, 
               m.TRANSMISSION_TYPE, m.MANUFACTURE_YEAR, m.PRICE, o.SUNROOF, o.HEATED_SEATS, 
               o.GPS_NAVIGATION, o.BACKUP_CAMERA
        FROM VEHICLES v
        JOIN VEHICLE_MODELS m ON v.MODEL_ID = m.MODEL_ID
        JOIN OPTIONS o ON m.OP_ID = o.OP_ID
        WHERE v.CAR_ID = %s AND v.STATUS = 'AVAILABLE'
        """, 
        (car_id,)
    )
    car = cursor.fetchone()
    if car:
        car = {
            "id": car[0],
            "brand": car[1],
            "model": car[2],
            "color": car[3],
            "petrol_type": car[4],
            "num_of_doors": car[5],
            "transmission_type": car[6],
            "manufacture_year": car[7],
            "price": car[8],
            "sunroof": car[9],
            "heated_seats": car[10],
            "gps_navigation": car[11],
            "backup_camera": car[12],
            "image_filename": f"{car[1]}_{car[2]}_{car[7]}.jpg"
        }
    cursor.close()
    db.close()

    if car:
        return render_template("carDetails.html", car=car)
    else:
        return render_template("404.html"), 404

@app.route("/car/<int:car_id>/purchase", methods=["POST"])
@login_required
def purchaseCar(car_id):
    if not current_user.is_authenticated:
        flash("You need to log in to purchase a car.", "error")
        return redirect(url_for("carDetails", car_id=car_id))

    # Check if the user is an admin or employee
    if current_user.isAdmin:
        flash("Employees and admins cannot purchase cars.", "error")
        return redirect(url_for("carDetails", car_id=car_id))

    db = mysql.connector.connect(
        host="localhost", user="root", password="Ahmad2003", database="carShowroom"
    )
    cursor = db.cursor()

    user_email = current_user.id

    # Ensure the user is a customer
    cursor.execute("SELECT CUS_ID FROM CUSTOMERS WHERE EMAIL = %s", (user_email,))
    result = cursor.fetchone()
    if not result:
        flash("Employees and admins cannot purchase cars.", "error")
        cursor.close()
        db.close()
        return redirect(url_for("carDetails", car_id=car_id))

    cus_id = result[0]

    payment_method = request.form.get('payment_method')
    if not payment_method:
        flash("Payment method is required.", "error")
        return redirect(url_for("carDetails", car_id=car_id))

    # Update vehicle status to SOLD
    cursor.execute("UPDATE VEHICLES SET STATUS='SOLD' WHERE CAR_ID=%s", (car_id,))

    DATE_OF_PURCHASE = datetime.datetime.today().strftime("%Y-%m-%d")

    # Fetch a random EMP_ID from SALES_EMP
    cursor.execute("SELECT se.EMP_ID FROM SALES_EMP se JOIN EMPLOYEE e ON se.EMP_ID = e.EMP_ID WHERE e.STATUS = 'CURRENT'")
    sales_emp_ids = [item[0] for item in cursor.fetchall()]

    if not sales_emp_ids:
        flash("No sales employees found to complete the purchase.", "error")
        db.rollback()
        cursor.close()
        db.close()
        return redirect(url_for("carDetails", car_id=car_id))

    emp_id = random.choice(sales_emp_ids)

    cursor.execute(
        "INSERT INTO SOLD_CARS (CAR_ID, DATE_OF_PURCHASE, CUS_ID, EMP_ID, PAYMENT_METHOD) VALUES (%s, %s, %s, %s, %s)",
        (car_id, DATE_OF_PURCHASE, cus_id, emp_id, payment_method),
    )

    cursor.execute("DELETE FROM NON_SOLD_CARS WHERE CAR_ID=%s", (car_id,))

    db.commit()
    cursor.close()
    db.close()

    flash("Purchase successful!", "success")
    return redirect(url_for("index"))

# Create custom error pages

# Invalid URL
@app.errorhandler(404)
def pageNotFound(e):
    return render_template("404.html"), 404

# Internal Server URL
@app.errorhandler(500)
def pageNotFound(e):
    return render_template("500.html"), 500

def addVehicleToDataBase(
    db,
    cursor,
    brand,
    numOfDoors,
    carColor,
    carModel,
    petrolType,
    numOfPass,
    transmissionType,
    manufactureYear,
    price,
    options,
    status,
):
    # Define the options as boolean values
    options_dict = {
        'Sunroof': 0,
        'Heated seats': 0,
        'GPS navigation': 0,
        'Backup camera': 0
    }
    
    for option in options:
        if option in options_dict:
            options_dict[option] = 1

    # Check if the options set already exists
    cursor.execute(
        """
        SELECT OP_ID FROM OPTIONS WHERE SUNROOF=%s AND HEATED_SEATS=%s AND GPS_NAVIGATION=%s AND BACKUP_CAMERA=%s
        """,
        (
            options_dict['Sunroof'],
            options_dict['Heated seats'],
            options_dict['GPS navigation'],
            options_dict['Backup camera']
        ),
    )
    result = cursor.fetchall()
    if result:
        result = result[0]
    
    if result:
        op_id = result[0]
    else:
        # Insert the new options set
        cursor.execute(
            """
            INSERT INTO OPTIONS (SUNROOF, HEATED_SEATS, GPS_NAVIGATION, BACKUP_CAMERA)
            VALUES (%s, %s, %s, %s)
            """,
            (
                options_dict['Sunroof'],
                options_dict['Heated seats'],
                options_dict['GPS navigation'],
                options_dict['Backup camera']
            ),
        )
        op_id = cursor.lastrowid

    # Insert into VEHICLE_MODELS table
    cursor.execute(
        """
        INSERT INTO VEHICLE_MODELS (
            CAR_BRAND, CAR_MODEL, NUM_OF_DOORS, CAR_COLOR, PETROL_TYPE, 
            NUM_OF_PASS, TRANSMISSION_TYPE, MANUFACTURE_YEAR, PRICE, OP_ID
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            brand,
            carModel,
            numOfDoors,
            carColor,
            petrolType,
            numOfPass,
            transmissionType,
            manufactureYear,
            price,
            op_id,
        ),
    )
    model_id = cursor.lastrowid

    # Insert into VEHICLES table
    cursor.execute(
        """
        INSERT INTO VEHICLES (
            MODEL_ID, STATUS
        ) VALUES (%s, %s)
        """,
        (
            model_id,
            status,
        ),
    )
    car_id = cursor.lastrowid

    # Fetch a random EMP_ID from SALES_EMP
    cursor.execute("SELECT EMP_ID FROM SALES_EMP")
    sales_emp_ids = [item[0] for item in cursor.fetchall()]

    if sales_emp_ids:
        emp_id = random.choice(sales_emp_ids)

        # Insert into NON_SOLD_CARS table
        cursor.execute(
            "INSERT INTO NON_SOLD_CARS (CAR_ID, DATE_OF_ARRIVAL) VALUES (%s, %s)",
            (car_id, datetime.datetime.now().strftime("%Y-%m-%d")),
        )

    db.commit()

# Create a form class
class vehicleForm(FlaskForm):
    brand = StringField("Brand", validators=[DataRequired()])
    numOfDoors = SelectField(
        "Number of Doors",
        choices=[("2", "2"), ("4", "4")],
        validators=[DataRequired()],
    )
    carColor = StringField("Car Color", validators=[DataRequired()])
    carModel = StringField("Car Model", validators=[DataRequired()])
    petrolType = SelectField(
        "Petrol Type",
        choices=[
            ("Gasoline", "Gasoline"),
            ("Diesel", "Diesel"),
            ("Electric", "Electric"),
            ("Hybrid", "Hybrid"),
        ],
        validators=[DataRequired()],
    )
    numOfPass = SelectField(
        "Number of Passengers",
        choices=[("2", "2"), ("5", "5"), ("7", "7")],
        validators=[DataRequired()],
    )
    transmissionType = SelectField(
        "Transmission Type",
        choices=[("Automatic", "Automatic"), ("Manual", "Manual")],
        validators=[DataRequired()],
    )
    current_year = datetime.datetime.now().year
    manufactureYear = IntegerField(
        "Manufacture Year",
        validators=[
            DataRequired(),
            NumberRange(
                min=1950,
                max=current_year,
                message=f"Year must be between 1950 and {current_year}",
            ),
        ],
    )
    price = IntegerField(
        "Price",
        validators=[
            DataRequired(),
            NumberRange(
                min=50000,
                max=3000000,
                message="Price must be between ₪50,000 and ₪3,000,000",
            ),
        ],
    )
    options = SelectMultipleField(
        "Options",
        choices=[
            ("GPS navigation", "GPS navigation"),
            ("Backup camera", "Backup camera"),
            ("Heated seats", "Heated seats"),
            ("Sunroof", "Sunroof"),
        ],
    )
    status = SelectField(
        "Status",
        choices=[("AVAILABLE", "AVAILABLE"), ("SOLD", "SOLD")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Add")