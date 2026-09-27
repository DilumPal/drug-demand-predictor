import pandas as pd
import numpy as np
import os

def generate_data(num_records=10000, output_path="data/inventory_data.csv"):
    np.random.seed(42)
    
    # Base product catalog
    num_products = 200
    product_ids = [f"DRG{str(i).zfill(3)}" for i in range(1, num_products + 1)]
    categories = ["Antibiotic", "Painkiller", "Vitamin", "Vaccine", "Antihistamine", "Diabetes", "Cardiology"]
    suppliers = ["A", "B", "C", "D"]
    
    # Assign base attributes to products
    product_catalog = {}
    for pid in product_ids:
        product_catalog[pid] = {
            "category": np.random.choice(categories),
            "supplier_tier": np.random.choice(suppliers),
            "base_sales": np.random.uniform(5.0, 100.0),
            "lead_time_days": np.random.randint(2, 21),
            "supplier_reliability": np.random.uniform(0.70, 0.99)
        }
    
    records = []
    
    # Generate historical snapshots
    for _ in range(num_records):
        pid = np.random.choice(product_ids)
        cat = product_catalog[pid]
        
        # Vary the sales avg slightly per snapshot
        daily_sales_avg = max(1.0, np.random.normal(cat["base_sales"], cat["base_sales"] * 0.1))
        sales_std_dev = daily_sales_avg * np.random.uniform(0.1, 0.4)
        
        # Current stock can be healthy or low
        current_stock = max(0, np.random.normal(daily_sales_avg * 45, daily_sales_avg * 20))
        
        reorder_point = daily_sales_avg * cat["lead_time_days"] * 1.5
        seasonality_factor = np.random.uniform(0.8, 1.3)
        
        # Simulate next 30 days to determine target
        stock = current_stock
        stockout_occurred = 0
        
        # Did we already place an order? (Assume yes if below reorder point)
        days_until_delivery = cat["lead_time_days"] if stock <= reorder_point else -1
        
        for day in range(30):
            # Daily demand
            demand = max(0, np.random.normal(daily_sales_avg * seasonality_factor, sales_std_dev))
            stock -= demand
            
            # Receive order if delivery day
            if days_until_delivery == 0:
                # Based on supplier reliability, we might get the full order, or a delayed/partial one
                if np.random.rand() < cat["supplier_reliability"]:
                    stock += reorder_point * 2 # standard restock amount
                else:
                    # Delayed, push back delivery
                    days_until_delivery = np.random.randint(1, 5)
            
            if stock <= 0:
                stockout_occurred = 1
                break
                
            if days_until_delivery > 0:
                days_until_delivery -= 1
        
        records.append({
            "product_id": pid,
            "category": cat["category"],
            "supplier_tier": cat["supplier_tier"],
            "daily_sales_avg": round(daily_sales_avg, 1),
            "sales_std_dev": round(sales_std_dev, 1),
            "current_stock": int(current_stock),
            "lead_time_days": cat["lead_time_days"],
            "reorder_point": int(reorder_point),
            "supplier_reliability": round(cat["supplier_reliability"], 2),
            "seasonality_factor": round(seasonality_factor, 2),
            "out_of_stock_30d": stockout_occurred
        })
        
    df = pd.DataFrame(records)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_records} rows of data and saved to {output_path}")
    print(f"Out of stock cases: {df['out_of_stock_30d'].sum()} / {num_records} ({df['out_of_stock_30d'].mean():.1%})")

if __name__ == "__main__":
    generate_data()
