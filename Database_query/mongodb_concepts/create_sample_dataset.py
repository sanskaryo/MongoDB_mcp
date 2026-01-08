"""Generate a synthetic restaurant analytics dataset.

This script creates realistic sample data for the following MongoDB collections:
- customers
- menu_items
- orders
- delivery_details
- users
- audit_logs

Outputs
=======
1. JSON files written to the project-level ``data/`` directory
2. Optional direct insertion into MongoDB (``--insert`` flag)

Usage
=====
# Only write JSON files
python mongodb_concepts/create_sample_dataset.py

# Write JSON files and upsert into MongoDB using credentials from .env
python mongodb_concepts/create_sample_dataset.py --insert

The script reads ``MONGODB_URI`` (or ``MONGO_URI``) and ``MONGODB_DATABASE``
(or ``DB_NAME``) from the .env file when inserting into MongoDB.
"""

from __future__ import annotations

import argparse
import json
import os
import random
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List

from dotenv import load_dotenv

try:
    from pymongo import MongoClient
    from pymongo.collection import Collection
except ImportError:  # pragma: no cover - optional dependency for JSON-only usage
    MongoClient = None  # type: ignore
    Collection = None  # type: ignore

# Load environment variables once so CLI insertion can reuse existing .env values
load_dotenv()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_DB_NAME = "restaurant_management"

RANDOM_SEED = 8675309
CUSTOMER_COUNT = 60
MENU_ITEM_COUNT = 24
ORDER_COUNT = 480
USER_COUNT = 12

SEGMENTS = ["vip", "premium", "standard", "new"]
ORDER_TYPES = ["dine_in", "delivery", "takeout"]
ORDER_STATUSES = ["completed", "pending", "cancelled", "refunded"]
PAYMENT_METHODS = ["card", "upi", "cash", "wallet"]
USER_ROLES = ["manager", "chef", "server", "delivery", "cashier"]

MENU_CATALOG = {
    "Starters": [
        ("Garlic Bread", 6.5, 2.1),
        ("Bruschetta", 7.2, 2.6),
        ("Stuffed Mushrooms", 8.0, 3.0),
        ("Loaded Nachos", 9.5, 3.8),
    ],
    "Mains": [
        ("Margherita Pizza", 14.0, 5.2),
        ("BBQ Chicken Pizza", 16.5, 6.1),
        ("Penne Alfredo", 15.0, 4.9),
        ("Veggie Burger", 12.5, 4.1),
        ("Grilled Salmon", 21.0, 9.0),
        ("Ribeye Steak", 28.0, 12.2),
    ],
    "Desserts": [
        ("Tiramisu", 7.0, 2.5),
        ("Cheesecake", 7.5, 2.8),
        ("Chocolate Lava Cake", 8.5, 3.3),
    ],
    "Beverages": [
        ("Fresh Lime Soda", 4.5, 1.0),
        ("Iced Tea", 4.0, 1.2),
        ("Craft Coffee", 5.5, 1.6),
        ("Orange Juice", 4.8, 1.3),
        ("Mocktail", 6.5, 2.0),
    ],
}

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Riley", "Casey", "Jamie",
    "Drew", "Rowan", "Harper", "Avery", "Skyler", "Quinn", "Hayden",
    "Dakota", "Elliot", "Kennedy", "Sawyer", "Peyton", "Blake",
]
LAST_NAMES = [
    "Smith", "Johnson", "Lee", "Garcia", "Brown", "Martinez", "Davis",
    "Miller", "Wilson", "Anderson", "Thomas", "Jackson", "White",
    "Harris", "Clark", "Lewis", "Robinson", "Walker", "Young", "King",
]
STREETS = [
    "Main Street", "Oak Avenue", "Cedar Lane", "Pine Street", "Maple Road",
    "Elm Street", "Lakeview Drive", "Sunset Boulevard", "Ridgeway Court",
    "Highland Avenue",
]
CITIES = [
    "Seattle", "Austin", "Denver", "Boston", "San Diego", "Portland",
    "Nashville", "Chicago", "San Francisco", "Atlanta",
]

