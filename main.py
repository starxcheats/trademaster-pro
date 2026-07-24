import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(page_title="Intellectual Trader", layout="centered", page_icon="🧠")
st.title("🧠 Intellectual Trader")
st.markdown("**Fixed Risk + Limited Compounding**")

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
        "daily_target_percent": 13.0,
        "daily_stop_loss_percent": 5.0,
        "max_compound_steps": 3,
        "current_step": 0,
        "trades": [],
        "total_profit": 0.0,
        "total_loss": 0.0,
        "recovery_mode": False
    }

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# Settings
st.sidebar.header("⚙️ Settings")
data["initial_capital"] = st.sidebar.number_input("Initial Capital ($)", value=data["initial_capital"], step=100.0)
data["fixed_risk_amount"] = st.sidebar.number_input("Fixed Risk Amount ($)", value=data.get("fixed_risk_amount", 250.0), step=10.0)
data["daily_target_percent"] = st.sidebar.number_input("Daily Target (%)", value=data.get("daily_target_percent", 13.0), step=0.5)
data["daily_stop_loss_percent"] = st.sidebar.number_input("Daily Stop Loss (%)", value=data.get("daily_stop_loss_percent", 5.0), step=0.5)
data["max_compound_steps"] = st.sidebar.slider("Max Compounding Steps", 1, 5, data.get("max_compound_steps", 3))
data["recovery_mode"] = st.sidebar.checkbox("Recovery Mode", value=data.get("recovery_mode", False))

if st.sidebar.button("💾 Save Settings"):
    os.makedirs("trading_data", exist_ok=True)
    with open("trading_data/session.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    st.sidebar.success("✅ Saved!")

# Calculations
capital = data["current_capital"]
fixed = data["fixed_risk_amount"]
step = data.get("current_step", 0)

st.subheader("📊 Status")
st.metric("Current Capital", f"${capital:.2f}")
st.metric("Current Compounding Step", f"{step} / {data['max_compound_steps']}")

# AI Suggestion
st.subheader("🤖 AI Next Trade Suggestion")
if data.get("recovery_mode"):
    suggested = fixed * 1.8
    st.info(f"**RECOVERY MODE**\nSuggested: **${suggested:.2f}**")
else:
    suggested = fixed + (step * fixed * 0.5)  # Compounding
    st.info(f"**Step {step}**\nSuggested Amount: **${suggested:.2f}**")

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
    data["current_step"] = min(step + 1, data["max_compound_steps"])
    data["session_wins"] = data.get("session_wins", 0) + 1
    data["session_losses"] = 0
    data.setdefault("trades", []).append({"time": datetime.now().strftime("%H:%M"), "symbol": symbol or "Unknown", "result": "WIN", "amount": amount})
    st.success("WIN! Compounding Increased")
    st.rerun()

if c2.button("❌ LOSS TRADE", use_container_width=True):
    amount = suggested
    data["current_capital"] = max(100, data["current_capital"] - amount)
    data["total_loss"] += amount
    data["current_step"] = 0  # Reset on loss
    data["session_losses"] = data.get("session_losses", 0) + 1
    data["session_wins"] = 0
    data.setdefault("trades", []).append({"time": datetime.now().strftime("%H:%M"), "symbol": symbol or "Unknown", "result": "LOSS", "amount": amount})
    st.error("LOSS - Reset to Base Amount")
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

if st.button("🗑️ Clear All History"):
    if st.checkbox("Confirm?"):
        st.session_state.data = load_data()
        st.success("History Cleared!")
        st.rerun()
