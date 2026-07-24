import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(page_title="Intellectual Trader", layout="centered", page_icon="🧠")
st.title("🧠 Intellectual Trader")
st.markdown("**Advanced Compounding Money Management**")

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
        "compounding_steps": 3,
        "trades": [],
        "total_profit": 0.0,
        "total_loss": 0.0,
        "recovery_mode": False
    }

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# Sidebar Settings
st.sidebar.header("⚙️ Settings")
data["initial_capital"] = st.sidebar.number_input("Initial Capital ($)", value=data["initial_capital"], step=100.0)
data["daily_target_percent"] = st.sidebar.number_input("Daily Target (%)", value=data["daily_target_percent"], step=0.5)
data["daily_stop_loss_percent"] = st.sidebar.number_input("Daily Stop Loss (%)", value=data["daily_stop_loss_percent"], step=0.5)
data["base_risk_percent"] = st.sidebar.number_input("Base Risk per Trade (%)", value=data["base_risk_percent"], step=0.1)
data["compounding_steps"] = st.sidebar.slider("Compounding Steps", 1, 5, data.get("compounding_steps", 3))
data["recovery_mode"] = st.sidebar.checkbox("Recovery Mode", value=data.get("recovery_mode", False))

if st.sidebar.button("💾 Save Settings"):
    os.makedirs("trading_data", exist_ok=True)
    with open("trading_data/session.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    st.sidebar.success("✅ Saved!")

# Calculations
capital = data["current_capital"]
daily_target = capital * (data["daily_target_percent"] / 100)
daily_stop = capital * (data["daily_stop_loss_percent"] / 100)
base_amount = capital * (data["base_risk_percent"] / 100)

st.subheader("📊 Status")
st.metric("Current Capital", f"${capital:.2f}")
st.metric("Daily Target", f"${daily_target:.2f} ({data['daily_target_percent']}%)")
st.metric("Daily Stop Loss", f"${daily_stop:.2f} ({data['daily_stop_loss_percent']}%)")

# AI Suggestion with Compounding
st.subheader("🤖 AI Next Trade Suggestion")
if data.get("recovery_mode"):
    suggested = max(100, round(base_amount * 1.8, 2))
    st.info(f"**RECOVERY MODE**\nSuggested: **${suggested:.2f}**")
else:
    suggested = max(100, round(base_amount, 2))
    st.info(f"**Normal / Compounding Trade**\nSuggested Amount: **${suggested:.2f}**")

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
    data["session_wins"] = data.get("session_wins", 0) + 1
    data["session_losses"] = 0
    data.setdefault("trades", []).append({"time": datetime.now().strftime("%H:%M"), "symbol": symbol or "Unknown", "result": "WIN", "amount": amount})
    st.success("WIN + Compounding Applied!")
    st.rerun()

if c2.button("❌ LOSS TRADE", use_container_width=True):
    amount = suggested
    data["current_capital"] = max(100, data["current_capital"] - amount)
    data["total_loss"] += amount
    data["session_losses"] = data.get("session_losses", 0) + 1
    data["session_wins"] = 0
    data.setdefault("trades", []).append({"time": datetime.now().strftime("%H:%M"), "symbol": symbol or "Unknown", "result": "LOSS", "amount": amount})
    st.error("LOSS - Reset to Base Amount for Next Trade")
    st.rerun()

# Summary
st.subheader("📈 Full Summary")
st.write(f"**Total Profit:** +${data.get('total_profit',0):.2f}")
st.write(f"**Total Loss:** -${data.get('total_loss',0):.2f}")
st.write(f"**Net:** ${data.get('total_profit',0) - data.get('total_loss',0):.2f}")

# History
st.subheader("📜 History")
if data.get("trades"):
    for t in reversed(data["trades"]):
        emoji = "✅" if t.get("result") == "WIN" else "❌"
        st.write(f"{emoji} **{t['time']}** - {t['symbol']} | **${t['amount']:.2f}**")
else:
    st.info("No trades yet.")

if st.button("🗑️ Clear All History"):
    if st.checkbox("Confirm?"):
        st.session_state.data = load_data()
        st.success("All Cleared!")
        st.rerun()
