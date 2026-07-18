import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(page_title="TradeMaster Pro", layout="centered", page_icon="🔥")
st.title("🔥 TradeMaster Pro - Final Version")

def get_today_folder():
    return os.path.join("trading_data", datetime.now().strftime("%Y/%m/%d"))

def default_data():
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

def load_data():
    folder = get_today_folder()
    file = os.path.join(folder, "session.json")
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                d = json.load(f)
            # Merge missing defaults
            for k, v in default_data().items():
                if k not in d:
                    d[k] = v
            return d
        except:
            return default_data()
    return default_data()

def save_data(data):
    folder = get_today_folder()
    os.makedirs(folder, exist_ok=True)
    file = os.path.join(folder, "session.json")
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calculate_suggestion(data):
    capital = data.get("current_capital", 10000.0)
    base = data.get("base_risk", 1.0)
    losses = data.get("session_losses", 0)
    wins = data.get("session_wins", 0)
    recovery = data.get("recovery_mode", False)
    
    if recovery:
        risk_pct = min(3.0, base * 1.6)
        advice = "RECOVERY MODE - Aggressive Recovery"
    elif losses >= 2:
        risk_pct = min(2.0, base * 1.3)
        advice = "Loss Streak - Careful Increase"
    elif wins >= 2:
        risk_pct = base * 1.5
        advice = "Good Streak - Risk Increased"
    else:
        risk_pct = base
        advice = "Normal Trade"
        
    amount = max(100, round(capital * risk_pct / 100, 2))
    return risk_pct, amount, advice

# Initialize session state
if "data" not in st.session_state:
    st.session_state.data = load_data()
if "capital_locked" not in st.session_state:
    st.session_state.capital_locked = False
if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False

data = st.session_state.data

# Settings Sidebar
st.sidebar.header("⚙️ Settings")
initial_cap = st.sidebar.number_input("Initial Capital ($)", value=float(data.get("initial_capital", 10000.0)), step=100.0, disabled=st.session_state.capital_locked)
base_risk = st.sidebar.number_input("Base Risk (%)", value=float(data.get("base_risk", 1.0)), min_value=0.1, step=0.1)

if st.sidebar.button("🔒 Lock Initial Capital", disabled=st.session_state.capital_locked):
    data["initial_capital"] = initial_cap
    data["current_capital"] = initial_cap
    st.session_state.capital_locked = True
    save_data(data)
    st.sidebar.success("Initial Capital Locked!")
    st.rerun()

if st.sidebar.button("💾 Save Settings"):
    data["base_risk"] = base_risk
    save_data(data)
    st.sidebar.success("Settings Saved")
    st.rerun()

recovery_mode = st.sidebar.checkbox("🔄 Recovery Mode (Extra 5 Trades)", value=data.get("recovery_mode", False))
if recovery_mode != data.get("recovery_mode", False):
    data["recovery_mode"] = recovery_mode
    save_data(data)
    st.rerun()

# Main Display
st.subheader("📊 Status")
total_trades = len(data.get("trades", []))
limit = data.get("daily_limit", 5) * (2 if data.get("recovery_mode", False) else 1)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Capital", f"${data.get('current_capital', 10000):.2f}")
col2.metric("Total Trades", total_trades)
wins = sum(1 for t in data.get("trades", []) if t.get("result") == "WIN")
winrate = round(wins / total_trades * 100, 2) if total_trades > 0 else 0
col3.metric("Win Rate", f"{winrate}%")
col4.metric("Trade Limit", f"{total_trades}/{limit}")

# AI Suggestion
st.subheader("🤖 AI Next Trade Suggestion")
risk_pct, suggested_amount, advice = calculate_suggestion(data)
st.info(f"Current Capital: ${data['current_capital']:.2f}\n\nSuggested Risk: {risk_pct:.2f}% → Amount: ${suggested_amount:.2f}\n\n💡 {advice}")

# Trade Entry
st.subheader("New Trade")
symbol = st.text_input("Symbol", placeholder="EURUSD, BTC, GOLD")
payout = st.number_input("Payout %", value=0.0, step=1.0)

c1, c2 = st.columns(2)

def add_trade(is_win):
    if total_trades >= limit:
        st.error("আজকের ট্রেড লিমিট শেষ!")
        return
    
    sym = symbol.strip() or "Unknown"
    pay = payout
    _, suggested_amt, _ = calculate_suggestion(data)
    
    data.setdefault("trades", []).append({
        "time": datetime.now().strftime("%H:%M"),
        "symbol": sym,
        "result": "WIN" if is_win else "LOSS",
        "payout": pay,
        "amount": suggested_amt
    })
    
    if is_win:
        profit = suggested_amt * (pay/100 if pay > 0 else 1.5)
        data["current_capital"] += profit
        data["total_profit"] = data.get("total_profit", 0) + profit
        data["session_wins"] = data.get("session_wins", 0) + 1
        data["session_losses"] = 0
        st.success("WIN Recorded!")
    else:
        data["current_capital"] -= suggested_amt
        data["total_loss"] = data.get("total_loss", 0) + suggested_amt
        data["session_losses"] = data.get("session_losses", 0) + 1
        data["session_wins"] = 0
        st.error("LOSS Recorded!")
        
    save_data(data)
    st.rerun()

if c1.button("✅ WIN TRADE", use_container_width=True):
    add_trade(True)

if c2.button("❌ LOSS TRADE", use_container_width=True):
    add_trade(False)

# History
st.subheader("📜 History")
if data.get("trades"):
    for t in reversed(data["trades"]):
        emoji = "✅" if t.get("result") == "WIN" else "❌"
        st.write(f"{emoji} **{t['time']}** - {t['symbol']} | Result: {t['result']} | Payout: {t.get('payout', 0)}% | Amount: ${t.get('amount', 0):.2f}")
else:
    st.info("No trades yet.")

# Controls
st.write("---")
if st.button("🗑️ Clear Session", type="primary"):
    st.session_state.confirm_clear = True

if st.session_state.confirm_clear:
    st.warning("পুরো সেশন ক্লিয়ার করবেন?")
    cc1, cc2 = st.columns(2)
    if cc1.button("Yes, Clear All", type="primary"):
        st.session_state.data = default_data()
        save_data(st.session_state.data)
        st.session_state.capital_locked = False
        st.session_state.confirm_clear = False
        st.rerun()
    if cc2.button("Cancel"):
        st.session_state.confirm_clear = False
        st.rerun()
