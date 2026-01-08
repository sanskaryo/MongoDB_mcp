# Generate Charts - Create different types of data visualizations

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pymongo
import shutil
from dotenv import load_dotenv

# Set matplotlib backend for better compatibility
matplotlib.use('Agg')  # Use non-interactive backend for better compatibility

load_dotenv()

# Create charts directory
charts_dir = "charts"
if os.path.exists(charts_dir):
    # Delete existing charts folder and recreate
    shutil.rmtree(charts_dir)
    print(f"🗑️  Deleted existing {charts_dir} folder")

os.makedirs(charts_dir)
print(f"📁 Created new {charts_dir} folder")

# Connect to MongoDB
mongodb_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/hotel_management')
print(f"🔌 Connecting to MongoDB: {mongodb_uri}")
client = pymongo.MongoClient(mongodb_uri)
db = client['hotel_management']

orders = db.orders
print(f"📊 Connected to database. Order count: {orders.count_documents({})}")

print("Generating various chart types from MongoDB data...")

# 1. PIE CHART - Revenue by Customer Segment
print("1. Creating pie chart - Revenue by Customer Segment")
segment_pipeline = [
    {
        "$lookup": {
            "from": "customers",
            "localField": "customer_id",
            "foreignField": "_id",
            "as": "customer_info"
        }
    },
    {"$unwind": "$customer_info"},
    {"$match": {"order_status": "completed"}},
    {
        "$group": {
            "_id": "$customer_info.segment",
            "revenue": {"$sum": "$total_amount"}
        }
    }
]

segment_data = list(orders.aggregate(segment_pipeline))
print(f"   Found {len(segment_data)} segments")
if segment_data:
    labels = [item['_id'] for item in segment_data]
    sizes = [item['revenue'] for item in segment_data]
    
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title('Revenue Distribution by Customer Segment')
    plt.axis('equal')
    
    chart_path = os.path.join(charts_dir, 'pie_revenue_by_segment.png')
    try:
        plt.savefig(chart_path, bbox_inches='tight', dpi=300)
        print(f"   ✅ Saved: {chart_path}")
        print(f"   File exists: {os.path.exists(chart_path)}")
        if os.path.exists(chart_path):
            file_size = os.path.getsize(chart_path)
            print(f"   File size: {file_size} bytes")
    except Exception as e:
        print(f"   ❌ Error saving pie chart: {e}")
    plt.close()  # Close to prevent display issues
else:
    print("   ⚠️  No segment data found for pie chart")

# 2. BAR CHART - Order Count by Status
print("2. Creating bar chart - Order Count by Status")
status_pipeline = [
    {"$match": {"order_status": {"$ne": None}}},
    {"$group": {
        "_id": "$order_status",
        "count": {"$sum": 1},
        "avg_amount": {"$avg": "$total_amount"}
    }}
]

status_data = list(orders.aggregate(status_pipeline))
if status_data:
    statuses = [item['_id'] for item in status_data]
    counts = [item['count'] for item in status_data]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(statuses, counts, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    plt.title('Order Count by Status')
    plt.xlabel('Order Status')
    plt.ylabel('Number of Orders')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, 'bar_orders_by_status.png'), bbox_inches='tight', dpi=300)
    print("   ✅ Saved: charts/bar_orders_by_status.png")
    plt.close()

# 3. LINE CHART - Daily Revenue Trend
print("3. Creating line chart - Daily Revenue Trend")
daily_pipeline = [
    {"$match": {"order_status": "completed", "created_at": {"$ne": None}}},
    {"$addFields": {
        "order_date": {"$substr": ["$created_at", 0, 10]}  # Extract YYYY-MM-DD
    }},
    {"$group": {
        "_id": "$order_date",
        "daily_revenue": {"$sum": "$total_amount"},
        "daily_orders": {"$sum": 1}
    }},
    {"$sort": {"_id": 1}}
]

