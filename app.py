from flask import Flask, render_template, request, redirect, session, send_file
from database import get_db_connection
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import io

app = Flask(__name__)
app.secret_key="cybercrimeportal123"

UPLOAD_FOLDER = "static/uploads"

app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Home Page
@app.route('/')
def home():
    return render_template("index.html")


# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            return "Email already registered! Please login."

        cursor.execute(
            "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)",
            (name, email, phone, password)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return "Registration Successful!"

    return render_template("register.html")


# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session["user"] = user["name"]
            session["email"] = user["email"]
            return render_template("dashboard.html", username=user["name"])
        else:
            return "Invalid Email or Password!"

    return render_template("login.html")


# File Complaint
@app.route('/complaint', methods=['GET', 'POST'])
def complaint():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        crime_type = request.form['crime_type']
        complaint = request.form['complaint']
        location = request.form['location']
        complaint_date = request.form['complaint_date']

        evidence = request.files['evidence']
        filename = ""

        if evidence.filename != "":
            filename = evidence.filename
            evidence.save(

                os.path.join(app.config['UPLOAD_FOLDER'], filename)
            )
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
    """
    INSERT INTO complaints
    (name,email,phone,crime_type,complaint,location,complaint_date,status,evidence)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """,
    (
        name,
        email,
        phone,
        crime_type,
        complaint,
        location,
        complaint_date,
        "Pending",
        filename
    )
)

        conn.commit()

        cursor.close()
        conn.close()

        return render_template("dashboard.html", username=session.get("user"), message="Complaint Submitted Successfully!")

    return render_template("complaint.html")


# Admin Login
@app.route('/admin', methods=['GET', 'POST'])
def admin():

    if session.get("admin"):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM complaints")
        complaints = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS total FROM complaints")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS pending FROM complaints WHERE status='Pending'")
        pending = cursor.fetchone()["pending"]

        cursor.execute("SELECT COUNT(*) AS progress FROM complaints WHERE status='In Progress'")
        progress = cursor.fetchone()["progress"]

        cursor.execute("SELECT COUNT(*) AS resolved FROM complaints WHERE status='Resolved'")
        resolved = cursor.fetchone()["resolved"]

        #Crime type analysis

        cursor.execute("""SELECT crime_type, COUNT(*) AS count FROM complaints GROUP BY crime_type""")
        crime_data = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            "admin_dashboard.html",
            complaints=complaints,
            total=total,
            pending=pending,
            progress=progress,
            resolved=resolved,
            crime_data=crime_data
        )


    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']


        if username == "admin" and password == "admin123":

            session["admin"] = True

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True) 

            cursor.execute("SELECT * FROM complaints")
            complaints = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) AS total FROM complaints")
            total = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS pending FROM complaints WHERE status='Pending'")
            pending = cursor.fetchone()["pending"]

from flask import Flask, render_template, request, redirect, session, send_file
from database import get_db_connection
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import io

app = Flask(__name__)
app.secret_key="cybercrimeportal123"

UPLOAD_FOLDER = "static/uploads"

app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Home Page
@app.route('/')
def home():
    return render_template("index.html")


# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            return "Email already registered! Please login."

        cursor.execute(
            "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)",
            (name, email, phone, password)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return "Registration Successful!"

    return render_template("register.html")


# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session["user"] = user["name"]
            session["email"] = user["email"]
            return render_template("dashboard.html", username=user["name"])
        else:
            return "Invalid Email or Password!"

    return render_template("login.html")


# File Complaint
@app.route('/complaint', methods=['GET', 'POST'])
def complaint():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        crime_type = request.form['crime_type']
        complaint = request.form['complaint']
        location = request.form['location']
        complaint_date = request.form['complaint_date']

        evidence = request.files['evidence']
        filename = ""

        if evidence.filename != "":
            filename = evidence.filename
            evidence.save(

                os.path.join(app.config['UPLOAD_FOLDER'], filename)
            )
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
    """
    INSERT INTO complaints
    (name,email,phone,crime_type,complaint,location,complaint_date,status,evidence)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """,
    (
        name,
        email,
        phone,
        crime_type,
        complaint,
        location,
        complaint_date,
        "Pending",
        filename
    )
)

        conn.commit()

        cursor.close()
        conn.close()

        return render_template("dashboard.html", username=session.get("user"), message="Complaint Submitted Successfully!")

    return render_template("complaint.html")


