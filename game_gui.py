import tkinter as tk
import time

# --- Game State ---
state = {
    "cups": 0.0,
    "money": 0.0,
    "click_power": 1,
    "producers": {
        "barista": {"name": "Hire Barista", "baseProd": 1, "baseCost": 2, "costMul": 1.15, "qty": 0, "mult": 1},
        "machine": {"name": "Buy Coffee Machine", "baseProd": 5, "baseCost": 50, "costMul": 1.15, "qty": 0, "mult": 1},
        "shop": {"name": "Open Coffee Shop", "baseProd": 20, "baseCost": 200, "costMul": 1.15, "qty": 0, "mult": 1},
    },
    "upgrades": {
        "better_beans": {"name": "Better Beans", "target": "barista", "mult": 2, "cost": 100, "purchased": False},
        "espresso": {"name": "Espresso Machines", "target": "machine", "mult": 2, "cost": 500, "purchased": False},
        "branding": {"name": "Global Branding", "target": "shop", "mult": 2, "cost": 2000, "purchased": False},
        "stronger_hands": {"name": "Stronger Hands", "target": "click", "mult": 2, "cost": 50, "purchased": False},
        "turbo_brewing": {"name": "Turbo Brewing", "target": "click", "mult": 3, "cost": 250, "purchased": False},
    }
}

producer_frames = {}
upgrade_frames = {}

# --- Helpers ---
def format_num(num: float) -> str:
    if num >= 1e9: return f"{num/1e9:.2f}B"
    if num >= 1e6: return f"{num/1e6:.2f}M"
    if num >= 1e3: return f"{num/1e3:.2f}K"
    return f"{num:.0f}"

def get_cost(p): return p["baseCost"] * (p["costMul"] ** p["qty"])
def get_total_production(): return sum(p["baseProd"] * p["qty"] * p["mult"] for p in state["producers"].values())

# --- Core Actions ---
def brew_click():
    click_gain = state["click_power"]
    state["cups"] += click_gain
    state["money"] += click_gain
    #animate_cup_fill()
    animate_brew_button()
    floating_text(canvas, 60, 40, f"+{click_gain} coffee", color="saddlebrown")
    update_ui()

def buy_producer(pid):
    p = state["producers"][pid]
    cost = get_cost(p)
    frame = producer_frames[pid]  # store row frame reference
    if state["money"] >= cost:
        state["money"] -= cost
        p["qty"] += 1
        flash_row(frame, success=True)
    else:
        flash_row(frame, success=False)
        flash_message(f"Need ${format_num(cost)}")
    update_ui()


def buy_upgrade(uid):
    u = state["upgrades"][uid]
    frame = upgrade_frames[uid]
    if u["purchased"]:
        flash_message("Already purchased")
        return
    if state["money"] >= u["cost"]:
        state["money"] -= u["cost"]
        if u["target"] == "click":
            state["click_power"] *= u["mult"]
        else:
            state["producers"][u["target"]]["mult"] *= u["mult"]
        u["purchased"] = True
        flash_row(frame, success=True)
    else:
        flash_row(frame, success=False)
        flash_message(f"Need ${format_num(u['cost'])}")
    update_ui()


# --- UI Setup ---
root = tk.Tk()
root.title("☕ Coffee Empire")

stats_label = tk.Label(root, text="", font=("Arial", 14))
stats_label.pack(pady=8)

# Load safe image
def safe_load_image(fname):
    try:
        return tk.PhotoImage(file=fname)
    except Exception:
        return tk.PhotoImage(width=32, height=32)  # blank fallback

coffee_img = safe_load_image("coffee_cup.png")
canvas = tk.Canvas(root, width=120, height=160, bg="white", highlightthickness=0)
canvas.pack(pady=5)
canvas.create_image(60, 80, image=coffee_img)
cup_fill = canvas.create_rectangle(32, 140, 88, 140, fill="saddlebrown", width=0)

brew_button = tk.Button(root, text="BREW COFFEE", font=("Arial", 16, "bold"), command=brew_click)
brew_button.pack(pady=8)

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=8, pady=8)

producers_frame = tk.LabelFrame(main_frame, text="Producers", padx=10, pady=10)
producers_frame.pack(side="left", padx=6, pady=6, fill="y")

upgrades_frame = tk.LabelFrame(main_frame, text="Upgrades", padx=10, pady=10)
upgrades_frame.pack(side="right", padx=6, pady=6, fill="y")

# --- Load Icons ---
icon_files = {
    "barista": "barista.png",
    "machine": "machine.png",
    "shop": "shop.png",
    "better_beans": "better_beans.png",
    "espresso": "espresso.png",
    "branding": "branding.png",
    "stronger_hands": "stronger_hands.png",
    "turbo_brewing": "turbo_brewing.png"
}
icons = {key: safe_load_image(fname) for key, fname in icon_files.items()}

producer_widgets = {}
upgrade_widgets = {}

# Feedback label
message_label = tk.Label(root, text="", fg="red", font=("Arial", 10))
message_label.pack()

def flash_message(text, duration=1200):
    message_label.config(text=text)
    root.after(duration, lambda: message_label.config(text=""))

# --- Row Flash Animation ---
def flash_row(frame, success=True):
    color = "#a6f3a6" if success else "#f3a6a6"  # green vs red

    frame.config(bg=color)
    for child in frame.winfo_children():
        child.config(bg=color)

    # fade back after 300ms
    root.after(300, lambda: reset_row_bg(frame))