daily_data = list(orders.aggregate(daily_pipeline))
print(f"   Found {len(daily_data)} daily records")
if daily_data:
    dates = [item['_id'] for item in daily_data]
    revenues = [item['daily_revenue'] for item in daily_data]
    
    plt.figure(figsize=(14, 6))
    plt.plot(dates, revenues, marker='o', linewidth=2, markersize=6, color='#2E86AB')
    plt.title('Daily Revenue Trend Over Time')
    plt.xlabel('Date')
    plt.ylabel('Daily Revenue ($)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    chart_path = os.path.join(charts_dir, 'line_daily_revenue_trend.png')
    plt.savefig(chart_path, bbox_inches='tight', dpi=300)
    print(f"   ✅ Saved: {chart_path}")
    if os.path.exists(chart_path):
        file_size = os.path.getsize(chart_path)
        print(f"   File size: {file_size} bytes")
    plt.close()
else:
    print("   ⚠️  No daily data found for line chart")

# 4. SCATTER PLOT - Order Amount vs Customer Spending Pattern
print("4. Creating scatter plot - Order Amount vs Customer Total Spending")
customer_pipeline = [
    {"$lookup": {
        "from": "customers",
        "localField": "customer_id",
        "foreignField": "_id", 
        "as": "customer_info"
    }},
    {"$unwind": "$customer_info"},
    {"$match": {"order_status": "completed"}},
    {"$project": {
        "order_amount": "$total_amount",
        "customer_total": "$customer_info.total_spent",
        "customer_orders": "$customer_info.total_orders"
    }}
]

customer_data = list(orders.aggregate(customer_pipeline))
print(f"   Found {len(customer_data)} customer records")
if customer_data and len(customer_data) > 0:
    order_amounts = [item['order_amount'] for item in customer_data]
    customer_totals = [item['customer_total'] for item in customer_data]
    customer_orders = [item['customer_orders'] for item in customer_data]
    
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(customer_orders, customer_totals, c=order_amounts, 
                         s=60, alpha=0.7, cmap='viridis')
    plt.colorbar(scatter, label='Current Order Amount ($)')
    plt.title('Customer Spending Analysis')
    plt.xlabel('Total Orders by Customer')
    plt.ylabel('Total Amount Spent by Customer ($)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    chart_path = os.path.join(charts_dir, 'scatter_customer_analysis.png')
    plt.savefig(chart_path, bbox_inches='tight', dpi=300)
    print(f"   ✅ Saved: {chart_path}")
    if os.path.exists(chart_path):
        file_size = os.path.getsize(chart_path)
        print(f"   File size: {file_size} bytes")
    plt.close()
else:
    print("   ⚠️  No customer data found for scatter plot")

# 5. HISTOGRAM - Order Amount Distribution
print("5. Creating histogram - Order Amount Distribution")
amount_pipeline = [
    {"$match": {"order_status": "completed", "total_amount": {"$ne": None, "$gt": 0}}},
    {"$project": {"total_amount": 1}}
]

amount_data = list(orders.aggregate(amount_pipeline))
print(f"   Found {len(amount_data)} completed orders")
if amount_data:
    amounts = [item['total_amount'] for item in amount_data]
    
    plt.figure(figsize=(10, 6))
    plt.hist(amounts, bins=20, color='#FF6B6B', alpha=0.7, edgecolor='black')
    plt.title('Distribution of Order Amounts')
    plt.xlabel('Order Amount ($)')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3, axis='y')
    
    chart_path = os.path.join(charts_dir, 'histogram_order_amounts.png')
    plt.savefig(chart_path, bbox_inches='tight', dpi=300)
    print(f"   ✅ Saved: {chart_path}")
    if os.path.exists(chart_path):
        file_size = os.path.getsize(chart_path)
        print(f"   File size: {file_size} bytes")
    plt.close()
else:
    print("   ⚠️  No order amount data found for histogram")

# 6. HORIZONTAL BAR CHART - Top Customers by Revenue
print("6. Creating horizontal bar chart - Top 10 Customers by Revenue")
top_customers_pipeline = [
    {"$lookup": {
        "from": "customers",
        "localField": "customer_id",
        "foreignField": "_id", 
        "as": "customer_info"
    }},
    {"$unwind": "$customer_info"},
    {"$match": {"order_status": "completed"}},
    {"$group": {
        "_id": "$customer_info.name",
        "total_revenue": {"$sum": "$total_amount"}
    }},
    {"$sort": {"total_revenue": -1}},
    {"$limit": 10}
]

top_customers = list(orders.aggregate(top_customers_pipeline))
print(f"   Found {len(top_customers)} top customers")
if top_customers:
    customer_names = [item['_id'] for item in top_customers]
    customer_revenues = [item['total_revenue'] for item in top_customers]
    
    plt.figure(figsize=(10, 8))
    bars = plt.barh(customer_names, customer_revenues, color='#45B7D1')
    plt.title('Top 10 Customers by Total Revenue')
    plt.xlabel('Total Revenue ($)')
    plt.ylabel('Customer Name')
    
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width + 1, bar.get_y() + bar.get_height()/2,
                f'${width:.0f}', ha='left', va='center')
    
    plt.tight_layout()
    
    chart_path = os.path.join(charts_dir, 'horizontal_top_customers.png')
    plt.savefig(chart_path, bbox_inches='tight', dpi=300)
    print(f"   ✅ Saved: {chart_path}")
    if os.path.exists(chart_path):
        file_size = os.path.getsize(chart_path)
        print(f"   File size: {file_size} bytes")
    plt.close()
