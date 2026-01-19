import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

# ==========================================
# 👇 તમારો ડેટા 👇
# ==========================================

SHEET_URL = "https://docs.google.com/spreadsheets/d/1zncebeUrh1Sfu1z0U1jdyErRboXiDZ3xeSt9NclbuYg/edit?usp=sharing"
KEY_FILE = "google_key.json"  # આપણે અપલોડ કરેલી ફાઈલનું નામ

# ==========================================

st.set_page_config(page_title="Tatva OS", page_icon="🟠", layout="wide")

# --- CONNECTION SETUP ---
def get_db_connection():
    # જો ફાઈલ ન મળે તો ચેતવણી આપશે
    if not os.path.exists(KEY_FILE):
        st.error(f"⚠️ ફાઈલ નથી મળી! કૃપા કરીને '{KEY_FILE}' ફાઈલ GitHub પર અપલોડ કરો.")
        st.stop()
        
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        # સીધી ફાઈલમાંથી જ ડેટા વાંચશે (કોઈ પેસ્ટિંગની લપ નહીં)
        creds = Credentials.from_service_account_file(KEY_FILE, scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_url(SHEET_URL).sheet1
    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")
        st.stop()

try:
    sheet = get_db_connection()
except:
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
    st.title("👥 Team")
    c1, c2 = st.columns([3,1])
    nm = c1.text_input("Name")
    if c2.button("Add") and nm:
        if nm not in st.session_state.db["team"]:
            st.session_state.db["team"].append(nm)
            save_db(st.session_state.db)
            st.rerun()
    for m in st.session_state.db["team"]:
        if m != "Self":
            c1, c2 = st.columns([4,1])
            c1.write(f"👤 {m}")
            if c2.button("Remove", key=f"rm_{m}"):
                st.session_state.db["team"].remove(m)
                save_db(st.session_state.db)
                st.rerun()