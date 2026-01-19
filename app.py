import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ==========================================
# 👇 તમારો ડેટા અહીં ભરો (FILL THIS) 👇
# ==========================================

# 1. તમારી ગૂગલ શીટની લિંક અહીં મૂકો:
SHEET_URL = "
https://docs.google.com/spreadsheets/d/1zncebeUrh1Sfu1z0U1jdyErRboXiDZ3xeSt9NclbuYg/edit?usp=sharing"

# 2. તમારી JSON ફાઈલ ખોલો, બધું કોપી કરો અને નીચે બે લાલ લીટીની વચ્ચે પેસ્ટ કરો:
# (આપેલા ત્રણ અવતરણ ચિહ્નો """ કાઢતા નહીં)

JSON_DATA = """{
  "type": "service_account",
  "project_id": "cool-beanbag-484808-f8",
  "private_key_id": "55038a369d1c650dc1c89f878f47ab8d89de76ce",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCsrpD3xZhHCROv\nCo7IGIh1cNwY/D8CyTb1j4Jlqy8luTpBTR7SlOvbyRDM3tVlhdCL0UzlLF6WkdyM\nsS8N58octJeqhhUYFK4eUc8pkD/iwX0EHq+3AXlmwILg9mH+1vWyntkTtXAYUAsq\npg1AoMbxzYVTbfgJ9CWqlRO7Qr8AixD/m8TzPqxkZ7LGYnc4WfYYpj2eS/8hoArB\nQMXca9jZgPLTtf4xLRveC3XeP1zxa1RyETtHo8A13Fm+j5jTr6OlrYUilc4ED8Xk\n6qTIZ47NJu/h5TUvy4UkHpjz+gHBuxndAPYAbAMe50SctZsqP4IvQeCC8PjC8H2a\nzeFToNQlAgMBAAECggEAEi3oliUnxGa4u0dVw8wNZavFiB3aNl1fm1eJ51Evy/1l\nnCVV1t6VvBQ9YAwflCoTy/xzZ3cV2C0v9mHa7dBWr1H12551Dw1yTT/YmuwURbeQ\nBUSDxDT0BnTC8pMNuwn/YNgnS1NhIzYeDtXfdEvY1fEIlcFwiP+6jWxXYPIEcLaG\n2JDMPTKRArAAeRQ7W7xPSq9RIElzYxRSZMy+Z68vj3/t/x4BuqzO0QukHX3YP2Ce\n4Icm/Q4yBtiOnAijUdC7lwzdDdRwwyA9/PgV/k8uPuRCsVu9BJK85a5b+wtjYXH4\n01cXYFldCPny9IkffcpEOl0M5WTRLBdskWnEbXpBAQKBgQDls3//pymKbSou/8j2\nFkBQm/YelaGLvmgJCToVy1iBtCXRq0JqjjH1sfUA+p5eBthBFShkNMtfsiNm1Xhv\nNZtE5edNtqCTwAqY1hQ+wWEVkeo7WhEz1FXgz740qJCc4ae6C9qlVrX+pZnEpWBq\n91fxgjQbJgnOi4qi22e5w4QfgQKBgQDAc9d4HupcyPPR6gIHc45bQqvveyXVhuL7\ny9WqZHa2+qGEJm3eTU5kfnqhvj96KwK/6QN/tEdL+dJiqjCVl58bIodW8/tda152\nf21gbbkcASs+m/WukP3HMSL6eiYzg7Ecy5sOIy5Zuf6QN+Qcxy6B8NntRT2+teae\nVGDWBHuGpQKBgFFu25gE6UM8BFJ5OAOWS+LIB+872POz4yog7UjAuHXzKd01O+yO\n0MNr/ZIFR5PKFWytVY6A8QDSJJ7WW0YB2TQJ1YDFmBQJZzhb3P2KjSKaglHcUnDv\nfCqhO6trfyk/Drl0bmVjYk4O437FqnMBkVn7cQGW8K8a5WFrK1C+Md8BAoGBAJkv\nW9G0Ie3K0jBC6GyP8T742axcRGgq3p93xtHC96973XY3tHoe5IgfGHOH4DTY6W5i\nBbPvhlSWPHzmZJedwTozCLEQsQLSBLWjhiccDxyYXZiPQUY7CJU1qlbfRWr5ps95\nzSi6nhkzb8nRgxPZA07QrFYtKBGV7kQWe6G+nag1AoGBAMM9qYynr5i5nBA7/ns+\nysNMFxuCQERNizkp+Gm/rUIjqwuYKCok4p52yr60fqj+X1vxLhbM/q+qinNSNnTa\nlyi2RR/SiIaaZ2gR1K+CEomlgMnhX3If4l1Nz2e5RoR4vCqPadxa/VmTjFmO7iHk\nx3xPeY3WXK3csWDmTKmP/Srw\n-----END PRIVATE KEY-----\n",
  "client_email": "tatva-bot@cool-beanbag-484808-f8.iam.gserviceaccount.com",
  "client_id": "111819596221554520240",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/tatva-bot%40cool-beanbag-484808-f8.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}



"""

