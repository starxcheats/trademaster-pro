import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class TradingManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔥 TradeMaster Pro - Final Version")
        self.root.geometry("1250x850")
        self.root.configure(bg='#0f172a')
        
        self.base_dir = "trading_data"
        os.makedirs(self.base_dir, exist_ok=True)
        
        self.load_data()
        self.create_widgets()
    
    def get_today_folder(self):
        return os.path.join(self.base_dir, datetime.now().strftime("%Y/%m/%d"))
    
    def default_data(self):
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
    
    def load_data(self):
        folder = self.get_today_folder()
        file = os.path.join(folder, "session.json")
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                for k, v in self.default_data().items():
                    if k not in self.data:
                        self.data[k] = v
            except:
                self.data = self.default_data()
        else:
            self.data = self.default_data()
    
    def save_data(self):
        with open(os.path.join(self.get_today_folder(), "session.json"), 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def create_widgets(self):
        tk.Label(self.root, text="TradeMaster Pro - Final", bg='#0f172a', fg='#60a5fa', font=('Segoe UI', 18, 'bold')).pack(pady=12)
        
        # Settings
        settings = tk.LabelFrame(self.root, text=" Settings ", bg='#1e2937', fg='#94a3b8')
        settings.pack(fill='x', padx=20, pady=10)
        
        tk.Label(settings, text="Initial Capital ($):", bg='#1e2937', fg='white').grid(row=0, column=0, padx=15, pady=8, sticky='w')
        self.init_cap_var = tk.DoubleVar(value=self.data["initial_capital"])
        self.init_entry = tk.Entry(settings, textvariable=self.init_cap_var, width=15, state='normal', bg='#334155', fg='white')
        self.init_entry.grid(row=0, column=1, padx=10)
        
        tk.Button(settings, text="Lock Initial Capital", bg='#eab308', command=self.lock_initial_capital).grid(row=0, column=2, padx=10)
        
        tk.Label(settings, text="Base Risk (%):", bg='#1e2937', fg='white').grid(row=1, column=0, padx=15, pady=8, sticky='w')
        self.risk_var = tk.DoubleVar(value=self.data["base_risk"])
        tk.Entry(settings, textvariable=self.risk_var, width=10, bg='#334155', fg='white').grid(row=1, column=1, padx=10, sticky='w')
        
        tk.Button(settings, text="Save Settings", bg='#22c55e', command=self.save_settings).grid(row=2, column=1, pady=10)
        
        # Recovery Mode
        self.recovery_var = tk.BooleanVar(value=self.data.get("recovery_mode", False))
        tk.Checkbutton(self.root, text="🔄 Recovery Mode (Extra 5 Trades)", bg='#1e2937', fg='#67e8f9', variable=self.recovery_var, command=self.toggle_recovery).pack(pady=5)
        
        # AI Suggestion
        self.sugg_frame = tk.LabelFrame(self.root, text="🤖 AI Next Trade Suggestion", bg='#1e2937', fg='#67e8f9')
        self.sugg_frame.pack(fill='x', padx=20, pady=8)
        self.sugg_label = tk.Label(self.sugg_frame, text="", bg='#1e2937', fg='#c4d0ff', font=('Segoe UI', 11), justify='left')
        self.sugg_label.pack(padx=15, pady=12, anchor='w')
        
        # Trade Entry
        entry = tk.LabelFrame(self.root, text=" New Trade ", bg='#1e2937', fg='#94a3b8')
        entry.pack(fill='x', padx=20, pady=10)
        
        tk.Label(entry, text="Symbol:", bg='#1e2937', fg='white').pack(side='left', padx=10)
        self.symbol_var = tk.StringVar()
        tk.Entry(entry, textvariable=self.symbol_var, width=20, bg='#334155', fg='white').pack(side='left')
        
        tk.Label(entry, text="Payout %:", bg='#1e2937', fg='white').pack(side='left', padx=15)
        self.payout_var = tk.DoubleVar(value=0)
        tk.Entry(entry, textvariable=self.payout_var, width=10, bg='#334155', fg='white').pack(side='left')
        
        tk.Button(entry, text="✅ WIN", bg='#22c55e', width=12, command=lambda: self.add_trade(True)).pack(side='left', padx=20)
        tk.Button(entry, text="❌ LOSS", bg='#ef4444', width=12, command=lambda: self.add_trade(False)).pack(side='left')
        
        # Controls
        ctrl = tk.Frame(self.root, bg='#0f172a')
        ctrl.pack(pady=8)
        tk.Button(ctrl, text="🗑️ Clear Session", bg='#ef4444', fg='white', command=self.clear_session).pack(side='left', padx=10)
        tk.Button(ctrl, text="🔄 Refresh", bg='#eab308', command=self.refresh).pack(side='left', padx=10)
        
        # Analysis
        self.analysis = tk.Text(self.root, height=7, bg='#1e2937', fg='#c4d0ff')
        self.analysis.pack(fill='x', padx=20, pady=10)
        
        # History
        hist = tk.LabelFrame(self.root, text=" History ", bg='#1e2937', fg='#94a3b8')
        hist.pack(fill='both', expand=True, padx=20, pady=10)
        self.tree = ttk.Treeview(hist, columns=('time','symbol','result','payout','amount'), show='headings')
        for col, h in [('time','Time'),('symbol','Symbol'),('result','Result'),('payout','Payout %'),('amount','Amount')]:
            self.tree.heading(col, text=h)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.update_suggestion()
        self.load_history()
        self.update_analysis()
    
    def lock_initial_capital(self):
        self.data["initial_capital"] = self.init_cap_var.get()
        self.data["current_capital"] = self.data["initial_capital"]
        self.save_data()
        self.init_entry.config(state='disabled')
        messagebox.showinfo("Locked", "Initial Capital Locked!")
    
    def save_settings(self):
        self.data["base_risk"] = self.risk_var.get()
        self.save_data()
        self.update_suggestion()
        messagebox.showinfo("Saved", "Settings Saved")
    
    def toggle_recovery(self):
        self.data["recovery_mode"] = self.recovery_var.get()
        self.save_data()
        self.update_analysis()
        self.update_suggestion()
    
    def calculate_suggestion(self):
        capital = self.data["current_capital"]
        base = self.data["base_risk"]
        losses = self.data.get("session_losses", 0)
        recovery = self.data.get("recovery_mode", False)
        
        if recovery:
            risk_pct = min(3.0, base * 1.6)
            advice = "RECOVERY MODE - Aggressive Recovery"
        elif losses >= 2:
            risk_pct = min(2.0, base * 1.3)
            advice = "Loss Streak - Careful Increase"
        elif self.data.get("session_wins", 0) >= 2:
            risk_pct = base * 1.5
            advice = "Good Streak - Risk Increased"
        else:
            risk_pct = base
            advice = "Normal Trade"
        
        amount = max(100, round(capital * risk_pct / 100, 2))
        return risk_pct, amount, advice
    
    def update_suggestion(self):
        pct, amt, advice = self.calculate_suggestion()
        text = f"Current Capital: ${self.data['current_capital']:.2f}\nSuggested Risk: {pct:.2f}% → Amount: ${amt:.2f}\n\n💡 {advice}"
        self.sugg_label.config(text=text)
    
    def add_trade(self, is_win):
        limit = self.data.get("daily_limit", 5) * (2 if self.data.get("recovery_mode", False) else 1)
        if len(self.data.get("trades", [])) >= limit:
            messagebox.showwarning("Stop", "আজকের ট্রেড লিমিট শেষ!")
            return
        
        symbol = self.symbol_var.get().strip() or "Unknown"
        payout = self.payout_var.get()
        _, suggested_amount, _ = self.calculate_suggestion()
        
        self.data.setdefault("trades", []).append({
            "time": datetime.now().strftime("%H:%M"),
            "symbol": symbol,
            "result": "WIN" if is_win else "LOSS",
            "payout": payout,
            "amount": suggested_amount
        })
        
        if is_win:
            profit = suggested_amount * (payout/100 if payout > 0 else 1.5)
            self.data["current_capital"] += profit
            self.data["total_profit"] = self.data.get("total_profit", 0) + profit
            self.data["session_wins"] = self.data.get("session_wins", 0) + 1
            self.data["session_losses"] = 0
        else:
            self.data["current_capital"] -= suggested_amount
            self.data["total_loss"] = self.data.get("total_loss", 0) + suggested_amount
            self.data["session_losses"] = self.data.get("session_losses", 0) + 1
            self.data["session_wins"] = 0
        
        self.save_data()
        self.load_history()
        self.update_analysis()
        self.update_suggestion()
    
    def load_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in reversed(self.data.get("trades", [])):
            self.tree.insert('', 0, values=(t.get('time'), t.get('symbol'), t.get('result'), t.get('payout',0), f"${t.get('amount',0):.2f}"))
    
    def update_analysis(self):
        self.analysis.delete(1.0, tk.END)
        trades = self.data.get("trades", [])
        winrate = round(sum(1 for t in trades if t.get('result')=='WIN') / len(trades) * 100, 2) if trades else 0
        text = f"Trades: {len(trades)} | Win Rate: {winrate}%\nCurrent Capital: ${self.data['current_capital']:.2f}\nTotal Profit: +${self.data.get('total_profit',0):.2f} | Loss: -${self.data.get('total_loss',0):.2f}"
        self.analysis.insert(tk.END, text)
    
    def clear_session(self):
        if messagebox.askyesno("Confirm", "পুরো সেশন ক্লিয়ার করবেন?"):
            self.data = self.default_data()
            self.save_data()
            self.refresh()
    
    def refresh(self):
        self.load_data()
        self.load_history()
        self.update_analysis()
        self.update_suggestion()

if __name__ == "__main__":
    app = TradingManager()
    app.root.mainloop()
