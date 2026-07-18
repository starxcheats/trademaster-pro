import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(page_title="TradeMaster Pro", layout="centered", page_icon="🔥")
st.title("🔥 TradeMaster Pro - Web Version")

# --- Original Logic Helpers ---

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
    file_path = os.path.join(folder, "session.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Ensure all keys exist
            for k, v in default_data().items():
                if k not in data:
                    data[k] = v
            return data
        except:
            pass
    return default_data()

def save_data(data):
    folder = get_today_folder()
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, "session.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Original 4-condition AI logic
def calculate_suggestion(data):
    capital = data.get("current_capital", 10000.0)
    base = data.get("base_risk", 1.0)
    losses = data.get("session_losses", 0)
    wins = data.get("session_wins", 0)
    recovery = data.get("recovery_mode", False)

    if recovery:
        risk_pct = min(3.0, base * 1.6)
        advice = "🔴 RECOVERY MODE - Aggressive Recovery"
    elif losses >= 2:
        risk_pct = min(2.0, base * 1.3)
        advice = "⚠️ Loss Streak - Careful Increase"
    elif wins >= 2:
        risk_pct = base * 1.5
        advice = "✅ Good Streak - Risk Increased"
    else:
        risk_pct = base
        advice = "⚪ Normal Trade"

    amount = max(100, round(capital * risk_pct / 100, 2))
    return risk_pct, amount, advice

# --- Session State Init ---

if "data" not in st.session_state:
    st.session_state.data = load_data()

# If we switch days, reload automatically
current_file = os.path.join(get_today_folder(), "session.json")
if "last_file" not in st.session_state or st.session_state.last_file != current_file:
    st.session_state.data = load_data()
    st.session_state.last_file = current_file

data = st.session_state.data

# --- Sidebar Settings ---

st.sidebar.header("⚙️ Settings")

# Lock state tracking
if "capital_locked" not in st.session_state:
    st.session_state.capital_locked = False

initial_val = float(data.get("initial_capital", 10000.0))
current_cap = float(data.get("current_capital", 10000.0))

# Show initial capital input (disabled if locked, but streamlit doesn't disable easily,
# so we show a note and ignore changes if locked)
init_input = st.sidebar.number_input(
    "Initial Capital ($)", 
    value=initial_val, 
    step=100.0, 
    disabled=st.session_state.capital_locked
)

if st.sidebar.button("🔒 Lock Initial Capital"):
    data["initial_capital"] = init_input
    data["current_capital"] = init_input
    st.session_state.capital_locked = True
    save_data(data)
    st.sidebar.success("✅ Capital Locked!")

base_risk_input = st.sidebar.number_input(
    "Base Risk (%)", 
    value=float(data.get("base_risk", 1.0)), 
    min_value=0.1, 
    step=0.1
)

recovery_input = st.sidebar.checkbox(
    "🔄 Recovery Mode (Extra 5 Trades)", 
    value=data.get("recovery_mode", False)
)

if st.sidebar.button("💾 Save Settings"):
    data["base_risk"] = base_risk_input
    data["recovery_mode"] = recovery_input
    # Only update initial/current if not locked; if locked keep as is
    if not st.session_state.capital_locked:
        data["initial_capital"] = init_input
    else:
        data["initial_capital"] = float(data.get("initial_capital", init_input))
    save_data(data)
    st.session_state.data = data
    st.sidebar.success("✅ Settings Saved!")

# --- Main Status ---

st.subheader("📊 Session Status")

col_a, col_b, col_c = st.columns(3)
col_a.metric("Current Capital", f"${data.get('current_capital', 0):.2f}")
col_b.metric("Initial Capital", f"${data.get('initial_capital', 0):.2f}")
col_c.metric("Base Risk %", f"{data.get('base_risk', 1.0)}%")

# Recovery indicator
if data.get("recovery_mode", False):
    st.warning("🔄 RECOVERY MODE ACTIVE — Daily limit doubled to 10 trades")

# Analysis metrics row
trades = data.get("trades", [])
total_trades = len(trades)
wins = sum(1 for t in trades if t.get("result") == "WIN")
winrate = round(wins / total_trades * 100, 2) if total_trades > 0 else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Trades", total_trades)
m2.metric("Win Rate", f"{winrate}%")
m3.metric("Session Wins", data.get("session_wins", 0))
m4.metric("Session Losses", data.get("session_losses", 0))

# --- AI Suggestion (Original Logic) ---

st.subheader("🤖 AI Next Trade Suggestion")
pct, amt, advice = calculate_suggestion(data)

st.info(
    f"**Suggested Risk:** {pct:.2f}%\n"
    f"**Suggested Amount:** ${amt:.2f}\n"
    f"**Advice:** {advice}\n"
    f"**Recovery Active:** {'Yes' if data.get('recovery_mode', False) else 'No'}"
)

# --- Trade Entry ---

st.subheader("📝 New Trade Entry")

symbol = st.text_input("Symbol", value="", placeholder="e.g. EURUSD, GOLD, BTC")
payout = st.number_input("Payout % (WIN only)", value=0.0, step=1.0)

# Original limit logic
normal_limit = data.get("daily_limit", 5)
limit = normal_limit * (2 if data.get("recovery_mode", False) else 1)
in_recovery = data.get("recovery_mode", False) and total_trades >= normal_limit

c_win, c_loss = st.columns(2)

if c_win.button("✅ WIN", use_container_width=True):
    if total_trades >= limit:
        st.error("⛔ Daily trade limit reached!")
    else:
        _, amount, _ = calculate_suggestion(data)
        # Original win formula: amount * (payout/100 if payout > 0 else 1.5)
        profit = amount * (payout / 100 if payout > 0 else 1.5)
        data["current_capital"] += profit
        data["total_profit"] = data.get("total_profit", 0.0) + profit
        data["session_wins"] = data.get("session_wins", 0) + 1
        data["session_losses"] = 0
        data.setdefault("trades", []).append({
            "time": datetime.now().strftime("%H:%M"),
            "symbol": symbol.strip() or "Unknown",
            "result": "WIN",
            "payout": payout,
            "amount": amount
        })
        save_data(data)
        st.session_state.data = data
        st.success(f"✅ WIN Recorded! Profit: +${profit:.2f}")
        st.rerun()

if c_loss.button("❌ LOSS", use_container_width=True):
    if total_trades >= limit:
        st.error("⛔ Daily trade limit reached!")
    else:
        _, amount, _ = calculate_suggestion(data)
        data["current_capital"] = max(100.0, data["current_capital"] - amount)
        data["total_loss"] = data.get("total_loss", 0.0) + amount
        data["session_losses"] = data.get("session_losses", 0) + 1
        data["session_wins"] = 0
        data.setdefault("trades", []).append({
            "time": datetime.now().strftime("%H:%M"),
            "symbol": symbol.strip() or "Unknown",
            "result": "LOSS",
            "payout": payout,
            "amount": amount
        })
        save_data(data)
        st.session_state.data = data
        st.error(f"❌ LOSS Recorded! Deducted: -${amount:.2f}")
        st.rerun()

# --- Analysis Text ---

st.subheader("📈 Session Analysis")
analysis_text = (
    f"Trades Completed: {len(trades)}\n"
    f"Win Rate: {winrate}%\n"
    f"Current Capital: ${data.get('current_capital', 0):.2f}\n"
    f"Initial Capital: ${data.get('initial_capital', 0):.2f}\n"
    f"Total Profit: +${data.get('total_profit', 0):.2f}\n"
    f"Total Loss: -${data.get('total_loss', 0):.2f}"
)
st.text_area("Analysis", value=analysis_text, height=150, disabled=True)

# --- Trade History (Original Columns) ---

st.subheader("📜 Trade History")
if trades:
    # Show newest first (reversed)
    for t in reversed(trades):
        emoji = "✅" if t.get("result") == "WIN" else "❌"
        payout_display = f"{t.get('payout', 0)}%"
        st.write(
            f"{emoji} **{t.get('time', '')}** | Symbol: **{t.get('symbol', 'Unknown')}** | "
            f"Result: **{t.get('result')}** | Payout: **{payout_display}** | Amount: **${t.get('amount', 0):.2f}**"
        )
else:
    st.info("No trades recorded yet.")

# Daily limit status
st.caption(f"Trade Limit: {len(trades)} / {limit} (Normal: {normal_limit}, Recovery: {'On' if data.get('recovery_mode') else 'Off'})")

# --- Clear Session (Fixed) ---

st.divider()
if st.button("🗑️ Clear All Session History", type="primary"):
    confirm = st.checkbox("⚠️ Confirm: Delete ALL trades and reset session?")
    if confirm:
        # Reset to default but keep folder logic
        st.session_state.data = default_data()
        # Also reset lock state? Original clears everything.
        st.session_state.capital_locked = False
        save_data(st.session_state.data)
        st.success("✅ All history cleared and session reset!")
        st.rerun()