# ==========================================
# 👆 બસ અહીં સુધી જ ફેરફાર કરવાનો છે 👆
# ==========================================

st.set_page_config(page_title="Tatva OS", page_icon="🟠", layout="wide")

# --- CONNECTION SETUP ---
def get_db_connection():
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        # Convert string back to JSON securely
        info = json.loads(JSON_DATA)
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_url(SHEET_URL).sheet1
    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")
        st.stop()

try:
    sheet = get_db_connection()
except:
    st.warning("તમારી JSON Key બરાબર પેસ્ટ નથી થઈ. ફરીથી ચેક કરો.")
    st.stop()

# --- DATABASE FUNCTIONS ---
def load_db():
    try:
        val = sheet.cell(1, 1).value
        if val:
            return json.loads(val)
    except:
        pass
    return {"orders": [], "team": ["Self"]}

def save_db(data):
    try:
        sheet.update_cell(1, 1, json.dumps(data))
    except Exception as e:
        st.error(f"Save Error: {e}")

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR MENU ---
st.sidebar.title("🟠 Tatva Cloud")
if st.sidebar.button("🔄 Refresh"):
    st.session_state.db = load_db()
    st.rerun()

menu = st.sidebar.radio("Menu", ["Dashboard", "New Order", "Order Details", "Manage Team"])

# --- DASHBOARD ---
if menu == "Dashboard":
    st.title("📊 Cloud Dashboard")
    orders = st.session_state.db["orders"]
    
    rev = sum(int(o["price"]) for o in orders)
    exp = 0
    recd = 0
    paid_out = 0
    
    for o in orders:
        recd += sum(int(p["amt"]) for p in o.get("income", []))
        for t in o.get("tasks", []):
            exp += int(t["cost"])
            paid_out += sum(int(p["amt"]) for p in t.get("payouts", []))
            
    net = rev - exp
    hand = recd - paid_out
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Orders", len(orders))
    c2.metric("Profit", f"₹{net}")
    c3.metric("Revenue", f"₹{rev}")
    c4.metric("Cash Hand", f"₹{hand}")
    
    st.divider()
    for o in reversed(orders[-10:]):
        c_recd = sum(int(p["amt"]) for p in o.get("income", []))
        status = "✅ Done" if (int(o["price"]) - c_recd) <= 0 else "⏳ Pending"
        st.success(f"**{o['client']}** | ₹{o['price']} | {status}")

# --- NEW ORDER ---
elif menu == "New Order":
    st.title("➕ New Order")
    with st.form("new_order", clear_on_submit=True):
        c1, c2 = st.columns(2)
        client = c1.text_input("Client Name")
        work = c2.text_input("Work")
        price = c1.number_input("Price", min_value=0)
        date = c2.date_input("Date", datetime.now())
        
        if st.form_submit_button("Save Order"):
            if client and price:
                new_o = {
                    "id": int(datetime.now().timestamp()),
                    "client": client, "work": work, "price": int(price),
                    "date": date.strftime("%d/%m/%Y"),
                    "income": [], "tasks": []
                }
                st.session_state.db["orders"].append(new_o)
                save_db(st.session_state.db)
                st.success("Saved to Google Sheet!")
                st.rerun()

# --- ORDER DETAILS ---
elif menu == "Order Details":
    st.title("📦 Manager")
    opts = {f"{o['client']} - {o['work']}": o['id'] for o in st.session_state.db["orders"]}
    sel = st.selectbox("Select Order", list(opts.keys()))
    
    if sel:
        oid = opts[sel]
        order = next(o for o in st.session_state.db["orders"] if o["id"] == oid)
        
        # Simple Income / Expense logic similar to before...
        # (Keeping it short for simplicity)
        st.info(f"Selected: {order['client']}")
        
        t1, t2 = st.tabs(["Income", "Expense"])
        with t1:
            amt = st.number_input("Add Payment", min_value=1, key="pay")
            if st.button("Add Recd"):
                order["income"].append({"amt": int(amt)})
                save_db(st.session_state.db)
                st.rerun()
            st.write(order.get("income", []))

        with t2:
            st.write(order.get("tasks", []))
            if st.button("Delete Order"):
                st.session_state.db["orders"].remove(order)
                save_db(st.session_state.db)
                st.rerun()

elif menu == "Manage Team":
    st.write("Team Management")