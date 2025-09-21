import time
import threading
import math

# --- Game State ---
state = {
    "cups": 0.0,
    "money": 0.0,
    "producers": {
        "barista": {"name": "Hire Barista", "baseProd": 1, "baseCost": 2, "costMul": 1.15, "qty": 0, "mult": 1},
        "machine": {"name": "Buy Coffee Machine", "baseProd": 5, "baseCost": 50, "costMul": 1.15, "qty": 0, "mult": 1},
        "shop": {"name": "Open Coffee Shop", "baseProd": 20, "baseCost": 200, "costMul": 1.15, "qty": 0, "mult": 1},
        "farmer": {"name": "Hire Coffee Farmer", "baseProd": 100, "baseCost": 1000, "costMul": 1.15, "qty": 0, "mult": 1},
        "factory": {"name": "Build Coffee Factory", "baseProd": 500, "baseCost": 10000, "costMul": 1.15, "qty": 0, "mult": 1},
        "franchise": {"name": "Start Global Franchise", "baseProd": 5000, "baseCost": 100000, "costMul": 1.15, "qty": 0, "mult": 1},
    },
    "upgrades": {
        "better_beans": {"name": "Better Beans", "target": "barista", "mult": 2, "cost": 100, "purchased": False},
        "espresso": {"name": "Espresso Machines", "target": "machine", "mult": 2, "cost": 500, "purchased": False},
        "branding": {"name": "Global Branding", "target": "shop", "mult": 2, "cost": 2000, "purchased": False},
    },
    "running": True
}

# --- Helpers ---
def format_num(num: float) -> str:
    if num >= 1e9:
        return f"{num/1e9:.2f}B"
    if num >= 1e6:
        return f"{num/1e6:.2f}M"
    if num >= 1e3:
        return f"{num/1e3:.2f}K"
    return f"{num:.0f}"

def get_cost(p):
    return p["baseCost"] * (p["costMul"] ** p["qty"])

def get_total_production():
    total = 0
    for p in state["producers"].values():
        total += p["baseProd"] * p["qty"] * p["mult"]
    return total

# --- Core Actions ---
def brew_click():
    state["cups"] += 1
    state["money"] += 1

def buy_producer(pid):
    p = state["producers"][pid]
    cost = get_cost(p)
    if state["money"] >= cost:
        state["money"] -= cost
        p["qty"] += 1
        print(f"✅ Bought {p['name']} (x{p['qty']})")
    else:
        print(f"❌ Not enough money. Need ${format_num(cost)}")

def buy_upgrade(uid):
    u = state["upgrades"][uid]
    if u["purchased"]:
        print("❌ Already purchased.")
        return
    if state["money"] >= u["cost"]:
        state["money"] -= u["cost"]
        state["producers"][u["target"]]["mult"] *= u["mult"]
        u["purchased"] = True
        print(f"✅ Upgrade applied: {u['name']}")
    else:
        print(f"❌ Not enough money. Need ${format_num(u['cost'])}")

# --- Idle Loop ---
def idle_loop():
    last = time.time()
    while state["running"]:
        now = time.time()
        delta = now - last
        last = now
        prod = get_total_production()
        gained = prod * delta
        state["cups"] += gained
        state["money"] += gained
        time.sleep(0.25)

# --- UI Loop ---
def main():
    threading.Thread(target=idle_loop, daemon=True).start()
    print("☕ Welcome to Coffee Empire (Expanded Python Prototype)!")
    print("Commands: brew, buy, upgrade, stats, quit\n")

    while state["running"]:
        cmd = input("> ").strip().lower()

        if cmd == "brew":
            brew_click()
            print("You brewed a cup of coffee!")

        elif cmd == "buy":
            print("\n--- Producers ---")
            for pid, p in state["producers"].items():
                cost = get_cost(p)
                print(f"{pid}: {p['name']} | Owned: {p['qty']} | Cost: ${format_num(cost)} | +{p['baseProd']*p['mult']}/sec")
            choice = input("Which one? ").strip().lower()
            if choice in state["producers"]:
                buy_producer(choice)

        elif cmd == "upgrade":
            print("\n--- Upgrades ---")
            for uid, u in state["upgrades"].items():
                status = "BOUGHT" if u["purchased"] else f"${format_num(u['cost'])}"
                print(f"{uid}: {u['name']} | {status}")
            choice = input("Which one? ").strip().lower()
            if choice in state["upgrades"]:
                buy_upgrade(choice)

        elif cmd == "stats":
            print(f"Cups: {format_num(state['cups'])} | Money: ${format_num(state['money'])}")
            print(f"Total production: {get_total_production():.1f} cups/sec")

        elif cmd == "quit":
            state["running"] = False
            print("Goodbye!")
        else:
            print("Commands: brew, buy, upgrade, stats, quit")

if __name__ == "__main__":
    main()
