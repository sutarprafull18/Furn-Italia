import streamlit as st
import pandas as pd
import os
import uuid
from PIL import Image
import io
import base64

# Set page configuration
st.set_page_config(
    page_title="Furn Italia",
    page_icon="🛒",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'products' not in st.session_state:
    # Create a default dataframe with sample product
    st.session_state.products = pd.DataFrame({
        'id': ['1'],
        'name': ['Sample Smartphone'],
        'price': [499.99],
        'discount_price': [399.99],
        'category': ['Electronics'],
        'rating': [4.5],
        'description': ['A high-performance smartphone with excellent camera and battery life.'],
        'specifications': [{'Display': '6.5 inch AMOLED', 'Processor': 'Octa-core', 'RAM': '8GB', 'Storage': '128GB'}],
        'images': [['/sample_phone.jpg']],
        'stock': [10]
    })

if 'current_product' not in st.session_state:
    st.session_state.current_product = None

if 'page' not in st.session_state:
    st.session_state.page = 'home'

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

# Function to display product management page
def show_product_management():
    st.title("Product Management")
    
    tab1, tab2 = st.tabs(["Add New Product", "View/Edit Products"])
    
    with tab1:
        st.header("Add New Product")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Product Name")
            price = st.number_input("Regular Price", min_value=0.0, format="%.2f")
            discount_price = st.number_input("Discounted Price", min_value=0.0, format="%.2f")
            category = st.selectbox("Category", ["Electronics", "Fashion", "Home & Kitchen", "Books", "Toys", "Beauty", "Sports", "Other"])
            rating = st.slider("Rating", 0.0, 5.0, 4.0, 0.1)
            stock = st.number_input("Stock Available", min_value=0, value=1)
            
        with col2:
            description = st.text_area("Product Description")
            
            # Specifications as key-value pairs
            st.subheader("Specifications")
            spec_cols = st.columns(2)
            
            specs = {}
            spec_keys = []
            spec_values = []
            
            # Add default specification fields
            for i in range(4):
                with spec_cols[0]:
                    key = st.text_input(f"Spec Key {i+1}", key=f"spec_key_{i}")
                    spec_keys.append(key)
                
                with spec_cols[1]:
                    value = st.text_input(f"Spec Value {i+1}", key=f"spec_value_{i}")
                    spec_values.append(value)
            
            # Create specifications dictionary
            for k, v in zip(spec_keys, spec_values):
                if k and v:  # Only add non-empty specs
                    specs[k] = v
            
            # Upload multiple images
            st.subheader("Product Images")
            uploaded_files = st.file_uploader("Upload product images", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
            
            image_paths = []
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    image_path = save_image(uploaded_file)
                    if image_path:
                        image_paths.append(image_path)
                        st.image(uploaded_file, width=100, caption=uploaded_file.name)
        
        if st.button("Add Product"):
            if name and price and description and image_paths:
                # Generate a unique ID for the product
                product_id = str(len(st.session_state.products) + 1)
                
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
                    'images': image_paths,
                    'stock': stock
                }
                
                # Add the new product to the dataframe
                st.session_state.products = pd.concat([
                    st.session_state.products, 
                    pd.DataFrame([new_product])
                ], ignore_index=True)
                
                st.success("Product added successfully!")
                st.balloons()
            else:
                st.error("Please fill in all required fields (name, price, description, and at least one image).")
    
    with tab2:
        st.header("View/Edit Products")
        
        # Display products in a dataframe with minimal columns for overview
        if not st.session_state.products.empty:
            # Create a display version of the dataframe with fewer columns
            display_df = st.session_state.products[['id', 'name', 'price', 'category', 'stock']].copy()
            display_df['View'] = ['View' for _ in range(len(display_df))]
            display_df['Edit'] = ['Edit' for _ in range(len(display_df))]
            display_df['Delete'] = ['Delete' for _ in range(len(display_df))]
            
            # Display the dataframe
            st.dataframe(display_df)
            
            # Product selection for actions
            product_names = st.session_state.products['name'].tolist()
            selected_product = st.selectbox("Select a product for actions:", product_names)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("View Product"):
                    product_id = st.session_state.products[st.session_state.products['name'] == selected_product]['id'].values[0]
                    st.session_state.current_product = product_id
                    st.session_state.page = 'product_detail'
                    st.rerun()
            
            with col2:
                if st.button("Edit Product"):
                    # TODO: Implement edit functionality
                    st.info("Edit functionality would be implemented here")
            
            with col3:
                if st.button("Delete Product"):
                    # Get the index of the product to delete
                    product_idx = st.session_state.products[st.session_state.products['name'] == selected_product].index
                    
                    # Remove the product
                    st.session_state.products = st.session_state.products.drop(product_idx).reset_index(drop=True)
                    st.success(f"Product '{selected_product}' deleted successfully!")
                    st.rerun()
        else:
            st.warning("No products available. Add some products first.")

# Function to display homepage with all products
def show_homepage():
    st.title("🛒 E-commerce Product Listings")
    
    # Add a sidebar for filters
    st.sidebar.title("Filters")
    
    # Category filter
    categories = ["All"] + list(st.session_state.products['category'].unique())
    selected_category = st.sidebar.selectbox("Category", categories)
    
    # Price range filter
    price_range = st.sidebar.slider(
        "Price Range",
        min_value=float(st.session_state.products['discount_price'].min() if not st.session_state.products.empty else 0),
        max_value=float(st.session_state.products['discount_price'].max() if not st.session_state.products.empty else 1000),
        value=(float(st.session_state.products['discount_price'].min() if not st.session_state.products.empty else 0), 
               float(st.session_state.products['discount_price'].max() if not st.session_state.products.empty else 1000))
    )
    
    # Rating filter
    min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.5)
    
    # Apply filters
    filtered_products = st.session_state.products.copy()
    
    if selected_category != "All":
        filtered_products = filtered_products[filtered_products['category'] == selected_category]
    
    filtered_products = filtered_products[
        (filtered_products['discount_price'] >= price_range[0]) & 
        (filtered_products['discount_price'] <= price_range[1]) &
        (filtered_products['rating'] >= min_rating)
    ]
    
    # Display products in grid layout
    if not filtered_products.empty:
        # Create rows with 3 products per row
        for i in range(0, len(filtered_products), 3):
            cols = st.columns(3)
            
            for j in range(3):
                if i + j < len(filtered_products):
                    product = filtered_products.iloc[i + j]
                    
                    with cols[j]:
                        st.subheader(product['name'])
                        
                        # Display first image
                        if product['images'] and len(product['images']) > 0:
                            try:
                                # If the image is a sample image without a file path
                                if product['images'][0].startswith('/'):
                                    st.image("https://via.placeholder.com/300x300?text=Sample+Product", width=200)
                                else:
                                    st.image(product['images'][0], width=200)
                            except:
                                st.image("https://via.placeholder.com/300x300?text=Image+Not+Available", width=200)
                        
                        # Display pricing information
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"<h3 style='margin:0;'>₹{product['discount_price']}</h3>", unsafe_allow_html=True)
                        with col2:
                            discount = round(((product['price'] - product['discount_price']) / product['price']) * 100)
                            st.markdown(f"<span style='text-decoration:line-through;color:gray;'>₹{product['price']}</span> <span style='color:green;'>{discount}% off</span>", unsafe_allow_html=True)
                        
                        # Rating
                        st.markdown(f"⭐ {product['rating']}")
                        
                        # View product button
                        if st.button(f"View Details", key=f"view_{product['id']}"):
                            st.session_state.current_product = product['id']
                            st.session_state.page = 'product_detail'
                            st.rerun()
    else:
        st.warning("No products match your filter criteria.")

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
    st.title(product['name'])
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Main image display
        if product['images'] and len(product['images']) > 0:
            # If the image is a sample image without a file path
            if product['images'][0].startswith('/'):
                main_image = "https://via.placeholder.com/500x500?text=Sample+Product"
            else:
                main_image = product['images'][0]
            st.image(main_image, width=400)
        
        # Thumbnail gallery
        if product['images'] and len(product['images']) > 1:
            st.write("More Images:")
            image_cols = st.columns(min(4, len(product['images'])))
            
            for i, img_path in enumerate(product['images'][:4]):  # Limit to 4 thumbnails
                with image_cols[i]:
                    # If the image is a sample image without a file path
                    if img_path.startswith('/'):
                        thumbnail = "https://via.placeholder.com/100x100?text=Sample"
                    else:
                        thumbnail = img_path
                    st.image(thumbnail, width=100)
                    
    with col2:
        # Price information
        price_col1, price_col2 = st.columns(2)
        with price_col1:
            st.markdown(f"<h2 style='margin:0;'>₹{product['discount_price']}</h2>", unsafe_allow_html=True)
        with price_col2:
            discount = round(((product['price'] - product['discount_price']) / product['price']) * 100)
            st.markdown(f"<span style='text-decoration:line-through;color:gray;'>₹{product['price']}</span> <span style='color:green;font-weight:bold;'>{discount}% off</span>", unsafe_allow_html=True)
        
        # Rating
        st.markdown(f"⭐ {product['rating']} Rating")
        
        # Stock information
        if product['stock'] > 0:
            st.markdown(f"<span style='color:green;'>In Stock ({product['stock']} available)</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:red;'>Out of Stock</span>", unsafe_allow_html=True)
        
        # Buy buttons
        col_buy1, col_buy2 = st.columns(2)
        with col_buy1:
            st.button("Add to Cart", type="primary")
        with col_buy2:
            st.button("Buy Now", type="secondary")
    
    # Description and Specifications tabs
    tab1, tab2 = st.tabs(["Description", "Specifications"])
    
    with tab1:
        st.markdown("## Description")
        st.write(product['description'])
    
    with tab2:
        st.markdown("## Specifications")
        if isinstance(product['specifications'], dict) and product['specifications']:
            for key, value in product['specifications'].items():
                if key and value:  # Only display non-empty specifications
                    st.markdown(f"**{key}:** {value}")
        else:
            st.info("No specifications available for this product.")
    
    # Similar products section
    st.markdown("## Similar Products")
    
    # Find products in the same category
    same_category = st.session_state.products[
        (st.session_state.products['category'] == product['category']) & 
        (st.session_state.products['id'] != product_id)
  ].head(3)  # Limit to 3 similar products
    
    if not same_category.empty:
        similar_cols = st.columns(min(3, len(same_category)))
        
        for i, (_, similar_product) in enumerate(same_category.iterrows()):
            with similar_cols[i]:
                st.subheader(similar_product['name'])
                
                # Display first image
                if similar_product['images'] and len(similar_product['images']) > 0:
                    try:
                        # If the image is a sample image without a file path
                        if similar_product['images'][0].startswith('/'):
                            st.image("https://via.placeholder.com/150x150?text=Sample+Product", width=150)
                        else:
                            st.image(similar_product['images'][0], width=150)
                    except:
                        st.image("https://via.placeholder.com/150x150?text=Image+Not+Available", width=150)
                
                st.markdown(f"₹{similar_product['discount_price']}")
                
                # View product button
                if st.button(f"View Details", key=f"similar_{similar_product['id']}"):
                    st.session_state.current_product = similar_product['id']
                    st.session_state.page = 'product_detail'
                    st.rerun()
    else:
        st.info("No similar products found.")

