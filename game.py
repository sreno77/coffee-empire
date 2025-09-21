import tkinter as tk
from tkinter import ttk

# ========================
# GAME STATE
# ========================
state = {
    "cups": 0.0,
    "money": 0.0,
    "click_power": 1,
    "total_clicks": 0,
    "total_upgrades": 0,
    "achievements": [],
    "producers": {
        "barista": {"name": "Hire Barista", "baseProd": 1, "baseCost": 2, "costMul": 1.15, "qty": 0, "mult": 1, "icon": "barista.png"},
        "machine": {"name": "Buy Coffee Machine", "baseProd": 5, "baseCost": 50, "costMul": 1.15, "qty": 0, "mult": 1, "icon": "machine.png"},
        "shop": {"name": "Open Coffee Shop", "baseProd": 20, "baseCost": 200, "costMul": 1.15, "qty": 0, "mult": 1, "icon": "shop.png"},

        "farmer": {"name": "Hire Coffee Farmer", "baseProd": 100, "baseCost": 1000, "costMul": 1.15, "qty": 0, "mult": 1, "icon": "shop.png"},
        "factory": {"name": "Build Coffee Factory", "baseProd": 500, "baseCost": 10000, "costMul": 1.15, "qty": 0, "mult": 1, "icon": "shop.png"},
        "franchise": {"name": "Start Global Franchise", "baseProd": 5000, "baseCost": 100000, "costMul": 1.15, "qty": 0, "mult": 1, "icon": "shop.png"},
    },
    "upgrades": {
        "stronger_hands": {"type": "click", "name": "Stronger Hands", "mult": 2, "cost": 50, "purchased": False, "unlock_at": {"money": 20}, "icon": "hands.png"},
        "turbo_brewing": {"type": "click", "name": "Turbo Brewing", "mult": 3, "cost": 250, "purchased": False, "unlock_at": {"money": 100}, "icon": "turbo.png"},
        "better_beans": {"type": "producer", "name": "Better Beans", "target": "barista", "mult": 2, "cost": 100, "purchased": False, "unlock_at": {"producer": ("barista", 5)}, "icon": "beans.png"},
    }
}

# UI references
producer_widgets = {}
upgrade_widgets = {}
stats_widgets = {}
images = {}  # keep references alive

# ========================
# HELPERS
# ========================
def format_num(n):
    if n >= 1e6: return f"{n/1e6:.1f}M"
    if n >= 1e3: return f"{n/1e3:.1f}K"
    return f"{n:.0f}"

def get_cost(p): return int(p["baseCost"] * (p["costMul"] ** p["qty"]))

def get_total_production():
    return sum(p["qty"] * p["baseProd"] * p["mult"] for p in state["producers"].values())

def is_unlocked(u):
    cond = u.get("unlock_at", {})
    if "money" in cond and state["money"] < cond["money"]: return False
    if "producer" in cond:
        pid, qty = cond["producer"]
        if state["producers"][pid]["qty"] < qty: return False
    return True

def unlock_hint(u):
    cond = u.get("unlock_at", {})
    if "money" in cond: return f"Requires ${cond['money']}"
    if "producer" in cond:
        pid, qty = cond["producer"]
        return f"Requires {qty} {state['producers'][pid]['name']}(s)"
    return "Unlock condition unknown"

# ========================
# TOOLTIP CLASS
# ========================
class ToolTip:
    def __init__(self, widget, text=""):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text: return
        x, y = self.widget.winfo_rootx() + 25, self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0", relief="solid", borderwidth=1, font=("tahoma", "8"))
        label.pack(ipadx=4)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# ========================
# GAME ACTIONS
# ========================
def brew_click():
    gain = state["click_power"]
    state["cups"] += gain
    state["money"] += gain
    state["total_clicks"] += 1
    floating_text(canvas, 60, 40, f"+{gain} coffee", color="saddlebrown")
    check_achievements()
    update_ui()

def buy_producer(pid):
    p = state["producers"][pid]
    cost = get_cost(p)
    if state["money"] >= cost:
        state["money"] -= cost
        p["qty"] += 1
    update_ui()

def buy_upgrade(uid):
    u = state["upgrades"][uid]
    if u["purchased"] or not is_unlocked(u): return
    if state["money"] >= u["cost"]:
        state["money"] -= u["cost"]
        if u["type"] == "click":
            state["click_power"] *= u["mult"]
        elif u["type"] == "producer":
            state["producers"][u["target"]]["mult"] *= u["mult"]
        u["purchased"] = True
        state["total_upgrades"] += 1
    check_achievements()
    update_ui()

# ========================
# ANIMATIONS
# ========================
def floating_text(canvas, x, y, text, color="black"):
    label = tk.Label(canvas, text=text, fg=color, bg="white", font=("Arial", 10, "bold"))
    label.place(x=x, y=y)
    def animate(i=0):
        if i > 20: label.destroy(); return
        label.place(x=x, y=y - i)
        label.after(30, animate, i+1)
    animate()

# ========================
# ACHIEVEMENTS
# ========================
def check_achievements():
    achievements = [
        ("First Brew", lambda: state["total_clicks"] >= 1),
        ("Apprentice Barista", lambda: state["producers"]["barista"]["qty"] >= 10),
        ("Bean Tycoon", lambda: state["cups"] >= 1000),
        ("Upgrade Enthusiast", lambda: state["total_upgrades"] >= 3),
    ]
    for name, cond in achievements:
        if cond() and name not in state["achievements"]:
            state["achievements"].append(name)
            floating_text(canvas, 60, 20, f"Achievement: {name}", color="green")
    update_ui()

