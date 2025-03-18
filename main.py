import streamlit as st
import sys
import os

# Add the app directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

# Set page configuration
st.set_page_config(
    page_title="Furn Italia - Premium Furniture",
    page_icon="🪑",
    layout="wide"
)

# Side panel for navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("---")

# Navigation buttons
if st.sidebar.button("🏠 Home"):
    st.session_state.page = 'home'

if st.sidebar.button("🛋️ Product 1"):
    st.session_state.page = 'product_1'

if st.sidebar.button("🛋️ Product 2"):
    st.session_state.page = 'product_2'

# Display the selected page
if st.session_state.get('page') == 'home':
    import home
    home.show_homepage()
elif st.session_state.get('page') == 'product_1':
    import product_1
    product_1.show_product_detail()
elif st.session_state.get('page') == 'product_2':
    import product_2
    product_2.show_product_detail()
else:
    import home
    home.show_homepage()
