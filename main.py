import streamlit as st
import json
import os
from datetime import datetime

# Page Config
st.set_page_config(page_title="Intellectual Trader", page_icon="📈", layout="wide")

# Data File
DATA_FILE = "intellectual_trader.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Initialize Session State
if 'data' not in st.session_state:
    saved = load_data()
    if saved:
        st.session_state.data = saved
    else:
        st.session_state.data = {
            'initial_capital': 10000.0,
            'current_capital': 10000.0,
            'base_amount': 250.0,
            'compound_steps': 3,
            'profit_target': 1000.0,
            'loss_target': 500.0,
            'current_step': 1,
            'current_cycle': 1,
            'trade_history': [],
            'locked': False,
            'lock_reason': ""
        }
        save_data(st.session_state.data)

data = st.session_state.data

# Sidebar Settings
st.sidebar.header("⚙️ Settings")

data['initial_capital'] = st.sidebar.number_input("Initial Capital", value=data['initial_capital'], step=100.0)
data['base_amount'] = st.sidebar.number_input("Base Trade Amount", value=data['base_amount'], step=50.0)
data['compound_steps'] = st.sidebar.slider("Compounding Steps", 1, 10, data['compound_steps'])
data['profit_target'] = st.sidebar.number_input("Profit Target", value=data['profit_target'], step=100.0)
data['loss_target'] = st.sidebar.number_input("Loss Target", value=data['loss_target'], step=100.0)

if st.sidebar.button("💾 Save Settings & Reset Session"):
    data['current_capital'] = data['initial_capital']
    data['current_step'] = 1
    data['current_cycle'] = 1
    data['trade_history'] = []
    data['locked'] = False
    save_data(data)
    st.success("Settings Saved & Session Reset!")

# Main UI
st.title("📈 Intellectual Trader - Best Money Management System")
st.markdown("**Advanced Compounding System with Cycle & Step**")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Current Capital", f"৳{data['current_capital']:,.2f}")
with col2:
    profit = data['current_capital'] - data['initial_capital']
    st.metric("Total Profit", f"৳{profit:,.2f}", delta=f"{(profit/data['initial_capital']*100):+.1f}%")
with col3:
    st.metric("Cycle", f"{data['current_cycle']} | Step {data['current_step']}/{data['compound_steps']}")
with col4:
    st.metric("Base Amount", f"৳{data['base_amount']:,.2f}")

# Lock Status
if data['locked']:
    st.error(f"🚫 TRADING LOCKED: {data['lock_reason']}")

# Trade Section
st.subheader("Trade Action")

# Next Trade Amount Preview
next_amount = data['base_amount'] if data['current_step'] == 1 else \
              (data['trade_history'][-1]['trade_amount'] + data['trade_history'][-1]['profit'] if data['trade_history'] else data['base_amount'])

st.info(f"**Next Trade Amount:** ৳{next_amount:,.2f} | Current Step: {data['current_step']}")

return_pct = st.number_input("Trade Return % (Positive for Profit, Negative for Loss)", 
                            value=0.0, step=0.1, format="%.2f")

col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])

with col_btn1:
    if st.button("✅ Record WIN/LOSS", type="primary", use_container_width=True, disabled=data['locked']):
        if return_pct == 0:
            st.warning("Please enter a non-zero percentage")
        else:
            trade_amount = next_amount
            
            # Calculate profit/loss based on percentage
            pnl = trade_amount * (return_pct / 100)
            data['current_capital'] += pnl
            
            data['trade_history'].append({
                'trade_no': len(data['trade_history']) + 1,
                'cycle': data['current_cycle'],
                'step': data['current_step'],
                'time': datetime.now().strftime("%H:%M:%S"),
                'trade_amount': round(trade_amount, 2),
                'return_pct': round(return_pct, 2),
                'profit': round(pnl, 2),
                'capital_after': round(data['current_capital'], 2),
                'result': 'WIN' if return_pct >= 0 else 'LOSS'
            })
            
            # Update Cycle & Step
            if return_pct >= 0:  # WIN
                data['current_step'] += 1
                if data['current_step'] > data['compound_steps']:
                    data['current_step'] = 1
                    data['current_cycle'] += 1
                    st.success(f"🎉 Cycle {data['current_cycle']-1} Completed!")
            else:  # LOSS
                data['current_step'] = 1
                st.warning("🔄 Loss হওয়ায় Cycle Reset হয়েছে।")
            
            # Check Targets
            total_profit = data['current_capital'] - data['initial_capital']
            total_loss = data['initial_capital'] - data['current_capital']
            
            if total_profit >= data['profit_target']:
                data['locked'] = True
                data['lock_reason'] = f"PROFIT TARGET ACHIEVED (+৳{total_profit:,.2f})"
            elif total_loss >= data['loss_target']:
                data['locked'] = True
                data['lock_reason'] = f"LOSS TARGET HIT (-৳{total_loss:,.2f})"
            
            save_data(data)
            st.rerun()

with col_btn2:
    if st.button("🔄 Reset Cycle", use_container_width=True):
        data['current_step'] = 1
        save_data(data)
        st.success("Cycle Reset!")
        st.rerun()

with col_btn3:
    if st.button("🗑 Clear All"):
        if st.checkbox("Confirm Clear All?"):
            data['current_capital'] = data['initial_capital']
            data['current_step'] = 1
            data['current_cycle'] = 1
            data['trade_history'] = []
            data['locked'] = False
            save_data(data)
            st.success("All Data Cleared!")
            st.rerun()

# Current Status
st.subheader("📊 Current Status")
col_a, col_b = st.columns(2)
with col_a:
    st.info(f"**Next Trade Amount:** ৳{next_amount:,.2f}")
with col_b:
    st.info(f"**Compounding Steps:** {data['compound_steps']}")

# History
st.subheader("📜 Trade History")
if data['trade_history']:
    history_df = []
    for t in reversed(data['trade_history'][-20:]):
        history_df.append({
            "Trade #": t['trade_no'],
            "Cycle-Step": f"C{t['cycle']}-S{t['step']}",
            "Time": t['time'],
            "Amount": f"৳{t['trade_amount']:,.2f}",
            "Return %": f"{t.get('return_pct', 0):+.2f}%",
            "P/L": f"৳{t['profit']:,.2f}",
            "Capital": f"৳{t['capital_after']:,.2f}",
            "Result": "🟢 WIN" if t['result']=='WIN' else "🔴 LOSS"
        })
    st.dataframe(history_df, use_container_width=True)
else:
    st.info("No trades yet.")

st.caption("Intellectual Trader - Smart Compounding Money Management System")
