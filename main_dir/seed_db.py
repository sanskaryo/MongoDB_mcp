import pymongo
import datetime

def seed_data():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["restaurant_analytics"]
    
    # Collections: orders, customers, menu, inventory, staff, feedback
    
    # 1. Menu
    menu_items = [
        {"name": "Burger", "category": "Main", "price": 12.99, "cost": 4.50},
        {"name": "Pizza", "category": "Main", "price": 15.99, "cost": 5.00},
        {"name": "Salad", "category": "Starter", "price": 8.99, "cost": 2.00},
        {"name": "Pasta", "category": "Main", "price": 13.99, "cost": 4.00},
        {"name": "Coke", "category": "Beverage", "price": 2.99, "cost": 0.50},
        {"name": "Beer", "category": "Beverage", "price": 5.99, "cost": 2.00},
    ]
    db.menu.drop()
    db.menu.insert_many(menu_items)
    
    # 2. Customers
    customers = [
        {"name": "John Doe", "email": "john@example.com", "join_date": datetime.datetime(2023, 1, 15)},
        {"name": "Jane Smith", "email": "jane@example.com", "join_date": datetime.datetime(2023, 2, 20)},
    ]
    db.customers.drop()
    db.customers.insert_many(customers)
    
    # 3. Orders
    orders = [
        {
            "customer_id": "John Doe", 
            "items": [{"name": "Burger", "quantity": 2}, {"name": "Coke", "quantity": 2}],
            "total": 31.96,
            "timestamp": datetime.datetime(2023, 10, 1, 12, 30),
            "status": "completed"
        },
        {
            "customer_id": "Jane Smith", 
            "items": [{"name": "Pizza", "quantity": 1}, {"name": "Beer", "quantity": 1}],
            "total": 21.98,
            "timestamp": datetime.datetime(2023, 10, 1, 19, 00),
            "status": "completed"
        },
        {
            "customer_id": "John Doe", 
            "items": [{"name": "Pasta", "quantity": 1}, {"name": "Beer", "quantity": 2}],
            "total": 25.97,
            "timestamp": datetime.datetime(2023, 10, 2, 13, 00),
            "status": "completed"
        }
    ]
    db.orders.drop()
    db.orders.insert_many(orders)
    
    # 4. Inventory
    inventory = [
        {"item": "Burger Buns", "quantity": 100, "unit": "pcs", "reorder_level": 20},
        {"item": "Beef Patties", "quantity": 80, "unit": "pcs", "reorder_level": 15},
        {"item": "Lettuce", "quantity": 10, "unit": "kg", "reorder_level": 2},
        {"item": "Coke Cans", "quantity": 200, "unit": "pcs", "reorder_level": 50},
    ]
    db.inventory.drop()
    db.inventory.insert_many(inventory)
    
    # 5. Staff
    staff = [
        {"name": "Alice", "role": "Chef", "shift": "Morning"},
        {"name": "Bob", "role": "Waiter", "shift": "Evening"},
    ]
    db.staff.drop()
    db.staff.insert_many(staff)
    
    # 6. Feedback
    feedback = [
        {"customer_id": "John Doe", "rating": 5, "comment": "Great burger!", "timestamp": datetime.datetime(2023, 10, 1)},
        {"customer_id": "Jane Smith", "rating": 4, "comment": "Pizza was good, but a bit cold.", "timestamp": datetime.datetime(2023, 10, 1)},
    ]
    db.feedback.drop()
    db.feedback.insert_many(feedback)
    
    print("Sample data seeded successfully!")

if __name__ == "__main__":
    seed_data()
