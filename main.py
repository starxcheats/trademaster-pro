import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(page_title="Intellectual Trader", layout="centered", page_icon="🧠")
st.title("🧠 Intellectual Trader")
st.markdown("**Best Money Management System**")

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
        "daily_target_percent": 13.0,
        "daily_stop_loss_percent": 5.0,
        "base_risk_percent": 1.0,
        "trades": [],
        "total_profit": 0.0,
        "total_loss": 0.0,
        "recovery_mode": False
    }

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# Sidebar
st.sidebar.header("⚙️ Settings")
initial_cap = st.sidebar.number_input("Initial Capital ($)", value=float(data.get("initial_capital", 10000.0)), step=100.0)
if st.sidebar.button("Reset Current Capital to Initial"):
    data["current_capital"] = initial_cap
    st.sidebar.success("Current Capital Reset!")

data["daily_target_percent"] = st.sidebar.number_input("Daily Profit Target (%)", value=data.get("daily_target_percent", 13.0), step=0.5)
data["daily_stop_loss_percent"] = st.sidebar.number_input("Daily Stop Loss (%)", value=data.get("daily_stop_loss_percent", 5.0), step=0.5)
data["base_risk_percent"] = st.sidebar.number_input("Base Risk per Trade (%)", value=data.get("base_risk_percent", 1.0), step=0.1)
data["recovery_mode"] = st.sidebar.checkbox("Recovery Mode", value=data.get("recovery_mode", False))

if st.sidebar.button("💾 Save All Settings"):
    data["initial_capital"] = initial_cap
    os.makedirs("trading_data", exist_ok=True)
    with open("trading_data/session.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    st.sidebar.success("✅ All Settings Saved!")

# Main Display
st.subheader("📊 Current Status")
col1, col2 = st.columns(2)
col1.metric("Initial Capital", f"${data.get('initial_capital', 10000):.2f}")
col2.metric("Current Capital", f"${data.get('current_capital', 10000):.2f}", 
            f"{data['current_capital'] - data['initial_capital']:.2f}")

daily_target = data["current_capital"] * (data["daily_target_percent"] / 100)
daily_stop = data["current_capital"] * (data["daily_stop_loss_percent"] / 100)

st.metric("Daily Target", f"${daily_target:.2f} ({data['daily_target_percent']}%)")
st.metric("Daily Stop Loss", f"${daily_stop:.2f} ({data['daily_stop_loss_percent']}%)")

# AI Suggestion
st.subheader("🤖 AI Next Trade Suggestion")
capital = data["current_capital"]
risk = data["base_risk_percent"]
suggested = max(100, round(capital * risk / 100, 2))

if data.get("recovery_mode"):
    suggested = max(100, round(suggested * 1.6, 2))
    st.info(f"**RECOVERY MODE**\nSuggested Amount: **${suggested:.2f}**")
else:
    st.info(f"**Normal Mode**\nSuggested Amount: **${suggested:.2f}**")

# Trade Entry
st.subheader("New Trade")
symbol = st.text_input("Symbol", placeholder="EURUSD, BTC, GOLD")
payout = st.number_input("Payout % (if WIN)", value=0.0, step=1.0)

c1, c2 = st.columns(2)
if c1.button("✅ WIN TRADE", use_container_width=True):
    amount = suggested
    profit = amount * (payout/100 if payout > 0 else 1.8)
    data["current_capital"] += profit
    data["total_profit"] = data.get("total_profit", 0) + profit
    data["session_wins"] = data.get("session_wins", 0) + 1
    data["session_losses"] = 0
    data.setdefault("trades", []).append({"time": datetime.now().strftime("%H:%M"), "symbol": symbol or "Unknown", "result": "WIN", "amount": amount})
    st.success("WIN Recorded!")
    st.rerun()

if c2.button("❌ LOSS TRADE", use_container_width=True):
    amount = suggested
    data["current_capital"] = max(100, data["current_capital"] - amount)
    data["total_loss"] = data.get("total_loss", 0) + amount
    data["session_losses"] = data.get("session_losses", 0) + 1
    data["session_wins"] = 0
    data.setdefault("trades", []).append({"time": datetime.now().strftime("%H:%M"), "symbol": symbol or "Unknown", "result": "LOSS", "amount": amount})
    st.error("LOSS Recorded!")
    st.rerun()

# Summary & History
st.subheader("📈 Summary")
st.write(f"**Total Profit:** +${data.get('total_profit',0):.2f}")
st.write(f"**Total Loss:** -${data.get('total_loss',0):.2f}")

st.subheader("📜 Trade History")
if data.get("trades"):
    for t in reversed(data["trades"]):
        emoji = "✅" if t.get("result") == "WIN" else "❌"
        st.write(f"{emoji} **{t['time']}** - {t['symbol']} | **${t['amount']:.2f}**")
else:
    st.info("No trades yet.")

if st.button("🗑️ Clear All History"):
    if st.checkbox("Confirm Delete All?"):
        st.session_state.data = load_data()
        st.success("History Cleared!")
        st.rerun()
