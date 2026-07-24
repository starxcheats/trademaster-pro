import streamlit as st
import json
import os
from datetime import datetime

# Page Config
st.set_page_config(page_title="Intellectual Trader", page_icon="ðŸ“ˆ", layout="wide")

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
            'payout_pct': 90.0,
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
st.sidebar.header("âš™ï¸ Settings")

data['initial_capital'] = st.sidebar.number_input("Initial Capital", value=data['initial_capital'], step=100.0)
data['base_amount'] = st.sidebar.number_input("Base Trade Amount", value=data['base_amount'], step=50.0)
data['compound_steps'] = st.sidebar.slider("Compounding Steps", 1, 10, data['compound_steps'])
data['payout_pct'] = st.sidebar.number_input("Payout % on WIN", value=data['payout_pct'], step=5.0)
data['profit_target'] = st.sidebar.number_input("Profit Target", value=data['profit_target'], step=100.0)
data['loss_target'] = st.sidebar.number_input("Loss Target", value=data['loss_target'], step=100.0)

if st.sidebar.button("ðŸ’¾ Save Settings & Reset Session"):
    data['current_capital'] = data['initial_capital']
    data['current_step'] = 1
    data['current_cycle'] = 1
    data['trade_history'] = []
    data['locked'] = False
    save_data(data)
    st.success("Settings Saved & Session Reset!")

# Main UI
st.title("ðŸ“ˆ Intellectual Trader - Best Money Management System")
st.markdown("**Advanced Compounding System with Cycle & Step**")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Current Capital", f"à§³{data['current_capital']:,.2f}")
with col2:
    profit = data['current_capital'] - data['initial_capital']
    st.metric("Total Profit", f"à§³{profit:,.2f}", delta=f"{(profit/data['initial_capital']*100):+.1f}%")
with col3:
    st.metric("Cycle", f"{data['current_cycle']} | Step {data['current_step']}/{data['compound_steps']}")
with col4:
    st.metric("Base Amount", f"à§³{data['base_amount']:,.2f}")

# Lock Status
if data['locked']:
    st.error(f"ðŸš« TRADING LOCKED: {data['lock_reason']}")

# Trade Buttons
st.subheader("Trade Action")

btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([2,2,1,1])

with btn_col1:
    if st.button("âœ… WIN", type="primary", use_container_width=True, disabled=data['locked']):
        trade_amount = data['base_amount'] if data['current_step'] == 1 else \
                      (data['trade_history'][-1]['trade_amount'] + data['trade_history'][-1]['profit'] if data['trade_history'] else data['base_amount'])
        
        profit = trade_amount * (data['payout_pct'] / 100)
        data['current_capital'] += profit
        
        data['trade_history'].append({
            'trade_no': len(data['trade_history']) + 1,
            'cycle': data['current_cycle'],
            'step': data['current_step'],
            'time': datetime.now().strftime("%H:%M:%S"),
            'trade_amount': round(trade_amount, 2),
            'profit': round(profit, 2),
            'capital_after': round(data['current_capital'], 2),
            'result': 'WIN'
        })
        
        data['current_step'] += 1
        if data['current_step'] > data['compound_steps']:
            data['current_step'] = 1
            data['current_cycle'] += 1
        
        # Check lock
        if (data['current_capital'] - data['initial_capital']) >= data['profit_target']:
            data['locked'] = True
            data['lock_reason'] = "PROFIT TARGET ACHIEVED"
        
        save_data(data)
        st.rerun()

with btn_col2:
    if st.button("âŒ LOSS", type="secondary", use_container_width=True, disabled=data['locked']):
        trade_amount = data['base_amount'] if data['current_step'] == 1 else \
                      (data['trade_history'][-1]['trade_amount'] + data['trade_history'][-1]['profit'] if data['trade_history'] else data['base_amount'])
        
        loss = -trade_amount
        data['current_capital'] += loss
        
        data['trade_history'].append({
            'trade_no': len(data['trade_history']) + 1,
            'cycle': data['current_cycle'],
            'step': data['current_step'],
            'time': datetime.now().strftime("%H:%M:%S"),
            'trade_amount': round(trade_amount, 2),
            'profit': round(loss, 2),
            'capital_after': round(data['current_capital'], 2),
            'result': 'LOSS'
        })
        
        data['current_step'] = 1  # Reset on loss
        
        # Check lock
        if (data['initial_capital'] - data['current_capital']) >= data['loss_target']:
            data['locked'] = True
            data['lock_reason'] = "LOSS TARGET HIT"
        
        save_data(data)
        st.rerun()

with btn_col3:
    if st.button("ðŸ”„ Reset Cycle"):
        data['current_step'] = 1
        save_data(data)
        st.success("Cycle Reset!")
        st.rerun()

with btn_col4:
    if st.button("ðŸ—‘ Clear All"):
        if st.checkbox("Confirm Clear?"):
            data['current_capital'] = data['initial_capital']
            data['current_step'] = 1
            data['current_cycle'] = 1
            data['trade_history'] = []
            data['locked'] = False
            save_data(data)
            st.success("All Data Cleared!")
            st.rerun()

# Status
st.subheader("ðŸ“Š Current Status")
col_a, col_b = st.columns(2)
with col_a:
    st.info(f"**Next Trade Amount:** à§³{ (data['base_amount'] if data['current_step']==1 else (data['trade_history'][-1]['trade_amount'] + data['trade_history'][-1]['profit'] if data['trade_history'] else data['base_amount'])) :,.2f}")
with col_b:
    st.info(f"**Payout on Win:** {data['payout_pct']}%")

# History
st.subheader("ðŸ“œ Trade History")
if data['trade_history']:
    history_df = []
    for t in reversed(data['trade_history'][-20:]):
        history_df.append({
            "Trade #": t['trade_no'],
            "Cycle-Step": f"C{t['cycle']}-S{t['step']}",
            "Time": t['time'],
            "Amount": f"à§³{t['trade_amount']:,.2f}",
            "P/L": f"à§³{t['profit']:,.2f}",
            "Capital": f"à§³{t['capital_after']:,.2f}",
            "Result": "ðŸŸ¢ WIN" if t['result']=='WIN' else "ðŸ”´ LOSS"
        })
    st.dataframe(history_df, use_container_width=True)
else:
    st.info("No trades yet.")

# Footer
st.caption("Intellectual Trader - Smart Compounding Money Management System")
