import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

# Page config
st.set_page_config(page_title="Point of Sale System", layout="wide")

# Initialize session state for cart
if 'cart' not in st.session_state:
    st.session_state.cart = {}

# Load product data from CSV
products_df = pd.read_csv("products.csv")
products = products_df.to_dict(orient="index")
# st.write(products)
def load_image(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None

def add_to_cart(product_id):
    if product_id in st.session_state.cart:
        st.session_state.cart[product_id]['quantity'] += 1
    else:
        st.session_state.cart[product_id] = {
            'name': products[product_id]['name'],
            'price': products[product_id]['price'],
            'quantity': 1,
            'image': products[product_id]['image']  # Store image URL in cart
        }

def update_quantity(product_id, delta):
    current_quantity = st.session_state.cart[product_id]['quantity']
    new_quantity = current_quantity + delta
    if new_quantity > 0:
        st.session_state.cart[product_id]['quantity'] = new_quantity
    elif new_quantity <= 0:
        del st.session_state.cart[product_id]

def calculate_total():
    return sum(item['price'] * item['quantity'] for item in st.session_state.cart.values())

# Main UI
st.title("ระบบงานขายหน้าร้าน")

# Create two columns: products and cart
col1, col2 = st.columns([2, 1])

with col1:
    st.header("รายการสินค้า")

    # Create a grid of products using columns
    num_col = 4
    for i, product_id in enumerate(products.keys()):  # Loop through keys
        if i % num_col == 0:  # Start a new row every 'num_col' products
            cols = st.columns(num_col)
        product = products[product_id]
        with cols[i % num_col]:  # Use the remainder for column index
            # Product image
            st.image(load_image(product['image']),
                    use_column_width=True,
                    caption=product['name'])
            # Product details
            st.write(f"**{product['price']:.2f} บาท**")
            st.write(f"หมวด: {product['category']}")
            if st.button(f"ใส่ตะกร้า", key=f"add_{product_id}"):
                add_to_cart(product_id)
                st.rerun()

with col2:
    st.header("ตะกร้าสินค้า")
    
    if not st.session_state.cart:
        st.write("ไม่พบสินค้าในตะกร้า")
    else:
        for product_id, item in st.session_state.cart.items():
            # st.write("---")
            
            # Create a container for each cart item
            cart_item = st.container()
            
            with cart_item:
                # Display product image and details side by side
                img_col, name_col , qty_col, tot_col = st.columns([1,2,1,1])
                
                with img_col:
                    # Display smaller image in cart
                    st.image(load_image(item['image']), 
                            width=80,
                            output_format="PNG")
                
                with name_col:
                    st.write(f"**{item['name']}**")
                with qty_col:
                    st.write(f"{item['price']:.2f} x {item['quantity']}")
                with tot_col:
                    st.write(f"เป็นเงิน: **{item['price'] * item['quantity']:.2f} บาท**")
                
                # Quantity controls
                ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1,1,1])
                with ctrl_col1:
                    if st.button("ลบ", key=f"minus_{product_id}"):
                        update_quantity(product_id, -1)
                        st.rerun()
                with ctrl_col2:
                    st.write(f"จำนวน: {item['quantity']}")
                with ctrl_col3:
                    if st.button("เพิ่ม", key=f"plus_{product_id}"):
                        update_quantity(product_id, 1)
                        st.rerun()

        # st.write("---")
        st.subheader(f"รวมเงิน: {calculate_total():.2f} บาท")
        
        if st.button("สั่งซื้อสินค้า", type="primary"):
            st.session_state.cart = {}
            st.success("Sale completed!")
            st.rerun()

# Add some custom CSS to improve the appearance
st.markdown("""
    <style>
        .stButton button {
            width: 100%;
        }
        div[data-testid="stHorizontalBlock"] {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
        }
        img {
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)