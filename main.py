import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(page_title="Intellectual Trader", layout="centered", page_icon="🧠")
st.title("🧠 Intellectual Trader")
st.markdown("**Fixed Risk + Compounding**")

def load_data():
    file = "trading_data/session.json"
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "initial_capital": 10000.0,
        "current_capital": 10000.0,
        "fixed_risk_amount": 250.0,
        "last_profit": 0.0,
        "trades": [],
        "total_profit": 0.0,
        "total_loss": 0.0
    }

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# Settings
st.sidebar.header("⚙️ Settings")
data["initial_capital"] = st.sidebar.number_input("Initial Capital ($)", value=data["initial_capital"], step=100.0)
data["fixed_risk_amount"] = st.sidebar.number_input("Fixed Risk Amount ($)", value=data.get("fixed_risk_amount", 250.0), step=10.0)

if st.sidebar.button("💾 Save Settings"):
    os.makedirs("trading_data", exist_ok=True)
    with open("trading_data/session.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    st.sidebar.success("✅ Saved!")

# Status
st.subheader("📊 Status")
st.metric("Current Capital", f"${data['current_capital']:.2f}")
st.metric("Fixed Risk", f"${data['fixed_risk_amount']:.2f}")

# AI Suggestion
st.subheader("🤖 AI Next Trade Suggestion")
suggested = data["fixed_risk_amount"] + data.get("last_profit", 0.0)
st.info(f"**Suggested Amount:** **${suggested:.2f}** (Fixed Risk + Last Profit)")

# Trade Entry
st.subheader("New Trade")
symbol = st.text_input("Symbol", placeholder="EURUSD, BTC, GOLD")
payout = st.number_input("Payout % (if WIN)", value=0.0, step=1.0)

c1, c2 = st.columns(2)
if c1.button("✅ WIN TRADE", use_container_width=True):
    amount = suggested
    profit = amount * (payout / 100 if payout > 0 else 1.8)
    data["current_capital"] += profit
    data["total_profit"] += profit
    data["last_profit"] = profit
    data.setdefault("trades", []).append({"time": datetime.now().strftime("%H:%M"), "symbol": symbol or "Unknown", "result": "WIN", "amount": amount})
    st.success("WIN! Next Trade will use compounding.")
    st.rerun()

if c2.button("❌ LOSS TRADE", use_container_width=True):
    amount = suggested
    data["current_capital"] = max(100, data["current_capital"] - amount)
    data["total_loss"] += amount
    data["last_profit"] = 0.0
    data.setdefault("trades", []).append({"time": datetime.now().strftime("%H:%M"), "symbol": symbol or "Unknown", "result": "LOSS", "amount": amount})
    st.error("LOSS - Reset to Fixed Risk")
    st.rerun()

# Summary
st.subheader("📈 Summary")
st.write(f"**Total Profit:** +${data.get('total_profit',0):.2f}")
st.write(f"**Total Loss:** -${data.get('total_loss',0):.2f}")

st.subheader("📜 History")
if data.get("trades"):
    for t in reversed(data["trades"]):
        emoji = "✅" if t.get("result") == "WIN" else "❌"
        st.write(f"{emoji} **{t['time']}** - {t['symbol']} | **${t['amount']:.2f}**")
else:
    st.info("No trades yet.")

# Clear History
if st.button("🗑️ Clear All History"):
    if st.checkbox("Confirm Delete All Trades?"):
        st.session_state.data = load_data()
        st.success("✅ History Cleared!")
        st.rerun()