# ---------------------------------------------------------------------------
# Utility Helpers
# ---------------------------------------------------------------------------

def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def random_phone() -> str:
    return f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


def random_email(name: str) -> str:
    base = name.lower().replace(" ", ".")
    domain = random.choice(["example.com", "mail.com", "dinetown.io"])
    return f"{base}{random.randint(10, 99)}@{domain}"


def random_address() -> str:
    street_number = random.randint(10, 999)
    street = random.choice(STREETS)
    city = random.choice(CITIES)
    return f"{street_number} {street}, {city}"


def random_date(start_days_ago: int = 120, span_days: int = 110) -> datetime:
    start = datetime.utcnow() - timedelta(days=start_days_ago)
    offset = timedelta(days=random.randint(0, span_days), hours=random.randint(8, 21))
    return start + offset


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def make_customer(customer_id: int) -> Dict[str, object]:
    full_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    segment = random.choices(SEGMENTS, weights=[0.1, 0.2, 0.45, 0.25], k=1)[0]
    registration = datetime.utcnow() - timedelta(days=random.randint(40, 380))
    return {
        "_id": f"cust_{customer_id:04d}",
        "customer_id": f"cust_{customer_id:04d}",
        "name": full_name,
        "email": random_email(full_name),
        "phone": random_phone(),
        "segment": segment,
        "registration_date": registration.strftime("%Y-%m-%d"),
        "total_spent": 0.0,
        "orders_count": 0,
        "loyalty_points": 0,
        "last_order_date": None,
    }


def make_menu_item(item_id: int, name: str, category: str, price: float, cost: float) -> Dict[str, object]:
    return {
        "_id": f"menu_{item_id:03d}",
        "item_id": f"menu_{item_id:03d}",
        "name": name,
        "category": category.lower(),
        "price": round(price, 2),
        "cost": round(cost, 2),
        "description": f"Signature {name.lower()} prepared daily.",
        "availability": random.random() > 0.05,
        "allergens": random.sample(["gluten", "dairy", "nuts", "soy"], k=random.randint(0, 2)),
        "preparation_time": random.randint(8, 30),
    }


def build_menu_items() -> List[Dict[str, object]]:
    items: List[Dict[str, object]] = []
    item_id = 1
    for category, entries in MENU_CATALOG.items():
        for name, price, cost in entries:
            items.append(make_menu_item(item_id, name, category, price, cost))
            item_id += 1
    # If configured MENU_ITEM_COUNT is larger than catalog, extend with variations
    while len(items) < MENU_ITEM_COUNT:
        base = random.choice(items)
        variant_name = f"{base['name']} ({random.choice(['Chef Special', 'XL', 'Seasonal'])})"
        items.append(
            make_menu_item(
                len(items) + 1,
                variant_name,
                base["category"].title(),
                float(base["price"]) + random.uniform(-1.5, 2.5),
                float(base["cost"]) + random.uniform(-1.0, 1.5),
            )
        )
    return items


def choose_items(menu: List[Dict[str, object]]) -> List[Dict[str, object]]:
    selection = random.sample(menu, k=random.randint(1, 4))
    items = []
    for item in selection:
        quantity = random.randint(1, 3)
        unit_price = float(item["price"])
        total_price = quantity * unit_price
        items.append(
            {
                "menu_item_id": item["item_id"],
                "name": item["name"],
                "quantity": quantity,
                "unit_price": unit_price,
                "price": unit_price,  # Maintain compatibility with existing analytics pipelines
                "total_price": round(total_price, 2),
            }
        )
    return items


def make_user(user_id: int) -> Dict[str, object]:
    full_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    role = random.choice(USER_ROLES)
    hire_date = datetime.utcnow() - timedelta(days=random.randint(120, 720))
    permissions_map = {
        "manager": ["order_management", "reports", "menu_updates", "staff"],
        "chef": ["order_management", "menu_updates"],
        "server": ["order_management"],
        "delivery": ["deliveries"],
        "cashier": ["payments", "order_management"],
    }
    return {
        "_id": f"staff_{user_id:03d}",
        "user_id": f"staff_{user_id:03d}",
        "name": full_name,
        "role": role,
        "email": random_email(full_name),
        "hire_date": hire_date.strftime("%Y-%m-%d"),
        "active": random.random() > 0.08,
        "permissions": permissions_map.get(role, ["order_management"]),
    }


