import streamlit as st
from db import *

def login_page(conn):
    st.title("BookMyShow - Login/Signup")
    choice = st.radio("Choose an option", ["Login", "Signup"])

    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = get_user(conn, username)
            if user is None:
                st.error("User not found. Please check your credentials.")
            elif not verify_password(password, user[2]):
                st.error("Incorrect password!")
            elif len(user) < 4 or user[3] not in ["user", "admin"]:
                st.error("User role is missing or invalid!")
            else:
                st.session_state['user'] = user
                st.session_state['page'] = 'movies' if user[3] == 'user' else 'admin'
    elif choice == "Signup":
        username = st.text_input("Choose a Username")
        password = st.text_input("Choose a Password", type="password")
        if st.button("Signup"):
            try:
                add_user(conn, username, password)
                st.success("Signup successful! Please login.")
            except sqlite3.IntegrityError:
                st.error("Username already exists!")

def movies_page(conn):
    st.title("BookMyShow - Movies")
    if st.button("Log Out"):
        st.session_state.clear()
        st.session_state['page'] = 'login'
    
    if st.button("View Booking History"):
        st.session_state['page'] = 'booking_history'
    
    movies = get_movies(conn)
    for movie in movies:
        st.subheader(movie[1])
        st.text(movie[2])
        st.text(f"Seats Available: {movie[3]}")
        
        shows = get_movie_shows(conn, movie[0])
        for show in shows:
            st.write(f"Show: {show[1]} | Price: ${show[2]:.2f}")
            if st.button(f"Book {movie[1]} - {show[1]}", key=f"{movie[0]}-{show[0]}"):
                st.session_state['movie'] = movie
                st.session_state['show'] = show
                st.session_state['page'] = 'seat_selection'

def seat_selection_page(conn):
    st.title("Select Seats")
    movie = st.session_state.get('movie')
    show = st.session_state.get('show')
    if not movie or not show:
        st.error("No movie or show selected!")
        st.session_state['page'] = 'movies'
        return
    
    available_seats = movie[3]
    st.write(f"Seats Available: {available_seats}")
    selected_seats = st.multiselect("Select Seats", range(1, available_seats + 1))
    
    if selected_seats:
        st.write(f"You have selected: {', '.join(map(str, selected_seats))}")
    
    if st.button("Confirm Seats"):
        if len(selected_seats) > available_seats:
            st.error("Not enough seats available!")
        elif not selected_seats:
            st.error("Please select at least one seat.")
        else:
            user_id = st.session_state['user'][0]
            book_seats(conn, user_id, movie[0], show[0], selected_seats)
            st.success(f"Seats booked: {', '.join(map(str, selected_seats))}")
            st.session_state['seats'] = selected_seats
            st.session_state['page'] = 'payment'

def payment_page():
    st.title("Payment")
    show = st.session_state.get('show')
    seats = st.session_state.get('seats')
    total_amount = len(seats) * show[2]  # Price per seat for the selected show
    st.write(f"Total Amount: ${total_amount:.2f}")

    payment_method = st.radio("Select Payment Method", ["Credit Card", "Debit Card", "PayPal", "Cash"])
    if st.button("Make Payment"):
        if payment_method:
            st.success(f"Payment of ${total_amount:.2f} via {payment_method} successful!")
            st.session_state['page'] = 'booking_details'
        else:
            st.error("Please select a payment method.")


def booking_details_page(conn):
    st.title("Booking Details")
    movie = st.session_state.get('movie')
    seats = st.session_state.get('seats')
    show = st.session_state.get('show')
    if not movie or not seats or not show:
        st.error("No booking details available!")
        st.session_state['page'] = 'movies'
        return
    
    st.write(f"Movie: {movie[1]}")
    st.write(f"Show: {show[1]}")
    st.write(f"Seats: {', '.join(map(str, seats))}")
    st.write("Thank you for booking with us!")
    if st.button("Back to Movies"):
        del st.session_state['movie']
        del st.session_state['show']
        del st.session_state['seats']
        st.session_state['page'] = 'movies'


def booking_history_page(conn):
    st.title("Booking History")
    user_id = st.session_state['user'][0]
    bookings = get_booking_history(conn, user_id)
    
    if bookings:
        for movie_name, show_time, seats in bookings:
            st.subheader(movie_name)
            st.write(f"Show: {show_time}")
            st.write(f"Seats: {seats}")
    else:
        st.write("No bookings found.")
    
    if st.button("Back to Movies"):
        st.session_state['page'] = 'movies'

def admin_page(conn):
    st.title("Admin Dashboard")
    st.write("Add a new movie:")
    
    name = st.text_input("Movie Name")
    description = st.text_area("Movie Description")
    seats_available = st.number_input("Available Seats", min_value=1, step=1)
    
    if st.button("Add Movie"):
        if name and description and seats_available > 0:
            add_movie(conn, name, description, seats_available)
            st.success("Movie added successfully!")
    
    st.write("Add show timings and pricing:")
    movie_id = st.number_input("Movie ID", min_value=1, step=1)
    show_time = st.text_input("Show Time (YYYY-MM-DD HH:MM)")
    price = st.number_input("Price", min_value=0.0, step=0.1)
    
    if st.button("Add Show"):
        if movie_id and show_time and price > 0:
            add_movie_show(conn, movie_id, show_time, price)
            st.success("Show added successfully!")

    if st.button("Log Out"):
        st.session_state.clear()
        st.session_state['page'] = 'login'
