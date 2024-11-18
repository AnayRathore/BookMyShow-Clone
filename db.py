import sqlite3
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def init_db():
    conn = sqlite3.connect("bookmyshow.db")
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            seats_available INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movie_shows (
            id INTEGER PRIMARY KEY,
            movie_id INTEGER,
            show_time TEXT,
            price REAL,
            FOREIGN KEY(movie_id) REFERENCES movies(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            movie_id INTEGER,
            show_id INTEGER,
            seats TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(movie_id) REFERENCES movies(id),
            FOREIGN KEY(show_id) REFERENCES movie_shows(id)
        )
    ''')

    # Insert sample users
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users = [
            ("admin", hash_password("admin123"), "admin"),
            ("user1", hash_password("password1"), "user"),
            ("user2", hash_password("password2"), "user")
        ]
        cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", users)
        conn.commit()

    # Insert sample movies
    cursor.execute("SELECT COUNT(*) FROM movies")
    if cursor.fetchone()[0] == 0:
        movies = [
            ("Inception", "A mind-bending thriller by Christopher Nolan.", 50),
            ("The Dark Knight", "A superhero crime thriller by Christopher Nolan.", 40)
        ]
        cursor.executemany("INSERT INTO movies (name, description, seats_available) VALUES (?, ?, ?)", movies)
        conn.commit()

    # Insert sample shows
    cursor.execute("SELECT COUNT(*) FROM movie_shows")
    if cursor.fetchone()[0] == 0:
        shows = [
            (1, "2024-11-18 18:00", 12.5),
            (1, "2024-11-18 21:00", 15.0),
            (2, "2024-11-18 19:00", 10.0)
        ]
        cursor.executemany("INSERT INTO movie_shows (movie_id, show_time, price) VALUES (?, ?, ?)", shows)
        conn.commit()

    return conn

def get_user(conn, username):
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, role FROM users WHERE username=?", (username,))
    return cursor.fetchone()

def add_user(conn, username, password):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'user')", (username, hash_password(password)))
    conn.commit()

def get_movies(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies")
    return cursor.fetchall()

def add_movie(conn, name, description, seats_available):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO movies (name, description, seats_available) VALUES (?, ?, ?)", (name, description, seats_available))
    conn.commit()

def add_movie_show(conn, movie_id, show_time, price):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO movie_shows (movie_id, show_time, price) VALUES (?, ?, ?)", (movie_id, show_time, price))
    conn.commit()

# The previously provided part remains unchanged, we just ensure that every function that manages movie shows works with the new database schema.

# Adding functions for retrieving movie shows, and booking for a specific show.
def get_movie_shows(conn, movie_id):
    cursor = conn.cursor()
    cursor.execute("SELECT id, show_time, price FROM movie_shows WHERE movie_id = ?", (movie_id,))
    return cursor.fetchall()

def book_seats(conn, user_id, movie_id, show_id, seats):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bookings (user_id, movie_id, show_id, seats) VALUES (?, ?, ?, ?)", 
                   (user_id, movie_id, show_id, ",".join(map(str, seats))))
    conn.commit()
    num_seats_selected = len(seats)
    cursor.execute("UPDATE movies SET seats_available = seats_available - ? WHERE id = ?", 
                   (num_seats_selected, movie_id))
    conn.commit()


def get_booking_history(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.name, s.show_time, b.seats 
        FROM bookings b
        INNER JOIN movies m ON b.movie_id = m.id
        INNER JOIN movie_shows s ON b.show_id = s.id
        WHERE b.user_id = ?
    ''', (user_id,))
    return cursor.fetchall()
