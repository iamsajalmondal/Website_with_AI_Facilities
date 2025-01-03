import pymysql
import bcrypt


def get_connection():
    return pymysql.connect(
        host="127.0.0.1",  # or "localhost"
        user="root",
        password="Sajal01@242001",  # Replace with the actual password
        database="user_auth",
        port=3306,  # Optional, defaults to 3306
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def sign_up(username, password, email, full_name):
    if not username or not password or not email:
        return "Error: Username, email, and password are required."

    if len(password) < 8:
        return "Error: Password must be at least 8 characters long."

    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            # Check if username already exists
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return "Error: Username already exists."
            
            # Check if email already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return "Error: Email is already registered."

            # Hash the password before storing it
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            # Insert the new user into the database
            cursor.execute("INSERT INTO users (username, password_hash, email, full_name) VALUES (%s, %s, %s, %s)",
                           (username, hashed_password, email, full_name))
            connection.commit()

        return "Sign-up successful! Please log in."
    
    finally:
        connection.close()


def log_in(username, password):
    if not username or not password:
        return "Error: Username and password are required."

    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            # Check if the user exists
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if not user:
                return "Error: Invalid username or password."

            # Check if the password matches the stored hash
            if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
                return "Error: Invalid username or password."

        return "Login successful! Welcome back."

    finally:
        connection.close()