# -------------------- Admin Login --------------------

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
        else:
            return "Invalid Admin Credentials!"

    if session.get("admin"):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM complaints")
        complaints = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS total FROM complaints")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS pending FROM complaints WHERE status='Pending'")
        pending = cursor.fetchone()["pending"]

        cursor.execute("SELECT COUNT(*) AS progress FROM complaints WHERE status='In Progress'")
        progress = cursor.fetchone()["progress"]

        cursor.execute("SELECT COUNT(*) AS resolved FROM complaints WHERE status='Resolved'")
        resolved = cursor.fetchone()["resolved"]

        cursor.execute("""
            SELECT crime_type, COUNT(*) AS count
            FROM complaints
            GROUP BY crime_type
        """)
        crime_data = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            "admin_dashboard.html",
            complaints=complaints,
            total=total,
            pending=pending,
            progress=progress,
            resolved=resolved,
            crime_data=crime_data
        )

    return render_template("admin_login.html")


# Update Complaint Status
@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):

    status = request.form['status']

    print("Updating Complaint ID:", id)
    print("New Status:", status)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE complaints SET status=%s WHERE id=%s",
        (status, id)
    )

    conn.commit()

    print("Rows Updated:", cursor.rowcount)

    cursor.close()
    conn.close()


    return redirect('/admin')

# View Complaint Details
@app.route('/complaint_details/<int:id>')
def complaint_details(id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM complaints WHERE id=%s",
        (id,)
    )

    complaint = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("complaint_details.html", complaint=complaint)
    


# Run Application

@app.route('/delete_complaint/<int:id>', methods=['POST'])
def delete_complaint(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM complaints WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/admin')

@app.route('/admin_logout')
def admin_logout():
    session.pop("admin", None)
    return redirect('/admin')

@app.route('/status')
def status():

    if "email" not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM complaints WHERE email=%s",
        (session["email"],)
    )

    complaints = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("status.html", complaints=complaints)

@app.route('/generate_pdf/<int:id>')
def generate_pdf(id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM complaints WHERE id=%s",
        (id,)
    )

    complaint = cursor.fetchone()

    cursor.close()
    conn.close()


    pdf = io.BytesIO()

    c = canvas.Canvas(pdf, pagesize=letter)


    c.setFont("Helvetica-Bold", 16)
    c.drawString(150, 750, "Cyber Crime Complaint Report")


    c.setFont("Helvetica", 12)

    y = 700

    data = [
        "Complaint ID: " + str(complaint['id']),
        "Name: " + complaint['name'],
        "Email: " + complaint['email'],
        "Phone: " + complaint['phone'],
        "Crime Type: " + complaint['crime_type'],
        "Location: " + complaint['location'],
        "Date: " + str(complaint['complaint_date']),
        "Status: " + complaint['status'],
        "Description: " + complaint['complaint']
    ]


    for line in data:
        c.drawString(80, y, line)
        y -= 30


    c.save()

    pdf.seek(0)


    return send_file(
        pdf,
        download_name="Complaint_Report.pdf",
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)




# Update Complaint Status
@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):

    status = request.form['status']

    print("Updating Complaint ID:", id)
    print("New Status:", status)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE complaints SET status=%s WHERE id=%s",
        (status, id)
    )

    conn.commit()

    print("Rows Updated:", cursor.rowcount)

    cursor.close()
    conn.close()


    return redirect('/admin')

# View Complaint Details
@app.route('/complaint_details/<int:id>')
def complaint_details(id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM complaints WHERE id=%s",
        (id,)
    )

    complaint = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("complaint_details.html", complaint=complaint)
    


# Run Application

@app.route('/delete_complaint/<int:id>', methods=['POST'])
def delete_complaint(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM complaints WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/admin')

@app.route('/admin_logout')
def admin_logout():
    session.pop("admin", None)
    return redirect('/admin')

@app.route('/status')
def status():

    if "email" not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM complaints WHERE email=%s",
        (session["email"],)
    )

    complaints = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("status.html", complaints=complaints)

@app.route('/generate_pdf/<int:id>')
def generate_pdf(id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM complaints WHERE id=%s",
        (id,)
    )

    complaint = cursor.fetchone()

    cursor.close()
    conn.close()


    pdf = io.BytesIO()

    c = canvas.Canvas(pdf, pagesize=letter)


    c.setFont("Helvetica-Bold", 16)
    c.drawString(150, 750, "Cyber Crime Complaint Report")


    c.setFont("Helvetica", 12)

    y = 700

    data = [
        "Complaint ID: " + str(complaint['id']),
        "Name: " + complaint['name'],
        "Email: " + complaint['email'],
        "Phone: " + complaint['phone'],
        "Crime Type: " + complaint['crime_type'],
        "Location: " + complaint['location'],
        "Date: " + str(complaint['complaint_date']),
        "Status: " + complaint['status'],
        "Description: " + complaint['complaint']
    ]


    for line in data:
        c.drawString(80, y, line)
        y -= 30


    c.save()

    pdf.seek(0)


    return send_file(
        pdf,
        download_name="Complaint_Report.pdf",
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)