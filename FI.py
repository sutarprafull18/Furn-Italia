import streamlit as st
import pandas as pd
import uuid
from PIL import Image
import io

# Set page configuration
st.set_page_config(
    page_title="Furn Italia - Premium Furniture",
    page_icon="🪑",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-family: 'Serif';
        color: #4E3524;
    }
    .product-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        transition: transform 0.3s;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .category-badge {
        background-color: #f8f9fa;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 14px;
        color: #4E3524;
    }
    .img-container {
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .spec-table {
        width: 100%;
    }
    .spec-table td {
        padding: 8px;
        border-bottom: 1px solid #f0f0f0;
    }
    .spec-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .gallery-image {
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Sample data
sample_data = {
    'id': ['1'],
    'name': ['Premium Leather Sofa'],
    'description': ['Luxurious 3-seater leather sofa with premium craftsmanship. Perfect for modern living rooms with its elegant design and exceptional comfort.'],
    'images': [['https://via.placeholder.com/800x600?text=Premium+Furniture']]
}

# Initialize session state variables if they don't exist
if 'products' not in st.session_state:
    st.session_state.products = pd.DataFrame(sample_data)

if 'current_product' not in st.session_state:
    st.session_state.current_product = None

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Function to display homepage with all products
def show_homepage():
    # Header with logo
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://via.placeholder.com/150x80?text=Furn+Italia", width=150)
    with col2:
        st.markdown("<h1 class='main-header'>Furn Italia - Furniture Collection</h1>", unsafe_allow_html=True)

    # Display products in grid layout
    st.markdown(f"## Our Furniture Collection {f'({len(st.session_state.products)} items)' if not st.session_state.products.empty else ''}")

    if not st.session_state.products.empty:
        # Create rows with 3 products per row
        for i in range(0, len(st.session_state.products), 3):
            cols = st.columns(3)

            for j in range(3):
                if i + j < len(st.session_state.products):
                    product = st.session_state.products.iloc[i + j]

                    with cols[j]:
                        with st.container():
                            st.markdown(f"<div class='product-card'>", unsafe_allow_html=True)

                            # Display first image with zoom functionality
                            if product['images'] and len(product['images']) > 0:
                                try:
                                    st.image(product['images'][0], width=300)
                                except:
                                    st.image("https://via.placeholder.com/400x300?text=Image+Not+Available", width=300)

                            st.subheader(product['name'])

                            # View product button
                            if st.button(f"View Details", key=f"view_{product['id']}"):
                                st.session_state.current_product = product['id']
                                st.session_state.page = 'product_detail'
                                st.rerun()

                            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No furniture items available.")

    # Add footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>© 2025 Furn Italia. All rights reserved.</p>
        <p>Premium Furniture for Every Space</p>
    </div>
    """, unsafe_allow_html=True)

# Function to display product detail page
def show_product_detail():
    product_id = st.session_state.current_product
    product = st.session_state.products[st.session_state.products['id'] == product_id].iloc[0]

    # Back button
    if st.button("← Back to Products"):
        st.session_state.page = 'home'
        st.session_state.current_product = None
        st.rerun()

    # Product Details
    st.markdown(f"<h1 class='main-header'>{product['name']}</h1>", unsafe_allow_html=True)

    # Main image display first
    if product['images'] and len(product['images']) > 0:
        st.markdown("<h2>Main Image</h2>", unsafe_allow_html=True)
        st.image(product['images'][0])

    # Description
    st.markdown("<h2>Details</h2>", unsafe_allow_html=True)
    st.markdown("<h3>Product Description</h3>", unsafe_allow_html=True)
    st.markdown(product['description'])

    # Display all images at full size
    if product['images'] and len(product['images']) > 0:
        st.markdown("<h2>All Images</h2>", unsafe_allow_html=True)

        for i, img_path in enumerate(product['images']):
            st.image(img_path, caption=f"Image {i+1}", use_column_width=False)
            st.markdown("<div class='gallery-image'></div>", unsafe_allow_html=True)

# Function to add a new product
def add_product():
    st.header("Add New Product")

    name = st.text_input("Product Name", placeholder="e.g. Leather Recliner Chair")
    description = st.text_area("Product Description", placeholder="Detailed description of the furniture item...", height=150)

    # Upload multiple images
    st.subheader("Product Images")
    uploaded_files = st.file_uploader("Upload product images", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

    image_urls = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Generate a unique filename
            file_ext = os.path.splitext(uploaded_file.name)[1]
            filename = f"{uuid.uuid4()}{file_ext}"

            # Save the file locally (optional, if you want to keep a local copy)
            with io.BytesIO() as buffer:
                buffer.write(uploaded_file.getbuffer())
                image = Image.open(buffer)
                image_url = f"https://via.placeholder.com/800x600?text={filename}"  # Placeholder URL
                image_urls.append(image_url)
                st.image(image, caption=uploaded_file.name)

    if st.button("Add Product", type="primary"):
        if name and description and image_urls:
            # Generate a unique ID for the product
            product_id = str(uuid.uuid4())[:8]

            # Create a new product entry
            new_product = {
                'id': product_id,
                'name': name,
                'description': description,
                'images': image_urls
            }

            # Add the new product to the dataframe
            st.session_state.products = pd.concat([
                st.session_state.products,
                pd.DataFrame([new_product])
            ], ignore_index=True)

            st.success("Product added successfully!")
        else:
            st.error("Please fill in all required fields (name, description, and images).")

# Main navigation
def main():
    # Add logo and navigation in sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/240x120?text=Furn+Italia", width=240)
        st.markdown("<h3>Navigation</h3>", unsafe_allow_html=True)

        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = 'home'
            st.session_state.current_product = None
            st.rerun()

        if st.button("➕ Add Product", use_container_width=True):
            st.session_state.page = 'add_product'
            st.rerun()

        st.markdown("---")

        # Customer support information
        st.markdown("""
        <h3>Customer Support</h3>
        <p>📞 Call us: +91 8390839090</p>
        <p>📧 Email: furnitalia.sales@gmail.com</p>
        <p>⏰ Mon-Sun: 10AM - 9PM</p>
        """, unsafe_allow_html=True)

    # Display the appropriate page based on the current state
    if st.session_state.page == 'home':
        show_homepage()
    elif st.session_state.page == 'add_product':
        add_product()
    elif st.session_state.page == 'product_detail':
        show_product_detail()

if __name__ == "__main__":
    main()
