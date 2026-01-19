import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- SETUP & CONNECTION ---
st.set_page_config(page_title="Tatva OS", page_icon="🟠", layout="wide")

# Google Sheets Connection
def get_db_connection():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    # Secrets mathi key lai ne login karse
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    # Sheet kholse
    sheet_url = st.secrets["private_gsheets_url"]
    return client.open_by_url(sheet_url).sheet1

try:
    sheet = get_db_connection()
except Exception as e:
    st.error(f"Connection Error: {e}")
    st.stop()

# --- DATABASE FUNCTIONS ---
def load_db():
    try:
        # Sheet na pehla khana (A1) mathi badho data lavse
        val = sheet.cell(1, 1).value
        if val:
            return json.loads(val)
    except:
        pass
    return {"orders": [], "team": ["Self"]}

def save_db(data):
    # Badho data Sheet na A1 khana ma save karse
    sheet.update_cell(1, 1, json.dumps(data))

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR & MENU ---
st.sidebar.title("🟠 Tatva OS Cloud")
if st.sidebar.button("🔄 Refresh Data"):
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
    c1.metric("Active Orders", len(orders))
    c2.metric("Net Profit", f"₹{net}")
    c3.metric("Revenue", f"₹{rev}")
    c4.metric("Cash Hand", f"₹{hand}")
    
    st.divider()
    if not orders:
        st.info("No orders yet.")
    else:
        for o in reversed(orders[-10:]):
            c_recd = sum(int(p["amt"]) for p in o.get("income", []))
            pending = int(o["price"]) - c_recd
            status = "✅ Paid" if pending <= 0 else f"⏳ ₹{pending} Left"
            st.success(f"**{o['client']}** | {o['work']} | ₹{o['price']} | {status}")

# --- NEW ORDER ---
elif menu == "New Order":
    st.title("➕ New Order")
    with st.form("new_order", clear_on_submit=True):
        c1, c2 = st.columns(2)
        client = c1.text_input("Client Name")
        work = c2.text_input("Work Details")
        price = c1.number_input("Deal Price (₹)", min_value=0)
        date = c2.date_input("Date", datetime.now())
        
        if st.form_submit_button("Create Order"):
            if client and price:
                new_o = {
                    "id": int(datetime.now().timestamp()),
                    "client": client, "work": work, "price": int(price),
                    "date": date.strftime("%d/%m/%Y"),
                    "income": [], "tasks": []
                }
                # Data update and save to sheet
                st.session_state.db["orders"].append(new_o)
                save_db(st.session_state.db)
                st.success("Saved to Google Sheet!")
                st.rerun()

# --- ORDER DETAILS ---
elif menu == "Order Details":
    st.title("📦 Order Manager")
    opts = {f"{o['client']} - {o['work']}": o['id'] for o in st.session_state.db["orders"]}
    sel = st.selectbox("Select Order", list(opts.keys()))
    
    if sel:
        oid = opts[sel]
        order = next(o for o in st.session_state.db["orders"] if o["id"] == oid)
        
        c_recd = sum(int(p["amt"]) for p in order.get("income", []))
        c_paid = sum(sum(int(p["amt"]) for p in t.get("payouts", [])) for t in order.get("tasks", []))
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Recd (In)", f"₹{c_recd}")
        k2.metric("Paid (Out)", f"₹{c_paid}")
        k3.metric("Net Hand", f"₹{c_recd - c_paid}")
        st.divider()
        
        t1, t2, t3 = st.tabs(["💰 Income", "🛠 Expenses", "⚙️ Actions"])
        
        with t1:
            pend = int(order["price"]) - c_recd
            st.info(f"Deal: ₹{order['price']} | Pending: ₹{pend}")
            x1, x2 = st.columns([3,1])
            amt = x1.number_input("Add Payment", min_value=1, key="pay_in")
            if x2.button("Add"):
                order["income"].append({"amt": int(amt), "date": datetime.now().strftime("%d/%m/%Y")})
                save_db(st.session_state.db)
                st.rerun()
            for i, p in enumerate(order["income"]):
                ic1, ic2, ic3 = st.columns([2,2,1])
                ic1.write(p["date"])
                ic2.write(f"₹{p['amt']}")
                if ic3.button("❌", key=f"di_{i}"):
                    order["income"].pop(i)
                    save_db(st.session_state.db)
                    st.rerun()

        with t2:
            with st.expander("Add Expense", expanded=True):
                a1, a2, a3, a4 = st.columns([2,2,2,1])
                tt = a1.selectbox("Type", ["Model", "Print", "Color", "Other"])
                ta = a2.selectbox("Artist", st.session_state.db["team"])
                tc = a3.number_input("Cost", min_value=0)
                if a4.button("Add"):
                    if tc > 0:
                        order["tasks"].append({"id": int(datetime.now().timestamp()), "type": tt, "artist": ta, "cost": int(tc), "payouts": []})
                        save_db(st.session_state.db)
                        st.rerun()
            
            for t in order.get("tasks", []):
                paid = sum(int(p["amt"]) for p in t.get("payouts", []))
                due = int(t["cost"]) - paid
                st.markdown(f"**{t['type']} ({t['artist']})** | Cost: ₹{t['cost']} | :red[Due: ₹{due}]")
                b1, b2, b3 = st.columns([2,1,1])
                p_amt = b1.number_input("Pay", key=f"pay_{t['id']}", label_visibility="collapsed")
                if b2.button("Pay", key=f"bp_{t['id']}"):
                    if p_amt > 0:
                        t["payouts"].append({"amt": int(p_amt), "date": datetime.now().strftime("%d/%m/%Y")})
                        save_db(st.session_state.db)
                        st.rerun()
                if b3.button("🗑", key=f"del_{t['id']}"):
                    order["tasks"].remove(t)
                    save_db(st.session_state.db)
                    st.rerun()
                st.divider()

        with t3:
            if st.button("✅ Mark Full Done"):
                today = datetime.now().strftime("%d/%m/%Y")
                rem_c = int(order["price"]) - c_recd
                if rem_c > 0: order["income"].append({"amt": rem_c, "date": f"{today} (Auto)"})
                for t in order["tasks"]:
                    paid = sum(int(p["amt"]) for p in t.get("payouts", []))
                    rem_t = int(t["cost"]) - paid
                    if rem_t > 0: t["payouts"].append({"amt": rem_t, "date": f"{today} (Auto)"})
                save_db(st.session_state.db)
                st.success("Settled!")
                st.rerun()
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