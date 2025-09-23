import sqlite3

class DatabaseManager:
    def __init__(self, db_name="coffee.db"):
        """Initialize the database connection and create a table if not exists."""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """Create game_state table if it doesn't exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cups REAL NOT NULL,
                money REAL NOT NULL,
                click_power INTEGER NOT NULL,
                total_clicks INTEGER NOT NULL,
                total_upgrades INTEGER NOT NULL,
                achievements TEXT DEFAULT '',
                producers TEXT DEFAULT '{}',
                upgrades TEXT DEFAULT '{}'
            )
        ''')
        self.conn.commit()

    # --- CRUD Operations ---

    def create(self, data: dict):
        """Insert a new game state."""
        self.cursor.execute('''
                INSERT INTO game_state (cups, money, click_power, total_clicks, total_upgrades, achievements, producers, upgrades)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                data.get("cups", 0.0),
                data.get("money", 0.0),
                data.get("click_power", 1),
                data.get("total_clicks", 0),
                data.get("total_upgrades", 0),
                data.get("achievements", ""),
                data.get("producers", "{}"),
                data.get("upgrades", "{}")
            )
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def read(self, id=None):
        """Fetch all game states or a specific game state by id."""
        if id:
            self.cursor.execute("SELECT * FROM game_state WHERE id=?", (id,))
            return self.cursor.fetchone()
        else:
            self.cursor.execute("SELECT * FROM game_state")
            return self.cursor.fetchall()
        
    def update(self, data: dict):
        """Update game state details by id."""
        id = data.get("id")
        if not id:
            raise ValueError("ID is required for update operation.")

        fields = []
        values = []

        for key in ["cups", "money", "click_power", "total_clicks", "total_upgrades", "achievements", "producers", "upgrades"]:
            if key in data:
                fields.append(f"{key}=?")
                values.append(data[key])

        if not fields:
            raise ValueError("No fields to update.")

        values.append(id)
        sql = f"UPDATE game_state SET {', '.join(fields)} WHERE id=?"
        self.cursor.execute(sql, tuple(values))
        self.conn.commit()

    def updateBak(self, id, cups=None, money=None, click_power=None, total_clicks=None, total_upgrades=None, achievements=None, producers=None, upgrades=None):
        """Update game state details by id."""
        if cups is not None:
            self.cursor.execute("UPDATE game_state SET cups=? WHERE id=?", (cups, id))

        if money is not None:
            self.cursor.execute("UPDATE game_state SET money=? WHERE id=?", (money, id))

        if click_power is not None:
            self.cursor.execute("UPDATE game_state SET click_power=? WHERE id=?", (click_power, id))

        if total_clicks is not None:
            self.cursor.execute("UPDATE game_state SET total_clicks=? WHERE id=?", (total_clicks, id))

        if total_upgrades is not None:
            self.cursor.execute("UPDATE game_state SET total_upgrades=? WHERE id=?", (total_upgrades, id))

        if achievements is not None:
            self.cursor.execute("UPDATE game_state SET achievements=? WHERE id=?", (achievements, id))

        if producers is not None:
            self.cursor.execute("UPDATE game_state SET producers=? WHERE id=?", (producers, id))

        if upgrades is not None:
            self.cursor.execute("UPDATE game_state SET upgrades=? WHERE id=?", (upgrades, id))

        self.conn.commit()

    def delete(self, id):
        """Delete a game state by id."""
        self.cursor.execute("DELETE FROM game_state WHERE id=?", (id,))
        self.conn.commit()

    def __del__(self):
        """Close the connection when the object is destroyed."""
        self.conn.close()

# --- Example usage ---
if __name__ == "__main__":
    db = DatabaseManager()

    # Create
    data = {
        "cups": 10.0,
        "money": 50.0,
        "click_power": 2,
        "total_clicks": 100,
        "total_upgrades": 5,
        "achievements": "First Brew, Bean Tycoon",
        "producers": '{"barista": {"name": "Hire Barista", "baseProd": 1, "baseCost": 2, "costMul": 1.15, "qty": 3, "mult": 1, "icon": "barista.png"}, "machine": {"name": "Buy Coffee Machine", "baseProd": 5, "baseCost": 100, "costMul": 1.15, "qty": 3, "mult": 1, "icon": "machine.png"}, "shop": {"name": "Open Coffee Shop", "baseProd": 20, "baseCost": 400, "costMul": 1.15, "qty": 1, "mult": 1, "icon": "shop.png"}, "farmer": {"name": "Hire Coffee Farmer", "baseProd": 100, "baseCost": 2000, "costMul": 1.15, "qty": 0, "mult": 1, "icon": "shop.png"}, "factory": {"name": "Build Coffee Factory", "baseProd": 500, "baseCost": 20000, "costMul": 1.15, "qty": 0, "mult": 1, "icon": "shop.png"}, "franchise": {"name": "Start Global Franchise", "baseProd": 5000, "baseCost": 200000, "costMul": 1.15, "qty": 0, "mult": 1, "icon": "shop.png"}}',
        "upgrades": '{"stronger_hands": {"type": "click", "name": "Stronger Hands", "mult": 2, "cost": 200, "purchased": True, "unlock_at": {"money": 20}, "icon": "hands.png"}, "turbo_brewing": {"type": "click", "name": "Turbo Brewing", "mult": 3, "cost": 1000, "purchased": True, "unlock_at": {"money": 100}, "icon": "turbo.png"}, "better_beans": {"type": "producer", "name": "Better Beans", "target": "barista", "mult": 2, "cost": 500, "purchased": False, "unlock_at": {"producer": ["barista", 5]}, "icon": "beans.png"}, "cold_brew": {"type": "producer", "name": "Cold Brew", "target": "barista", "mult": 2.5, "cost": 10000, "purchased": False, "unlock_at": {"producer": ["barista", 75]}, "icon": "beans.png"}}'
    }

    game_state_id = db.create(data)
    print(f"New game state ID: {game_state_id}")

    # Read
    game_state = db.read(game_state_id)
    print("Game state:", game_state)

    # Update
    db.update(game_state_id, cups=15.0, money=75.0)
    print("Updated game state:", db.read(game_state_id))

    # Delete
    db.delete(game_state_id)
    print("After deletion:", db.read())