# Main navigation
def main():
    # Add admin button in sidebar
    with st.sidebar:
        st.title("Navigation")
        
        if st.button("🏠 Home"):
            st.session_state.page = 'home'
            st.session_state.current_product = None
            st.rerun()
            
        if st.button("🛠️ Admin Panel"):
            st.session_state.page = 'admin'
            st.rerun()
            
        # Add a search box in the sidebar
        st.write("---")
        st.subheader("Search Products")
        search_term = st.text_input("Search by name:", key="search_box")
        
        if search_term:
            # Simple search functionality
            search_results = st.session_state.products[
                st.session_state.products['name'].str.contains(search_term, case=False) |
                st.session_state.products['description'].str.contains(search_term, case=False)
            ]
            
            if not search_results.empty:
                st.write(f"Found {len(search_results)} results:")
                for _, result in search_results.iterrows():
                    if st.button(f"{result['name']}", key=f"search_{result['id']}"):
                        st.session_state.current_product = result['id']
                        st.session_state.page = 'product_detail'
                        st.rerun()
            else:
                st.write("No results found.")
    
    # Display the appropriate page based on the current state
    if st.session_state.page == 'home':
        show_homepage()
    elif st.session_state.page == 'admin':
        show_product_management()
    elif st.session_state.page == 'product_detail':
        show_product_detail()

if __name__ == "__main__":
    main()
