import pandas as pd
import numpy as np
import os

def generate_data(num_samples=10000, output_path="data/inventory_data.csv"):
    np.random.seed(42)
    
    categories = ["Antibiotic", "Painkiller", "Vitamin", "Vaccine", "Antihistamine"]
    suppliers = ["A", "B", "C", "D"]
    
    daily_sales_avg = np.random.uniform(5.0, 100.0, num_samples)
    current_stock = np.random.uniform(50, 5000, num_samples)
    lead_time_days = np.random.randint(2, 30, num_samples)
    category = np.random.choice(categories, num_samples)
    supplier_tier = np.random.choice(suppliers, num_samples)
    
    # Calculate target based on a realistic scenario:
    # Will stock reach zero within next 30 days?
    days_of_stock = current_stock / daily_sales_avg
    
    out_of_stock = np.zeros(num_samples, dtype=int)
    for i in range(num_samples):
        # We go out of stock if we run out within 30 days AND lead time is too long to save us
        if days_of_stock[i] < 30 and lead_time_days[i] >= days_of_stock[i]:
            out_of_stock[i] = 1
        # Add some random chance of stockout due to supply chain issues for bad suppliers
        elif supplier_tier[i] in ['C', 'D'] and np.random.rand() < 0.1:
            out_of_stock[i] = 1
            
    df = pd.DataFrame({
        "daily_sales_avg": daily_sales_avg,
        "current_stock": current_stock,
        "lead_time_days": lead_time_days,
        "category": category,
        "supplier_tier": supplier_tier,
        "out_of_stock": out_of_stock
    })
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_samples} rows of data and saved to {output_path}")
    print(f"Out of stock cases: {df['out_of_stock'].sum()} / {num_samples} ({df['out_of_stock'].mean():.1%})")

if __name__ == "__main__":
    generate_data()