# ========================
# UI UPDATE
# ========================
def update_ui():
    stats_label.config(
        text=f"Cups: {format_num(state['cups'])}   |   Money: ${format_num(state['money'])}\n"
             f"Production: {get_total_production():.1f} cups/sec   |   Click Power: {state['click_power']}"
    )

    # Producers
    for pid, p in state["producers"].items():
        cost = get_cost(p)
        producer_widgets[pid]["label"].config(
            text=f"{p['name']} (x{p['qty']})\nCost: ${format_num(cost)} | +{p['baseProd']*p['mult']}/sec"
        )

    # Upgrades
    for uid, u in state["upgrades"].items():
        w = upgrade_widgets[uid]
        if not is_unlocked(u):
            w["label"].config(text="???")
            w["button"].config(state="disabled")
            continue
        if u["purchased"]:
            w["label"].config(text=f"{u['name']} (BOUGHT)")
            w["button"].config(state="disabled")
        else:
            w["label"].config(text=f"{u['name']} - Cost: ${format_num(u['cost'])}")
            w["button"].config(state="normal")

    # Stats & Achievements
    stats_widgets["clicks"].config(text=f"Total Clicks: {state['total_clicks']}")
    stats_widgets["upgrades"].config(text=f"Total Upgrades Bought: {state['total_upgrades']}")
    stats_widgets["achievements"].config(
        text="Achievements: " + (", ".join(state["achievements"]) if state["achievements"] else "None")
    )

# ========================
# GAME LOOP
# ========================
def game_loop():
    prod = get_total_production() / 10
    state["cups"] += prod
    state["money"] += prod
    check_achievements()
    update_ui()
    root.after(100, game_loop)

# ========================
# UI SETUP
# ========================
def setup_root():
    root = tk.Tk()
    root.title("🍵 Coffee Empire 🍵")
    return root

def setup_stats_label(root):
    stats_label = tk.Label(root, text="", font=("Arial", 12))
    stats_label.pack(pady=5)
    return stats_label

def setup_canvas(root):
    canvas = tk.Canvas(root, width=120, height=100, bg="white")
    canvas.pack(pady=5)
    return canvas

def setup_brew_button(canvas, images, brew_click):
    images["brew"] = tk.PhotoImage(file="cup.png")
    brew_btn = tk.Button(canvas, image=images["brew"], command=brew_click, borderwidth=0, highlightthickness=0, bg="white", activebackground="white")
    canvas.create_window(60, 50, window=brew_btn)
    ToolTip(brew_btn, "Brew Coffee")
    return brew_btn

def setup_notebook(root):
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    return notebook

def setup_producers_tab(notebook, images, producer_widgets, state, buy_producer):
    producers_tab = ttk.Frame(notebook)
    notebook.add(producers_tab, text="Producers")
    for pid, p in state["producers"].items():
        frame = tk.Frame(producers_tab)
        frame.pack(fill="x", pady=2)
        images[pid] = tk.PhotoImage(file=p["icon"])
        btn = tk.Button(frame, image=images[pid], command=lambda pid=pid: buy_producer(pid))
        btn.pack(side="left")
        label = tk.Label(frame, text="", anchor="w", justify="left")
        label.pack(side="left", padx=5)
        producer_widgets[pid] = {"button": btn, "label": label}
    return producers_tab

def setup_upgrades_tab(notebook, images, upgrade_widgets, state, buy_upgrade):
    upgrades_tab = ttk.Frame(notebook)
    notebook.add(upgrades_tab, text="Upgrades")
    for uid, u in state["upgrades"].items():
        frame = tk.Frame(upgrades_tab)
        frame.pack(fill="x", pady=2)
        images[uid] = tk.PhotoImage(file=u["icon"])
        btn = tk.Button(frame, image=images[uid], command=lambda uid=uid: buy_upgrade(uid))
        btn.pack(side="left")
        label = tk.Label(frame, text="???", anchor="w", justify="left")
        label.pack(side="left", padx=5)
        upgrade_widgets[uid] = {"button": btn, "label": label}
        ToolTip(label, unlock_hint(u))
    return upgrades_tab

def setup_stats_tab(notebook, stats_widgets):
    stats_tab = ttk.Frame(notebook)
    notebook.add(stats_tab, text="Stats & Achievements")
    stats_widgets["clicks"] = tk.Label(stats_tab, text="Total Clicks: 0", anchor="w")
    stats_widgets["clicks"].pack(fill="x", pady=2)
    stats_widgets["upgrades"] = tk.Label(stats_tab, text="Total Upgrades Bought: 0", anchor="w")
    stats_widgets["upgrades"].pack(fill="x", pady=2)
    stats_widgets["achievements"] = tk.Label(stats_tab, text="Achievements: None", anchor="w", wraplength=250, justify="left")
    stats_widgets["achievements"].pack(fill="x", pady=2)
    return stats_tab

# ========================
# MAIN
# ========================
def main():
    global root, stats_label, canvas
    root = setup_root()
    stats_label = setup_stats_label(root)
    canvas = setup_canvas(root)
    setup_brew_button(canvas, images, brew_click)
    notebook = setup_notebook(root)
    setup_producers_tab(notebook, images, producer_widgets, state, buy_producer)
    setup_upgrades_tab(notebook, images, upgrade_widgets, state, buy_upgrade)
    setup_stats_tab(notebook, stats_widgets)
    update_ui()
    game_loop()
    root.mainloop()

# ========================
# START
# ========================
if __name__ == "__main__":
    main()
