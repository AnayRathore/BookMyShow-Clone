import streamlit as st
from db import *
from pages import login_page, movies_page, seat_selection_page, payment_page, booking_details_page, booking_history_page, admin_page

def main():
    # Ensure the user is logged in before proceeding to other pages
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'

    conn = init_db()  # Use init_db to initialize the connection

    # Routing for different pages based on the user's current session state
    if st.session_state['page'] == 'login':
        login_page(conn)
    elif st.session_state['page'] == 'movies':
        movies_page(conn)
    elif st.session_state['page'] == 'seat_selection':
        seat_selection_page(conn)
    elif st.session_state['page'] == 'payment':
        payment_page()
    elif st.session_state['page'] == 'booking_details':
        booking_details_page(conn)
    elif st.session_state['page'] == 'booking_history':
        booking_history_page(conn)
    elif st.session_state['page'] == 'admin':
        admin_page(conn)

if __name__ == "__main__":
    main()
