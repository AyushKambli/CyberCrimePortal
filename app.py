from flask import Flask, render_template, request, redirect, session, send_file
from database import get_db_connection
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename
import os
import io

app = Flask(__name__)
app.secret_key = "cybercrimeportal123"

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# User Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM users WHERE email=%s",
                (email,)
            )
            if cursor.fetchone():
                return "Email already registered! Please login."

            cursor.execute(
                """INSERT INTO users (name, email, phone, password)
                   VALUES (%s, %s, %s, %s)""",
                (name, email, phone, password)
            )
            conn.commit()
            return "Registration Successful! Please login."
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")


# User Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT * FROM users WHERE email=%s AND password=%s",
                (email, password)
            )
            user = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if user:
            session["user"] = user["name"]
            session["email"] = user["email"]
            return render_template(
                "dashboard.html",
                username=user["name"]
            )

        return "Invalid Email or Password!"

    return render_template("login.html")


# File Complaint
@app.route("/complaint", methods=["GET", "POST"])
def complaint():
    if "email" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        email = session["email"]
        phone = request.form["phone"]
        crime_type = request.form["crime_type"]
        description = request.form["complaint"]
        location = request.form["location"]
        complaint_date = request.form["complaint_date"]

        evidence = request.files.get("evidence")
        filename = ""

        if evidence and evidence.filename:
            filename = secure_filename(evidence.filename)
            if filename:
                evidence.save(
                    os.path.join(app.config["UPLOAD_FOLDER"], filename)
                )

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO complaints
                (name, email, phone, crime_type, complaint,
                 location, complaint_date, status, evidence)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    name, email, phone, crime_type, description,
                    location, complaint_date, "Pending", filename
                )
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

        return render_template(
            "dashboard.html",
            username=session.get("user"),
            message="Complaint Submitted Successfully!"
        )

    return render_template("complaint.html")


# Admin Login and Dashboard
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin")

        return "Invalid Admin Credentials!"

    if not session.get("admin"):
        return render_template("admin_login.html")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM complaints")
        complaints = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS total FROM complaints")
        total = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS pending FROM complaints WHERE status=%s",
            ("Pending",)
        )
        pending = cursor.fetchone()["pending"]

        cursor.execute(
            "SELECT COUNT(*) AS progress FROM complaints WHERE status=%s",
            ("In Progress",)
        )
        progress = cursor.fetchone()["progress"]

        cursor.execute(
            "SELECT COUNT(*) AS resolved FROM complaints WHERE status=%s",
            ("Resolved",)
        )
        resolved = cursor.fetchone()["resolved"]

        cursor.execute(
            """SELECT crime_type, COUNT(*) AS count
               FROM complaints GROUP BY crime_type"""
        )
        crime_data = cursor.fetchall()
    finally:
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


# Update Complaint Status
@app.route("/update_status/<int:id>", methods=["POST"])
def update_status(id):
    if not session.get("admin"):
        return redirect("/admin")

    status_value = request.form["status"]
    allowed_statuses = ["Pending", "In Progress", "Resolved"]

    if status_value not in allowed_statuses:
        return "Invalid complaint status!", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE complaints SET status=%s WHERE id=%s",
            (status_value, id)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return redirect("/admin")


# View Complaint Details
@app.route("/complaint_details/<int:id>")
def complaint_details(id):
    if not session.get("admin"):
        return redirect("/admin")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM complaints WHERE id=%s",
            (id,)
        )
        complaint_record = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not complaint_record:
        return "Complaint not found", 404

    return render_template(
        "complaint_details.html",
        complaint=complaint_record
    )


# Delete Complaint
@app.route("/delete_complaint/<int:id>", methods=["POST"])
def delete_complaint(id):
    if not session.get("admin"):
        return redirect("/admin")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM complaints WHERE id=%s", (id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return redirect("/admin")


# Admin Logout
@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin")


# User Complaint Status
@app.route("/status")
def status():
    if "email" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM complaints WHERE email=%s",
            (session["email"],)
        )
        complaints = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template("status.html", complaints=complaints)


# Download Complaint PDF
@app.route("/generate_pdf/<int:id>")
def generate_pdf(id):
    if "email" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM complaints WHERE id=%s AND email=%s",
            (id, session["email"])
        )
        complaint_record = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not complaint_record:
        return "Complaint not found", 404

    pdf = io.BytesIO()
    c = canvas.Canvas(pdf, pagesize=letter)
    page_width, page_height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(60, page_height - 60, "Cyber Crime Complaint Report")

    c.setFont("Helvetica", 11)
    y = page_height - 100

    data = [
        f"Complaint ID: {complaint_record['id']}",
        f"Name: {complaint_record['name']}",
        f"Email: {complaint_record['email']}",
        f"Phone: {complaint_record['phone']}",
        f"Crime Type: {complaint_record['crime_type']}",
        f"Location: {complaint_record['location']}",
        f"Date: {complaint_record['complaint_date']}",
        f"Status: {complaint_record['status']}",
        "Description:"
    ]

    for line in data:
        c.drawString(60, y, line)
        y -= 22

    description = str(complaint_record["complaint"])
    for start in range(0, len(description), 85):
        if y < 60:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = page_height - 60

        c.drawString(60, y, description[start:start + 85])
        y -= 18

    c.save()
    pdf.seek(0)

    return send_file(
        pdf,
        mimetype="application/pdf",
        download_name="Complaint_Report.pdf",
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)