else:
    print("   ⚠️  No top customer data found")

# 7. STACKED BAR CHART - Monthly Orders by Status
print("7. Creating stacked bar chart - Monthly Orders by Status")
monthly_pipeline = [
    {"$match": {"created_at": {"$ne": None}, "order_status": {"$ne": None}}},
    {"$addFields": {
        "month": {"$substr": ["$created_at", 0, 7]}  # Extract YYYY-MM
    }},
    {"$group": {
        "_id": {"month": "$month", "status": "$order_status"},
        "count": {"$sum": 1}
    }},
    {"$sort": {"_id.month": 1}}
]

monthly_data = list(orders.aggregate(monthly_pipeline))
print(f"   Found {len(monthly_data)} monthly records")
if monthly_data:
    # Organize data for stacked bar chart
    months = sorted(set([item['_id']['month'] for item in monthly_data]))
    statuses = sorted(set([item['_id']['status'] for item in monthly_data]))
    
    # Create matrix
    data_matrix = {}
    for status in statuses:
        data_matrix[status] = []
        for month in months:
            count = next((item['count'] for item in monthly_data 
                         if item['_id']['month'] == month and item['_id']['status'] == status), 0)
            data_matrix[status].append(count)
    
    plt.figure(figsize=(14, 8))
    bottom = np.zeros(len(months))
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    for i, status in enumerate(statuses):
        plt.bar(months, data_matrix[status], bottom=bottom, 
                label=status, color=colors[i % len(colors)])
        bottom += np.array(data_matrix[status])
    
    plt.title('Monthly Orders by Status')
    plt.xlabel('Month')
    plt.ylabel('Number of Orders')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    chart_path = os.path.join(charts_dir, 'stacked_monthly_orders.png')
    plt.savefig(chart_path, bbox_inches='tight', dpi=300)
    print(f"   ✅ Saved: {chart_path}")
    if os.path.exists(chart_path):
        file_size = os.path.getsize(chart_path)
        print(f"   File size: {file_size} bytes")
    plt.close()
else:
    print("   ⚠️  No monthly data found for stacked bar chart")

# 8. BOX PLOT - Order Amount Distribution by Customer Segment
print("8. Creating box plot - Order Amount by Customer Segment")
segment_amounts_pipeline = [
    {"$lookup": {
        "from": "customers",
        "localField": "customer_id",
        "foreignField": "_id", 
        "as": "customer_info"
    }},
    {"$unwind": "$customer_info"},
    {"$match": {"order_status": "completed", "total_amount": {"$gt": 0}}},
    {"$project": {"customer_segment": "$customer_info.segment", "total_amount": 1}}
]

segment_amounts = list(orders.aggregate(segment_amounts_pipeline))
print(f"   Found {len(segment_amounts)} orders with segments")
if segment_amounts:
    # Group amounts by segment
    segment_dict = {}
    for item in segment_amounts:
        segment = item['customer_segment']
        if segment not in segment_dict:
            segment_dict[segment] = []
        segment_dict[segment].append(item['total_amount'])
    
    plt.figure(figsize=(10, 6))
    plt.boxplot([segment_dict[seg] for seg in segment_dict.keys()], 
                labels=list(segment_dict.keys()))
    plt.title('Order Amount Distribution by Customer Segment')
    plt.xlabel('Customer Segment')
    plt.ylabel('Order Amount ($)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    chart_path = os.path.join(charts_dir, 'boxplot_segments.png')
    plt.savefig(chart_path, bbox_inches='tight', dpi=300)
    print(f"   ✅ Saved: {chart_path}")
    if os.path.exists(chart_path):
        file_size = os.path.getsize(chart_path)
        print(f"   File size: {file_size} bytes")
    plt.close()
else:
    print("   ⚠️  No segment amount data found for box plot")

print("\n✅ All charts generated successfully!")
print(f"📊 Chart files created in {charts_dir}/ folder:")
print("   1. charts/pie_revenue_by_segment.png")
print("   2. charts/bar_orders_by_status.png") 
print("   3. charts/line_daily_revenue_trend.png")
print("   4. charts/scatter_customer_analysis.png")
print("   5. charts/histogram_order_amounts.png")
print("   6. charts/horizontal_top_customers.png")
print("   7. charts/stacked_monthly_orders.png")
print("   8. charts/boxplot_segments.png")
print(f"\n📁 To view charts:")
print(f"   - On Mac: open {charts_dir}/*.png")
print(f"   - On Windows: explorer {charts_dir}")
print(f"   - Or use: ls -la {charts_dir}/*.png to see file sizes")