import json
import os
from datetime import datetime

class IntellectualTrader:
    def __init__(self):
        self.data_file = "intellectual_trader.json"
        self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.initial_capital = data.get('initial_capital', 10000.0)
                self.current_capital = data.get('current_capital', self.initial_capital)
                self.base_amount = data.get('base_amount', 250.0)
                self.compound_steps = data.get('compound_steps', 3)
                self.payout_pct = data.get('payout_pct', 90.0)
                self.profit_target = data.get('profit_target', 1000.0)
                self.loss_target = data.get('loss_target', 500.0)
                self.current_step = data.get('current_step', 1)
                self.current_cycle = data.get('current_cycle', 1)
                self.trade_history = data.get('trade_history', [])
                self.locked = data.get('locked', False)
                self.lock_reason = data.get('lock_reason', "")
        else:
            self.reset_all()
    
    def save_data(self):
        data = {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'base_amount': self.base_amount,
            'compound_steps': self.compound_steps,
            'payout_pct': self.payout_pct,
            'profit_target': self.profit_target,
            'loss_target': self.loss_target,
            'current_step': self.current_step,
            'current_cycle': self.current_cycle,
            'trade_history': self.trade_history,
            'locked': self.locked,
            'lock_reason': self.lock_reason
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def reset_all(self):
        print("\n=== নতুন সেটিংস ===")
        self.initial_capital = float(input("Initial Capital: ") or 10000)
        self.current_capital = self.initial_capital
        self.base_amount = float(input("Base Trade Amount (e.g. 250): ") or 250)
        self.compound_steps = int(input("Compounding Steps (1-10): ") or 3)
        self.payout_pct = float(input("Payout % on Win (e.g. 90): ") or 90)
        self.profit_target = float(input("Profit Target: ") or 1000)
        self.loss_target = float(input("Loss Target: ") or 500)
        self.current_step = 1
        self.current_cycle = 1
        self.trade_history = []
        self.locked = False
        self.lock_reason = ""
        self.save_data()
    
    def get_next_trade_amount(self):
        if self.current_step == 1:
            return self.base_amount
        else:
            # Previous trade amount + previous profit (if any)
            last_trade = self.trade_history[-1] if self.trade_history else None
            if last_trade and last_trade['result'] == 'WIN':
                return last_trade['trade_amount'] + last_trade['profit']
            return self.base_amount
    
    def check_lock(self):
        total_profit = self.current_capital - self.initial_capital
        total_loss = max(0, self.initial_capital - self.current_capital)  # simplified
        
        if total_profit >= self.profit_target:
            self.locked = True
            self.lock_reason = f"PROFIT TARGET ACHIEVED (+৳{total_profit:,.2f})"
        elif total_loss >= self.loss_target:
            self.locked = True
            self.lock_reason = f"LOSS TARGET HIT (-৳{total_loss:,.2f})"
    
    def record_trade(self, is_win):
        if self.locked:
            print(f"\n🚫 TRADING LOCKED: {self.lock_reason}")
            return
        
        trade_amount = self.get_next_trade_amount()
        
        if is_win:
            profit = trade_amount * (self.payout_pct / 100)
            self.current_capital += profit
            result = 'WIN'
            pnl = profit
        else:
            profit = -trade_amount
            self.current_capital += profit
            result = 'LOSS'
            pnl = profit
        
        self.trade_history.append({
            'trade_no': len(self.trade_history) + 1,
            'cycle': self.current_cycle,
            'step': self.current_step,
            'time': datetime.now().strftime("%H:%M:%S"),
            'trade_amount': round(trade_amount, 2),
            'profit': round(pnl, 2),
            'capital_after': round(self.current_capital, 2),
            'result': result
        })
        
        # Update step & cycle
        if is_win:
            self.current_step += 1
            if self.current_step > self.compound_steps:
                self.current_step = 1
                self.current_cycle += 1
                print(f"🎉 Cycle {self.current_cycle-1} Completed! New Cycle Started.")
        else:
            self.current_step = 1  # Loss → reset to step 1
            print("🔄 Loss হওয়ায় Cycle Reset হয়েছে।")
        
        self.check_lock()
        self.save_data()
        self.show_status()
    
    def show_status(self):
        total_profit = self.current_capital - self.initial_capital
        print(f"\n{'='*70}")
        print("          INTELLECTUAL TRADER - COMPOUNDING SYSTEM")
        print(f"{'='*70}")
        print(f"Initial Capital : ৳{self.initial_capital:,.2f}")
        print(f"Current Capital : ৳{self.current_capital:,.2f}  (Profit: ৳{total_profit:,.2f})")
        print(f"Base Amount     : ৳{self.base_amount:,.2f}")
        print(f"Compound Steps  : {self.compound_steps}")
        print(f"Payout          : {self.payout_pct}%")
        print(f"Cycle           : {self.current_cycle} | Step: {self.current_step}/{self.compound_steps}")
        print(f"Profit Target   : ৳{self.profit_target:,.2f} | Loss Target: ৳{self.loss_target:,.2f}")
        if self.locked:
            print(f"🚫 LOCKED → {self.lock_reason}")
        print(f"{'='*70}")
    
    def show_history(self):
        print("\n📊 HISTORY:")
        for t in self.trade_history[-10:]:  # last 10
            print(f"#{t['trade_no']} | C{t['cycle']}-S{t['step']} | {t['time']} | "
                  f"৳{t['trade_amount']:,.0f} | {t['profit']:+,.2f} | ৳{t['capital_after']:,.2f} | {t['result']}")
    
    def run(self):
        print("\n🎯 Intellectual Trader - Advanced Compounding System")
        while True:
            print("\n1. ✅ WIN")
            print("2. ❌ LOSS")
            print("3. 🔄 Reset Current Cycle")
            print("4. 🗑 Clear All History")
            print("5. 📊 Show History")
            print("6. ⚙️  New Settings")
            print("7. Exit")
            
            choice = input("\nChoose (1-7): ")
            
            if choice == '1':
                self.record_trade(True)
            elif choice == '2':
                self.record_trade(False)
            elif choice == '3':
                self.current_step = 1
                print("🔄 Current Cycle Reset.")
                self.save_data()
            elif choice == '4':
                confirm = input("সবকিছু Clear করবেন? (y/n): ")
                if confirm.lower() == 'y':
                    self.reset_all()
            elif choice == '5':
                self.show_history()
            elif choice == '6':
                self.reset_all()
            elif choice == '7':
                print("✅ সেশন সেভ হয়েছে। শুভ ট্রেডিং!")
                break

if __name__ == "__main__":
    app = IntellectualTrader()
    app.run()