# ---------------------------------------------------------------------------
# Dataset Builders
# ---------------------------------------------------------------------------

def generate_dataset() -> Dict[str, List[Dict[str, object]]]:
    random.seed(RANDOM_SEED)

    customers = [make_customer(i + 1) for i in range(CUSTOMER_COUNT)]
    menu_items = build_menu_items()
    menu_index = {item["item_id"]: item for item in menu_items}

    customer_stats = defaultdict(lambda: {"total": 0.0, "count": 0, "last": None, "points": 0})
    delivery_records: List[Dict[str, object]] = []
    audit_logs: List[Dict[str, object]] = []

    orders: List[Dict[str, object]] = []
    for order_num in range(ORDER_COUNT):
        order_id = f"order_{order_num + 1:05d}"
        customer = random.choice(customers)
        items = choose_items(menu_items)
        subtotal = sum(item["total_price"] for item in items)
        discount = round(subtotal * random.choice([0, 0.05, 0.1]) if random.random() < 0.35 else 0.0, 2)
        tax = round((subtotal - discount) * 0.08, 2)
        total_amount = round(subtotal - discount + tax, 2)

        order_type = random.choices(ORDER_TYPES, weights=[0.45, 0.4, 0.15], k=1)[0]
        status = random.choices(ORDER_STATUSES, weights=[0.75, 0.1, 0.1, 0.05], k=1)[0]
        created_at = random_date()

        order_doc = {
            "_id": order_id,
            "order_id": order_id,
            "customer_id": customer["customer_id"],
            "order_date": iso(created_at),
            "created_at": iso(created_at),
            "order_type": order_type,
            "status": status,
            "order_status": status,  # Legacy compatibility for older scripts
            "total_amount": total_amount,
            "subtotal": round(subtotal, 2),
            "discount": discount,
            "tax": tax,
            "payment_mode": random.choice(PAYMENT_METHODS),
            "items": items,
            "special_instructions": random.choice([
                "",
                "Extra cheese",
                "No onions",
                "Gluten-free dough",
                "Mild spice",
            ]),
            "delivery_address": random_address() if order_type == "delivery" else None,
        }

        orders.append(order_doc)

        # Update customer stats
        stats = customer_stats[customer["customer_id"]]
        stats["total"] += total_amount
        stats["count"] += 1
        stats["last"] = max(stats["last"], created_at) if stats["last"] else created_at
        stats["points"] += int(total_amount // 10)

        # Delivery details for delivery orders
        if order_type == "delivery" and status in {"completed", "pending"}:
            pickup_time = created_at + timedelta(minutes=random.randint(15, 25))
            delivery_time = pickup_time + timedelta(minutes=random.randint(12, 28))
            delivery_records.append(
                {
                    "_id": f"delivery_{order_id}",
                    "order_id": order_id,
                    "delivery_person": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                    "pickup_time": iso(pickup_time),
                    "delivery_time": iso(delivery_time),
                    "delivery_status": "delivered" if status == "completed" else "in_transit",
                    "delivery_fee": round(random.uniform(3.5, 6.5), 2),
                    "distance_km": round(random.uniform(1.2, 6.8), 2),
                    "customer_rating": random.randint(3, 5),
                }
            )

        # Audit log entries
        audit_logs.append(
            {
                "_id": f"audit_{order_id}",
                "timestamp": iso(created_at + timedelta(minutes=5)),
                "user_id": random.choice([f"staff_{i:03d}" for i in range(1, USER_COUNT + 1)]),
                "action": random.choice(["order_created", "order_updated", "payment_processed"]),
                "resource": "orders",
                "resource_id": order_id,
                "details": f"Order status set to {status}",
            }
        )

    # Finalize customer stats
    for customer in customers:
        stats = customer_stats[customer["customer_id"]]
        customer["total_spent"] = round(stats["total"], 2)
        customer["orders_count"] = stats["count"]
        customer["loyalty_points"] = stats["points"]
        customer["last_order_date"] = stats["last"].strftime("%Y-%m-%d") if stats["last"] else None

    users = [make_user(i + 1) for i in range(USER_COUNT)]

    dataset = {
        "customers": customers,
        "menu_items": menu_items,
        "orders": orders,
        "delivery_details": delivery_records,
        "users": users,
        "audit_logs": audit_logs,
    }

    # Sanity checks: ensure referenced menu items exist
    for order in dataset["orders"]:
        for item in order["items"]:
            if item["menu_item_id"] not in menu_index:
                item_info = random.choice(menu_items)
                item["menu_item_id"] = item_info["item_id"]
                item["name"] = item_info["name"]
                item["unit_price"] = float(item_info["price"])
                item["total_price"] = round(item["unit_price"] * item["quantity"], 2)

    return dataset


# ---------------------------------------------------------------------------
# Persistence Helpers
# ---------------------------------------------------------------------------

def write_json_files(dataset: Dict[str, List[Dict[str, object]]]) -> None:
    ensure_data_dir()
    for collection, records in dataset.items():
        output_path = DATA_DIR / f"{collection}.json"
        with output_path.open("w", encoding="utf-8") as fh:
            json.dump(records, fh, indent=2)
        print(f"💾 Wrote {len(records)} records to {output_path.as_posix()}")


def insert_into_mongo(dataset: Dict[str, List[Dict[str, object]]]) -> None:
    if MongoClient is None:
        raise RuntimeError("pymongo is required to insert data. Install it with `pip install pymongo`."
                           )

    mongo_uri = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError("Set MONGODB_URI (or MONGO_URI) in .env before using --insert")

    database_name = os.getenv("MONGODB_DATABASE") or os.getenv("DB_NAME") or DEFAULT_DB_NAME

    client = MongoClient(mongo_uri)
    db = client[database_name]

    for collection_name, records in dataset.items():
        collection: Collection = db[collection_name]
        collection.drop()
        if records:
            collection.insert_many(records)
        print(f"📥 Inserted {len(records)} documents into {database_name}.{collection_name}")

    client.close()


# ---------------------------------------------------------------------------
# CLI Interface
# ---------------------------------------------------------------------------

def parse_args(args: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a synthetic restaurant analytics dataset")
    parser.add_argument(
        "--insert",
        action="store_true",
        help="Insert the generated dataset into MongoDB using credentials from .env",
    )
    parser.add_argument(
        "--orders",
        type=int,
        default=ORDER_COUNT,
        help="Number of synthetic orders to generate (default: %(default)s)",
    )
    parser.add_argument(
        "--customers",
        type=int,
        default=CUSTOMER_COUNT,
        help="Number of synthetic customers to generate (default: %(default)s)",
    )
    parser.add_argument(
        "--menu-items",
        type=int,
        default=MENU_ITEM_COUNT,
        dest="menu_items",
        help="Number of menu items to include (default: %(default)s)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_SEED,
        help="Random seed for reproducible datasets (default: %(default)s)",
    )
    return parser.parse_args(args)


def main() -> None:
    args = parse_args()

    global RANDOM_SEED, ORDER_COUNT, CUSTOMER_COUNT, MENU_ITEM_COUNT
    RANDOM_SEED = args.seed
    ORDER_COUNT = max(1, args.orders)
    CUSTOMER_COUNT = max(1, args.customers)
    MENU_ITEM_COUNT = max(8, args.menu_items)

    dataset = generate_dataset()
    write_json_files(dataset)

    if args.insert:
        insert_into_mongo(dataset)

    print("\n🎉 Dataset generation complete!")
    if args.insert:
        print("   MongoDB has been populated with fresh demo data.")
    else:
        print("   Import JSON files with mongoimport or rerun with --insert.")


if __name__ == "__main__":
    main()
