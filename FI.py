import streamlit as st
import pandas as pd
import os
import uuid
import json
import hashlib
from PIL import Image
import io
import base64
import time

# Set page configuration
st.set_page_config(
    page_title="Furn Italia - Premium Furniture",
    page_icon="🪑",
    layout="wide"
)

# Constants
ADMIN_USERNAME = "fiadmin"
ADMIN_PASSWORD_HASH = hashlib.sha256("8788474749@Fi".encode()).hexdigest()
DATA_FILE = "furniture_data.json"

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
    .price-tag {
        font-size: 24px;
        font-weight: bold;
        color: #4E3524;
    }
    .discount-tag {
        color: #28a745;
        font-weight: bold;
    }
    .original-price {
        text-decoration: line-through;
        color: gray;
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
        overflow: hidden;
        border-radius: 5px;
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
</style>
""", unsafe_allow_html=True)

# Functions for data persistence
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error loading data: {e}")
    
    # Return default data if file doesn't exist or there's an error
    return pd.DataFrame({
        'id': ['1'],
        'name': ['Premium Leather Sofa'],
        'price': [79999.99],
        'discount_price': [59999.99],
        'category': ['Living Room'],
        'rating': [4.7],
        'description': ['Luxurious 3-seater leather sofa with premium craftsmanship. Perfect for modern living rooms with its elegant design and exceptional comfort. The premium Italian leather upholstery ensures durability and a sophisticated appearance that elevates any space.'],
        'specifications': [{
            'Material': 'Genuine Italian Leather', 
            'Dimensions': '220cm × 95cm × 85cm (W×D×H)', 
            'Frame': 'Kiln-dried hardwood',
            'Seating Capacity': '3 persons',
            'Weight': '45 kg',
            'Assembly': 'No assembly required',
            'Warranty': '3 years on frame, 1 year on upholstery',
            'Color': 'Rich Brown'
        }],
        'images': [['/sample_sofa.jpg']],
        'stock': [5]
    })

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data.to_dict('records'), f)

# Function to save an uploaded image
def save_image(uploaded_file):
    if uploaded_file is not None:
        # Create images directory if it doesn't exist
        if not os.path.exists('images'):
            os.makedirs('images')
        
        # Generate a unique filename
        file_ext = os.path.splitext(uploaded_file.name)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join('images', filename)
        
        # Save the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    return None

# Initialize session state variables if they don't exist
if 'products' not in st.session_state:
    st.session_state.products = load_data()

if 'current_product' not in st.session_state:
    st.session_state.current_product = None

if 'page' not in st.session_state:
    st.session_state.page = 'home'

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# Admin login function
def admin_login():
    st.markdown("<h2 class='main-header'>Admin Login</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if username == ADMIN_USERNAME and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD_HASH:
                st.session_state.admin_logged_in = True
                st.success("Login successful!")
                time.sleep(1)  # Small delay for better UX
                st.rerun()
            else:
                st.error("Invalid username or password")

# Function to display product management page
def show_product_management():
    if not st.session_state.admin_logged_in:
        admin_login()
        return
    
    st.markdown("<h1 class='main-header'>Furn Italia Product Management</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Add New Product", "View/Edit Products"])
    
    with tab1:
        st.header("Add New Product")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Product Name", placeholder="e.g. Leather Recliner Chair")
            
            # Furniture specific categories
            category = st.selectbox("Category", [
                "Living Room", "Bedroom", "Dining Room", "Office", 
                "Outdoor", "Kitchen", "Bathroom", "Kids Room", "Storage"
            ])
            
            price = st.number_input("Regular Price (₹)", min_value=0.0, format="%.2f")
            discount_price = st.number_input("Sale Price (₹)", min_value=0.0, format="%.2f")
            rating = st.slider("Rating", 0.0, 5.0, 4.5, 0.1)
            stock = st.number_input("Stock Available", min_value=0, value=1)
            
        with col2:
            description = st.text_area("Product Description", 
                                      placeholder="Detailed description of the furniture item...",
                                      height=150)
            
            # Upload multiple images
            st.subheader("Product Images")
            uploaded_files = st.file_uploader("Upload product images (recommended size: 800x600px)", 
                                             accept_multiple_files=True, 
                                             type=['png', 'jpg', 'jpeg'])
            
            image_paths = []
            if uploaded_files:
                image_cols = st.columns(min(3, len(uploaded_files)))
                for i, uploaded_file in enumerate(uploaded_files):
                    with image_cols[i % 3]:
                        image_path = save_image(uploaded_file)
                        if image_path:
                            image_paths.append(image_path)
                            st.image(uploaded_file, width=200, caption=uploaded_file.name)
        
        # Expanded specifications section
        st.subheader("Product Specifications")
        with st.expander("Add Specifications", expanded=True):
            specs = {}
            
            # Common furniture specifications with default fields
            furniture_specs = {
                "Material": st.text_input("Material", placeholder="e.g. Teak Wood, Leather, etc."),
                "Dimensions": st.text_input("Dimensions", placeholder="e.g. 180cm × 90cm × 75cm (W×D×H)"),
                "Weight": st.text_input("Weight", placeholder="e.g. 45 kg"),
                "Color": st.text_input("Color", placeholder="e.g. Walnut Brown"),
                "Assembly": st.selectbox("Assembly Required", ["Yes", "No", "Partial"]),
                "Warranty": st.text_input("Warranty", placeholder="e.g. 1 year on manufacturing defects")
            }
            
            # Add furniture-specific specs based on category
            if category == "Living Room":
                furniture_specs["Seating Capacity"] = st.text_input("Seating Capacity", placeholder="e.g. 3 persons")
                furniture_specs["Upholstery"] = st.text_input("Upholstery", placeholder="e.g. Premium Fabric")
            
            elif category == "Bedroom":
                furniture_specs["Mattress Size"] = st.text_input("Mattress Size", placeholder="e.g. Queen, King")
                furniture_specs["Storage Type"] = st.text_input("Storage Type", placeholder="e.g. Drawer, Under-bed")
            
            elif category == "Dining Room":
                furniture_specs["Seating Capacity"] = st.text_input("Seating Capacity", placeholder="e.g. 6 persons")
                furniture_specs["Table Shape"] = st.text_input("Table Shape", placeholder="e.g. Rectangle, Round")
            
            elif category == "Office":
                furniture_specs["Maximum Load"] = st.text_input("Maximum Load", placeholder="e.g. 100 kg")
                furniture_specs["Features"] = st.text_input("Features", placeholder="e.g. Adjustable Height, Swivel")
            
            # Custom specifications (allow for 3 custom specs)
            st.subheader("Additional Specifications")
            for i in range(3):
                cols = st.columns(2)
                with cols[0]:
                    key = st.text_input(f"Custom Spec Name {i+1}", key=f"custom_key_{i}")
                with cols[1]:
                    value = st.text_input(f"Custom Spec Value {i+1}", key=f"custom_value_{i}")
                if key and value:
                    furniture_specs[key] = value
            
            # Filter out empty specs
            for k, v in furniture_specs.items():
                if v:  # Only add non-empty specs
                    specs[k] = v
        
        if st.button("Add Product", type="primary"):
            if name and price and description and (image_paths or len(image_paths) == 0):
                # Generate a unique ID for the product
                product_id = str(uuid.uuid4())[:8]
                
                # Create a new product entry
                new_product = {
                    'id': product_id,
                    'name': name,
                    'price': price,
                    'discount_price': discount_price,
                    'category': category,
                    'rating': rating,
                    'description': description,
                    'specifications': specs,
                    'images': image_paths if image_paths else ['/sample_furniture.jpg'],
                    'stock': stock
                }
                
                # Add the new product to the dataframe
                st.session_state.products = pd.concat([
                    st.session_state.products, 
                    pd.DataFrame([new_product])
                ], ignore_index=True)
                
                # Save to persistent storage
                save_data(st.session_state.products)
                
                st.success("Product added successfully!")
                st.balloons()
            else:
                st.error("Please fill in all required fields (name, price, and description).")
    
    with tab2:
        st.header("View/Edit Products")
        
        # Display products in a dataframe with minimal columns for overview
        if not st.session_state.products.empty:
            # Create a display version of the dataframe with fewer columns
            display_df = st.session_state.products[['id', 'name', 'price', 'discount_price', 'category', 'stock']].copy()
            
            # Format the price columns
            display_df['price'] = display_df['price'].apply(lambda x: f"₹{x:,.2f}")
            display_df['discount_price'] = display_df['discount_price'].apply(lambda x: f"₹{x:,.2f}")
            
            # Display the dataframe
            st.dataframe(display_df, height=300)
            
            # Product selection for actions
            product_names = st.session_state.products['name'].tolist()
            selected_product = st.selectbox("Select a product for actions:", product_names)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("View Product", type="primary"):
                    product_id = st.session_state.products[st.session_state.products['name'] == selected_product]['id'].values[0]
                    st.session_state.current_product = product_id
                    st.session_state.page = 'product_detail'
                    st.rerun()
            
            with col2:
                if st.button("Edit Product", type="secondary"):
                    st.info("Edit functionality would be implemented here")
                    # (For simplicity, full edit functionality not implemented in this example)
            
            with col3:
                if st.button("Delete Product", type="secondary"):
                    # Get the index of the product to delete
                    product_idx = st.session_state.products[st.session_state.products['name'] == selected_product].index
                    
                    # Remove the product
                    st.session_state.products = st.session_state.products.drop(product_idx).reset_index(drop=True)
                    
                    # Save to persistent storage
                    save_data(st.session_state.products)
                    
                    st.success(f"Product '{selected_product}' deleted successfully!")
                    st.rerun()
        else:
            st.warning("No products available. Add some products first.")

# Function to display homepage with all products
def show_homepage():
    # Header with logo
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://via.placeholder.com/150x80?text=Furn+Italia", width=150)
    with col2:
        st.markdown("<h1 class='main-header'>Furn Italia - Premium Furniture Collection</h1>", unsafe_allow_html=True)
    
    # Add a sidebar for filters
    st.sidebar.markdown("<h3>Filter Furniture</h3>", unsafe_allow_html=True)
    
    # Category filter
    categories = ["All"] + list(st.session_state.products['category'].unique())
    selected_category = st.sidebar.selectbox("Category", categories)
    
    # Price range filter
    min_price = int(st.session_state.products['discount_price'].min()) if not st.session_state.products.empty else 0
    max_price = int(st.session_state.products['discount_price'].max()) if not st.session_state.products.empty else 100000
    
    price_range = st.sidebar.slider(
        "Price Range (₹)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=1000
    )
    
    # Rating filter
    min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.5)
    
    # Search box
    search_query = st.sidebar.text_input("Search Products", "")
    
    # Apply filters
    filtered_products = st.session_state.products.copy()
    
    if selected_category != "All":
        filtered_products = filtered_products[filtered_products['category'] == selected_category]
    
    filtered_products = filtered_products[
        (filtered_products['discount_price'] >= price_range[0]) & 
        (filtered_products['discount_price'] <= price_range[1]) &
        (filtered_products['rating'] >= min_rating)
    ]
    
    # Apply search filter if provided
    if search_query:
        filtered_products = filtered_products[
            filtered_products['name'].str.contains(search_query, case=False) | 
            filtered_products['description'].str.contains(search_query, case=False)
        ]
    
    # Featured section
    if st.session_state.page == 'home' and not search_query and selected_category == "All":
        st.markdown("## 🌟 Featured Collection")
        featured_items = st.session_state.products.sample(min(3, len(st.session_state.products)))
        
        feat_cols = st.columns(min(3, len(featured_items)))
        for i, (_, product) in enumerate(featured_items.iterrows()):
            with feat_cols[i]:
                with st.container():
                    st.markdown(f"<div class='product-card'>", unsafe_allow_html=True)
                    
                    # Display first image
                    if product['images'] and len(product['images']) > 0:
                        try:
                            # If the image is a sample image without a file path
                            if product['images'][0].startswith('/'):
                                st.image("https://via.placeholder.com/400x300?text=Premium+Furniture", width=300)
                            else:
                                st.image(product['images'][0], width=300)
                        except:
                            st.image("https://via.placeholder.com/400x300?text=Image+Not+Available", width=300)
                    
                    st.subheader(product['name'])
                    st.markdown(f"<span class='category-badge'>{product['category']}</span>", unsafe_allow_html=True)
                    
                    # Display pricing information
                    discount = round(((product['price'] - product['discount_price']) / product['price']) * 100)
                    st.markdown(f"""
                    <div>
                        <span class='price-tag'>₹{product['discount_price']:,.2f}</span>
                        <br/>
                        <span class='original-price'>₹{product['price']:,.2f}</span> 
                        <span class='discount-tag'>{discount}% off</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Rating
                    st.markdown(f"⭐ {product['rating']} Rating")
                    
                    # View product button
                    if st.button(f"View Details", key=f"featured_{product['id']}"):
                        st.session_state.current_product = product['id']
                        st.session_state.page = 'product_detail'
                        st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
    
    # Display products in grid layout
    st.markdown(f"## Our Furniture Collection {f'({len(filtered_products)} items)' if not filtered_products.empty else ''}")
    
    if not filtered_products.empty:
        # Create rows with 3 products per row
        for i in range(0, len(filtered_products), 3):
            cols = st.columns(3)
            
            for j in range(3):
                if i + j < len(filtered_products):
                    product = filtered_products.iloc[i + j]
                    
                    with cols[j]:
                        with st.container():
                            st.markdown(f"<div class='product-card'>", unsafe_allow_html=True)
                            
                            # Display first image
                            if product['images'] and len(product['images']) > 0:
                                try:
                                    # If the image is a sample image without a file path
                                    if product['images'][0].startswith('/'):
                                        st.image("https://via.placeholder.com/400x300?text=Premium+Furniture", width=300)
                                    else:
                                        st.image(product['images'][0], width=300)
                                except:
                                    st.image("https://via.placeholder.com/400x300?text=Image+Not+Available", width=300)
                            
                            st.subheader(product['name'])
                            st.markdown(f"<span class='category-badge'>{product['category']}</span>", unsafe_allow_html=True)
                            
                            # Display pricing information
                            col1, col2 = st.columns([3, 2])
                            with col1:
                                st.markdown(f"<span class='price-tag'>₹{product['discount_price']:,.2f}</span>", unsafe_allow_html=True)
                            with col2:
                                discount = round(((product['price'] - product['discount_price']) / product['price']) * 100)
                                st.markdown(f"<span class='original-price'>₹{product['price']:,.2f}</span> <span class='discount-tag'>{discount}% off</span>", unsafe_allow_html=True)
                            
                            # Rating
                            st.markdown(f"⭐ {product['rating']} Rating")
                            
                            # View product button
                            if st.button(f"View Details", key=f"view_{product['id']}"):
                                st.session_state.current_product = product['id']
                                st.session_state.page = 'product_detail'
                                st.rerun()
                            
                            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No furniture items match your filter criteria.")
        
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
    st.markdown(f"<span class='category-badge'>{product['category']}</span>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Main image display
        if product['images'] and len(product['images']) > 0:
            # If the image is a sample image without a file path
            if product['images'][0].startswith('/'):
                main_image = "https://via.placeholder.com/800x600?text=Premium+Furniture"
            else:
                main_image = product['images'][0]
            st.image(main_image, width=500)
        
        # Thumbnail gallery
        if product['images'] and len(product['images']) > 1:
            st.write("More Images:")
            image_cols = st.columns(min(4, len(product['images'])))
            
            for i, img_path in enumerate(product['images'][:4]):  # Limit to 4 thumbnails
                with image_cols[i]:
                    # If the image is a sample image without a file path
                    if img_path.startswith('/'):
                        thumbnail = "https://via.placeholder.com/150x150?text=Gallery"
                    else:
                        thumbnail = img_path
                    st.image(thumbnail, width=120)
                    
    with col2:
        # Price information
        discount = round(((product['price'] - product['discount_price']) / product['price']) * 100)
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="margin:0; color: #4E3524;">₹{product['discount_price']:,.2f}</h2>
            <p>
                <span class='original-price'>₹{product['price']:,.2f}</span> 
                <span class='discount-tag'>{discount}% off</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Rating
        st.markdown(f"### ⭐ {product['rating']} Customer Rating")
        
        # Stock information
        if product['stock'] > 0:
            st.markdown(f"<div style='color:green; font-weight:500;'>✓ In Stock ({product['stock']} available)</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:red;'>✗ Out of Stock</div>", unsafe_allow_html=True)
        
        # Delivery options
        st.markdown("""
        <div style="margin: 15px 0;">
            <p>🚚 Fast Delivery Available</p>
            <p>🛠️ Professional Assembly Available</p>
            <p>↩️ 7-Day Return Policy</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Buy buttons
        col_buy1, col_buy2 = st.columns(2)
        with col_buy1:
            st.button("Add to Cart", type="primary", use_container_width=True)
        with col_buy2:
            st.button("Buy Now", type="secondary", use_container_width=True)
            
        # Check availability
        st.markdown("### Check Availability")
        pincode = st.text_input("Enter Pincode")
        if pincode and st.button("Check"):
            st.success(f"Delivery available to {pincode}. Estimated delivery in 3-5 days.")
    
    # Horizontal line
    st.markdown("---")
    
    # Description and Specifications tabs
    tab1, tab2, tab3 = st.tabs(["Product Description", "Specifications", "Reviews"])
    
    with tab1:
        st.markdown("### Product Description")
        st.markdown(product['description'])
        
        # Add some nicely formatted product highlights
        st.markdown("### Product Highlights")
        highlights = [
            "Premium quality materials for durability",
            "Ergonomic design for maximum comfort",
            "Elegant aesthetics to enhance your space",
            "Made with sustainable practices"
        ]
        for highlight in highlights:
            st.markdown(f"✓ {highlight}")
    
    with tab2:
        st.markdown("### Product Specifications")
        if isinstance(product['specifications'], dict) and product['specifications']:
            # Display specifications in a nicely formatted table
            st.markdown("<table class='spec-table'>", unsafe_allow_html=True)
            for key, value in product['specifications'].items():
                st.markdown(f"<tr><td><strong>{key}</strong></td><td>{value}</td></tr>", unsafe_allow_html=True)
            st.markdown("</table>", unsafe_allow_html=True)
        else:
            st.info("No specifications available for this product.")
    
    with tab3:
        st.markdown("### Customer Reviews")
        # Simulated reviews for demonstration
        reviews = [
            {"name": "Rahul M.", "rating": 5, "comment": "Excellent quality furniture. Exactly as described and the delivery was prompt."},
            {"name": "Priya S.", "rating": 4, "comment": "Beautiful piece, but took slightly longer to deliver than expected."},
            {"name": "Amit K.", "rating": 5, "comment": "The craftsmanship is outstanding. Will definitely buy from Furn Italia again!"}
        ]
        
        for review in reviews:
            st.markdown(f"""
            <div style="border: 1px solid #e0e0e0; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <p>{'⭐' * review['rating']}</p>
                <p><em>"{review['comment']}"</em></p>
                <p style="text-align: right; color: #666;">— {review['name']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Similar products section
    st.markdown("### You May Also Like")
    
    # Find products in the same category
    same_category = st.session_state.products[
        (st.session_state.products['category'] == product['category']) & 
        (st.session_state.products['id'] != product_id)
    ].head(3)  # Limit to 3 similar products
    
    if not same_category.empty:
        similar_cols = st.columns(min(3, len(same_category)))
        
        for i, (_, similar_product) in enumerate(same_category.iterrows()):
            with similar_cols[i]:
                with st.container():
                    st.markdown(f"<div class='product-card'>", unsafe_allow_html=True)
                    
                    # Display first image
                    if similar_product['images'] and len(similar_product['images']) > 0:
                        try:
                            # If the image is a sample image without a file path
                            if similar_product['images'][0].startswith('/'):
                                st.image("https://via.placeholder.com/300x225?text=Related+Item", width=200)
                            else:
                                st.image(similar_product['images'][0], width=200)
                        except:
                            st.image("https://via.placeholder.com/300x225?text=Image+Not+Available", width=200)
                    
                    st.subheader(similar_product['name'])
                    st.markdown(f"<span class='price-tag'>₹{similar_product['discount_price']:,.2f}</span>", unsafe_allow_html=True)
                    
                    # View product button
                    if st.button(f"View Details", key=f"similar_{similar_product['id']}"):
                        st.session_state.current_product = similar_product['id']
                        st.session_state.page = 'product_detail'
                        st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No similar products found.")

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
            
        if st.button("🛋️ All Collections", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()
            
        # Admin panel button with check for login status
        if st.session_state.admin_logged_in:
            if st.button("🛠️ Admin Panel", use_container_width=True):
                st.session_state.page = 'admin'
                st.rerun()
        else:
            if st.button("🔒 Admin Login", use_container_width=True):
                st.session_state.page = 'admin'
                st.rerun()
        
        st.markdown("---")
        
        # Quick category navigation
        st.markdown("<h3>Categories</h3>", unsafe_allow_html=True)
        categories = list(st.session_state.products['category'].unique())
        
        for category in categories:
            if st.button(f"📁 {category}", key=f"cat_{category}", use_container_width=True):
                # Set filter in session state and redirect to home
                st.session_state.category_filter = category
                st.session_state.page = 'home'
                st.rerun()
                
        st.markdown("---")
        
        # Customer support information
        st.markdown("""
        <h3>Customer Support</h3>
        <p>📞 Call us: +91 98765 43210</p>
        <p>📧 Email: support@furnitalia.com</p>
        <p>⏰ Mon-Sat: 10AM - 7PM</p>
        """, unsafe_allow_html=True)
    
    # Display the appropriate page based on the current state
    if st.session_state.page == 'home':
        show_homepage()
    elif st.session_state.page == 'admin':
        show_product_management()
    elif st.session_state.page == 'product_detail':
        show_product_detail()

if __name__ == "__main__":
    main()
            
