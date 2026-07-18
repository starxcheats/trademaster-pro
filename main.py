import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(page_title="TradeMaster Pro", layout="centered", page_icon="🔥")
st.title("🔥 TradeMaster Pro - Web Version")

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
        "base_risk": 1.0,
        "trades": [],
        "session_wins": 0,
        "session_losses": 0,
        "daily_limit": 5,
        "recovery_mode": False,
        "total_profit": 0.0,
        "total_loss": 0.0
    }

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# Settings
st.sidebar.header("⚙️ Settings")
initial_cap = st.sidebar.number_input("Initial Capital ($)", value=float(data.get("initial_capital", 10000.0)), step=100.0)
base_risk = st.sidebar.number_input("Base Risk (%)", value=float(data.get("base_risk", 1.0)), min_value=0.1, step=0.1)
recovery_mode = st.sidebar.checkbox("Recovery Mode", value=data.get("recovery_mode", False))

if st.sidebar.button("💾 Save Settings"):
    data["initial_capital"] = initial_cap
    data["current_capital"] = initial_cap
    data["base_risk"] = base_risk
    data["recovery_mode"] = recovery_mode
    os.makedirs("trading_data", exist_ok=True)
    with open("trading_data/session.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    st.sidebar.success("✅ Saved!")

# Main Display
st.subheader("📊 Status")
st.metric("Current Capital", f"${data.get('current_capital', 10000):.2f}")

total_trades = len(data.get("trades", []))
normal_limit = data.get("daily_limit", 5)
in_recovery = recovery_mode and total_trades >= normal_limit

col1, col2 = st.columns(2)
col1.metric("Total Trades", total_trades)
wins = sum(1 for t in data.get("trades", []) if t.get("result") == "WIN")
winrate = round(wins / total_trades * 100, 1) if total_trades > 0 else 0
col2.metric("Win Rate", f"{winrate}%")

# AI Suggestion
st.subheader("🤖 AI Suggestion")
capital = data.get("current_capital", 10000.0)
risk = data.get("base_risk", 1.0)

if in_recovery:
    suggested = max(100, round(capital * risk * 1.6 / 100, 2))
    mode_text = "🔴 RECOVERY MODE (Aggressive)"
else:
    suggested = max(100, round(capital * risk / 100, 2))
    mode_text = "Normal Mode"

st.info(f"**Next Trade:** ${suggested:.2f}\n**Mode:** {mode_text}")

# Trade Entry
st.subheader("New Trade")
symbol = st.text_input("Symbol", placeholder="EURUSD, BTC, GOLD")
payout = st.number_input("Payout % (WIN)", value=0.0, step=1.0)

c1, c2 = st.columns(2)
if c1.button("✅ WIN TRADE", use_container_width=True):
    if total_trades >= normal_limit and not in_recovery:
        st.error("Normal limit reached. Turn on Recovery Mode.")
    else:
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
    if total_trades >= normal_limit and not in_recovery:
        st.error("Normal limit reached. Turn on Recovery Mode.")
    else:
        amount = suggested
        data["current_capital"] = max(100, data["current_capital"] - amount)
        data["total_loss"] = data.get("total_loss", 0) + amount
        data["session_losses"] = data.get("session_losses", 0) + 1
        data["session_wins"] = 0
        data.setdefault("trades", []).append({"time": datetime.now().strftime("%H:%M"), "symbol": symbol or "Unknown", "result": "LOSS", "amount": amount})
        st.error("LOSS Recorded!")
        st.rerun()

# History
st.subheader("📜 Trade History")
if data.get("trades"):
    for t in reversed(data["trades"]):
        emoji = "✅" if t.get("result") == "WIN" else "❌"
        st.write(f"{emoji} **{t['time']}** - {t['symbol']} | **${t['amount']:.2f}**")
else:
    st.info("No trades yet.")

# Clear Button (Fixed)
if st.button("🗑️ Clear All History", type="primary"):
    if st.checkbox("Are you sure you want to delete all trades?"):
        st.session_state.data = load_data()
        st.success("✅ All History Cleared!")
        st.rerun()