def reset_row_bg(frame):
    frame.config(bg="white")
    for child in frame.winfo_children():
        child.config(bg="white")


# --- Producers ---
def make_producer_row(pid, p):
    frame = tk.Frame(producers_frame, highlightthickness=1, relief="raised", bg="white")
    frame.pack(fill="x", pady=3)
    producer_frames[pid] = frame

    icon_label = tk.Label(frame, image=icons[pid], bg="white")
    icon_label.image = icons[pid]
    icon_label.pack(side="left", padx=5)

    text_label = tk.Label(frame, text="", anchor="w", bg="white")
    text_label.pack(side="left", padx=5, fill="x", expand=True)
    producer_widgets[pid] = text_label

    # Click anywhere in frame to buy
    def on_click(e=None): buy_producer(pid)
    frame.bind("<Button-1>", on_click)
    icon_label.bind("<Button-1>", on_click)
    text_label.bind("<Button-1>", on_click)

    # Hover effect
    def on_enter(e): frame.config(bg="#f0f0f0"); text_label.config(bg="#f0f0f0"); icon_label.config(bg="#f0f0f0")
    def on_leave(e): frame.config(bg="white"); text_label.config(bg="white"); icon_label.config(bg="white")
    frame.bind("<Enter>", on_enter)
    frame.bind("<Leave>", on_leave)
    icon_label.bind("<Enter>", on_enter)
    text_label.bind("<Enter>", on_enter)
    icon_label.bind("<Leave>", on_leave)
    text_label.bind("<Leave>", on_leave)

for pid, p in state["producers"].items():
    make_producer_row(pid, p)

# --- Upgrades ---
for uid, u in state["upgrades"].items():
    frame = tk.Frame(upgrades_frame, highlightthickness=1, relief="raised", bg="white")
    frame.pack(fill="x", pady=3)
    upgrade_frames[uid] = frame

    icon_label = tk.Label(frame, image=icons[uid], bg="white")
    icon_label.image = icons[uid]
    icon_label.pack(side="left", padx=5)

    text_label = tk.Label(frame, text="", anchor="w", bg="white")
    text_label.pack(side="left", padx=5, fill="x", expand=True)
    upgrade_widgets[uid] = text_label

    def on_click(e=None, x=uid): buy_upgrade(x)
    frame.bind("<Button-1>", on_click)
    icon_label.bind("<Button-1>", on_click)
    text_label.bind("<Button-1>", on_click)

    def on_enter(e): frame.config(bg="#f0f0f0"); text_label.config(bg="#f0f0f0"); icon_label.config(bg="#f0f0f0")
    def on_leave(e): frame.config(bg="white"); text_label.config(bg="white"); icon_label.config(bg="white")
    frame.bind("<Enter>", on_enter)
    frame.bind("<Leave>", on_leave)
    icon_label.bind("<Enter>", on_enter)
    text_label.bind("<Enter>", on_enter)
    icon_label.bind("<Leave>", on_leave)
    text_label.bind("<Leave>", on_leave)

# --- Cup Animation ---
# def animate_cup_fill():
#     for i in range(10):
#         root.after(i * 20, lambda h=140 - i*10: canvas.coords(cup_fill, 32, h, 88, 140))
#     root.after(220, lambda: canvas.coords(cup_fill, 32, 140, 88, 140))

# --- Brew Button Animation ---
def animate_brew_button():
    # flash color
    brew_button.config(bg="#d9ead3")  # light green
    root.after(100, lambda: brew_button.config(bg="SystemButtonFace"))

# --- Floating Text Animation ---
def floating_text(canvas, x, y, text, color="brown"):
    label = canvas.create_text(x, y, text=text, fill=color, font=("Arial", 12, "bold"))

    def animate(step=0):
        if step < 20:
            # move upward
            canvas.move(label, 0, -2)
            # fade (adjust color alpha if supported)
            alpha = max(0, 255 - step * 12)
            hex_alpha = f"#{alpha:02x}{alpha:02x}{alpha:02x}"
            try:
                canvas.itemconfig(label, fill=color)  # Tkinter doesn't support alpha well
            except:
                pass
            root.after(50, lambda: animate(step + 1))
        else:
            canvas.delete(label)

    animate()



# --- Update UI ---
def update_ui():
    stats_label.config(
        text=f"Cups: {format_num(state['cups'])}   |   Money: ${format_num(state['money'])}\n"
             f"Production: {get_total_production():.1f} cups/sec"
    )

    for pid, p in state["producers"].items():
        cost = get_cost(p)
        producer_widgets[pid].config(
            text=f"{p['name']} (x{p['qty']}) - Cost: ${format_num(cost)} - +{p['baseProd']*p['mult']}/sec"
        )

    for uid, u in state["upgrades"].items():
        if u["purchased"]:
            upgrade_widgets[uid].config(text=f"{u['name']} (BOUGHT)")
        else:
            upgrade_widgets[uid].config(text=f"{u['name']} - Cost: ${format_num(u['cost'])}")

# --- Idle Loop ---
last_time = time.time()
def idle_loop():
    global last_time
    now = time.time()
    delta = now - last_time
    last_time = now

    prod = get_total_production()
    gained = prod * delta
    state["cups"] += gained
    state["money"] += gained

    update_ui()
    root.after(250, idle_loop)

# Start game
update_ui()
idle_loop()
root.mainloop()
