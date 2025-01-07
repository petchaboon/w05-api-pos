import streamlit as st
import pandas as pd
from PIL import Image
import requests
import time

# Page config
st.set_page_config(page_title="Point of Sale System", layout="wide")

from streamlit_extras.image_in_tables import table_with_images
url = "https://676a35aa863eaa5ac0ddaa64.mockapi.io/products"

def con_api(url):
    try:
        # ดึงข้อมูลจาก API และแปลงเป็น DataFrame
        data = requests.get(url).json()
        if not isinstance(data, list):
            st.error("รูปแบบข้อมูลไม่ถูกต้อง")
            return pd.DataFrame()  # ส่งคืน DataFrame ว่าง
        data_df = pd.json_normalize(data)  # ทำ JSON ให้เป็นแบบแบน
        
        # ตรวจสอบว่ามีคอลัมน์ 'id' หรือไม่
        if 'id' not in data_df.columns:
            st.warning("ข้อมูลจาก API ไม่มีคอลัมน์ 'id' กำลังสร้าง ID เอง")
            data_df['id'] = range(1, len(data_df) + 1)
        # st.table(data_df)
        return data_df
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ API: {e}")
        return pd.DataFrame()  # ส่งคืน DataFrame ว่าง

# Initialize session state for cart
if 'cart' not in st.session_state:
    st.session_state.cart = {}

products = con_api(url)

df_html = table_with_images(products, url_columns=('image',))
st.markdown(df_html, unsafe_allow_html=True)

def add_to_cart(product_id):
    product = products.loc[products['id'] == product_id].iloc[0]  # ค้นหาสินค้าจาก ID
    if product_id in st.session_state.cart:
        st.session_state.cart[product_id]['quantity'] += 1
    else:
        st.session_state.cart[product_id] = {
            'name': product['name'],
            'price': product['price'],
            'quantity': 1,
            'image': product.get('image', "https://via.placeholder.com/150")  # ใช้ภาพเริ่มต้นหากไม่มี
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
    if products.empty:
        st.error("ไม่พบข้อมูลสินค้า")
    else:
        # สร้างกริดของสินค้า
        num_col = 4
        for i, product in products.iterrows():
            # ตรวจสอบว่ามี 'id' หรือไม่
            if 'id' not in product:
                st.warning(f"สินค้าที่ตำแหน่ง {i} ไม่มี 'id' และจะไม่ถูกแสดง")
                continue
            
            if i % num_col == 0:
                cols = st.columns(num_col)
            with cols[i % num_col]:
                st.image(product.get('image', "https://via.placeholder.com/150"), 
                         use_container_width=True, 
                         caption=product['name'])
                st.write(f"**{product['price']:.2f} บาท**")
                st.write(f"หมวด: {product['category']}")
                if st.button(f"ใส่ตะกร้า", key=f"add_{product['id']}", type="primary"):
                    add_to_cart(product['id'])
                    st.rerun()

with col2:
    st.header("ตะกร้าสินค้า")
    if not st.session_state.cart:
        st.write("ไม่พบสินค้าในตะกร้า")
    else:
        for product_id, item in st.session_state.cart.items():
            cart_item = st.container()
            with cart_item:
                img_col, name_col, qty_col, tot_col = st.columns([1, 2, 1, 1])
                with img_col:
                    st.image(item['image'], width=80)
                with name_col:
                    st.write(f"**{item['name']}**")
                with qty_col:
                    st.write(f"{item['price']:.2f} x {item['quantity']}")
                with tot_col:
                    st.write(f"**{item['price'] * item['quantity']:.2f} บาท**")

                ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 1])
                with ctrl_col1:
                    if st.button("ลบ", key=f"minus_{product_id}", type="primary"):
                        update_quantity(product_id, -1)
                        st.rerun()
                with ctrl_col2:
                    st.write(f"จำนวน: {item['quantity']}")
                with ctrl_col3:
                    if st.button("เพิ่ม", key=f"plus_{product_id}", type="primary"):
                        update_quantity(product_id, 1)
                        st.rerun()

        st.subheader(f"รวมเงิน: {calculate_total():.2f} บาท")
        if st.button("สั่งซื้อสินค้า", type="primary"):
            st.toast("**เราได้รับรายการสั่งซื้อของท่านเรียบร้อยแล้ว** \nและจะดำเนินการจัดส่งต่อไป")
            st.session_state.cart = {}
            time.sleep(3)  # รอแจ้งเตือนก่อนรีโหลด
            st.rerun()

# Add custom CSS for better styling
st.markdown("""
    <style>
        .stButton button {
            width: 100%;
        }
        div[data-testid="stHorizontalBlock"] {
            background-color: #e3f7ab;
            padding: 15px;
            border-radius: 5px;
            margin: 5px 0;
        }
        img {
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)
