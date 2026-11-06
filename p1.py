import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Machine learning imports
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# Set visual style
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 11, 'figure.titlesize': 14})


def generate_synthetic_transactions(num_customers=2000, days=730):
    """Generates a synthetic customer dataset with realistic purchase frequency and spend."""
    print(f"Generating synthetic transaction logs for {num_customers} customers over {days} days...")
    np.random.seed(42)
    
    start_date = datetime(2024, 1, 1)
    transaction_records = []
    
    for customer_id in range(10001, 10001 + num_customers):
        signup_offset = np.random.randint(0, int(days * 0.75))
        first_purchase_date = start_date + timedelta(days=signup_offset)
        
        segment_rand = np.random.rand()
        if segment_rand < 0.15:  # High-Value Loyal (15%)
            avg_frequency_days = np.random.randint(7, 21)
            avg_spend = np.random.lognormal(mean=4.5, sigma=0.4)
            lifespan_days = np.random.randint(400, 1000)
        elif segment_rand < 0.60:  # Moderate Repeat (45%)
            avg_frequency_days = np.random.randint(30, 90)
            avg_spend = np.random.lognormal(mean=3.5, sigma=0.3)
            lifespan_days = np.random.randint(180, 500)
        else:  # Low Value / One-Time Buyers (40%)
            avg_frequency_days = np.random.randint(120, 360)
            avg_spend = np.random.lognormal(mean=2.8, sigma=0.3)
            lifespan_days = np.random.randint(1, 90)
            
        customer_death_date = first_purchase_date + timedelta(days=lifespan_days)
        
        current_date = first_purchase_date
        while current_date <= (start_date + timedelta(days=days)) and current_date <= customer_death_date:
            amount = np.random.normal(loc=avg_spend, scale=avg_spend * 0.15)
            amount = max(5.0, round(amount, 2))
            
            transaction_records.append({
                "CustomerID": customer_id,
                "TransactionDate": current_date,
                "Amount": amount
            })
            
            days_to_next = np.random.exponential(scale=avg_frequency_days)
            current_date += timedelta(days=max(1, int(days_to_next)))
            
    df = pd.DataFrame(transaction_records)
    print(f"Data generation complete! Created {len(df)} transaction records.")
    return df


def build_rfm_features(df, calibration_end_date):
    """Transforms raw transaction logs into aggregated RFM features and target holdout values."""
    print(f"\nPerforming Calibration-Holdout split at: {calibration_end_date.strftime('%Y-%m-%d')}...")
    
    calibration_df = df[df['TransactionDate'] <= calibration_end_date].copy()
    holdout_df = df[df['TransactionDate'] > calibration_end_date].copy()
    
    cal_max_date = calibration_end_date
    
    rfm = calibration_df.groupby('CustomerID').agg(
        FirstPurchase=('TransactionDate', 'min'),
        LastPurchase=('TransactionDate', 'max'),
        Frequency=('TransactionDate', 'count'),
        TotalSpent=('Amount', 'sum'),
        AvgOrderValue=('Amount', 'mean')
    ).reset_index()
    
    rfm['Recency'] = (rfm['LastPurchase'] - rfm['FirstPurchase']).dt.days.clip(lower=0)
    rfm['T'] = (cal_max_date - rfm['FirstPurchase']).dt.days.clip(lower=0)
    rfm['PurchaseVelocity'] = rfm['Frequency'] / (rfm['T'] + 1)
    
    feature_cols = ['CustomerID', 'Frequency', 'Recency', 'T', 'TotalSpent', 'AvgOrderValue', 'PurchaseVelocity']
    features_df = rfm[feature_cols].copy()
    
    holdout_value = holdout_df.groupby('CustomerID').agg(
        HoldoutRevenue=('Amount', 'sum'),
        HoldoutTransactions=('TransactionDate', 'count')
    ).reset_index()
    
    master_df = pd.merge(features_df, holdout_value, on='CustomerID', how='left')
    master_df['HoldoutRevenue'] = master_df['HoldoutRevenue'].fillna(0.0)
    master_df['HoldoutTransactions'] = master_df['HoldoutTransactions'].fillna(0)
    master_df['IsActiveHoldout'] = (master_df['HoldoutTransactions'] > 0).astype(int)
    
    return master_df


def train_predictive_clv_models(data):
    """Trains regression models using log-transformed revenue targets for improved tail estimation."""
    print("\nPreparing ML dataset with log-transformed targets...")
    
    X = data[['Frequency', 'Recency', 'T', 'TotalSpent', 'AvgOrderValue', 'PurchaseVelocity']]
    y = data['HoldoutRevenue']
    
    # Log-transform target to handle extreme monetary skews
    y_log = np.log1p(y)
    
    X_train, X_test, y_train_log, y_test_log, y_train_orig, y_test_orig = train_test_split(
        X, y_log, y, test_size=0.25, random_state=42
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        "Ridge Regression": Ridge(alpha=1.0),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=150, max_depth=8, random_state=42)
    }
    
    trained_models = {}
    eval_results = {}
    
    for name, model in models.items():
        print(f"Training: {name}...")
        if "Ridge" in name:
            model.fit(X_train_scaled, y_train_log)
            preds_log = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_train_log)
            preds_log = model.predict(X_test)
            
        # Convert predictions back to original currency scale
        preds = np.expm1(np.clip(preds_log, a_min=0, a_max=None))
        
        mae = mean_absolute_error(y_test_orig, preds)
        rmse = np.sqrt(mean_squared_error(y_test_orig, preds))
        r2 = r2_score(y_test_orig, preds)
        
        eval_results[name] = {"MAE": mae, "RMSE": rmse, "R2": r2}
        trained_models[name] = model
        
        print(f" -> Metrics - MAE: ${mae:.2f} | RMSE: ${rmse:.2f} | R2: {r2:.4f}")
        
    return trained_models, eval_results, scaler, X, y


def run_business_analytics_and_plots(data, best_model, features, target):
    """Generates customer segments and exports analytical plots."""
    print("\nRunning business analytics and exporting charts...")
    os.makedirs('output_plots', exist_ok=True)
    
    # Predict in log space and reverse to monetary values
    data['Predicted_CLV_12M'] = np.expm1(np.clip(best_model.predict(features), 0, None))
    
    # Safe quantile dynamic binning
    labels = ['Bronze (Low)', 'Silver (Mid)', 'Gold (High)', 'Platinum (VIP)']
    try:
        data['CLV_Segment'] = pd.qcut(
            data['Predicted_CLV_12M'],
            q=4,
            labels=labels,
            duplicates='drop'
        )
    except ValueError:
        # Fallback if quantiles collapse due to zero-heavy predictions
        bins = [-np.inf, data['Predicted_CLV_12M'].quantile(0.5), 
                data['Predicted_CLV_12M'].quantile(0.75), 
                data['Predicted_CLV_12M'].quantile(0.9), np.inf]
        data['CLV_Segment'] = pd.cut(data['Predicted_CLV_12M'], bins=bins, labels=labels)

    segment_summary = data.groupby('CLV_Segment', observed=False).agg(
        CustomerCount=('CustomerID', 'count'),
        AvgHistoricalSpent=('TotalSpent', 'mean'),
        AvgExpectedValue=('Predicted_CLV_12M', 'mean'),
        TotalExpectedRevenue=('Predicted_CLV_12M', 'sum')
    ).reset_index()
    
    print("\n" + "="*50)
    print("           STRATEGIC CUSTOMER SEGMENTS")
    print("="*50)
    for idx, row in segment_summary.iterrows():
        print(f"Segment: {row['CLV_Segment']}")
        print(f"  Count: {row['CustomerCount']} customers ({row['CustomerCount']/len(data)*100:.1f}%)")
        print(f"  Avg Historical Spend: ${row['AvgHistoricalSpent']:.2f}")
        print(f"  Avg Predicted Value: ${row['AvgExpectedValue']:.2f}")
        print(f"  Aggregate Segment Yield: ${row['TotalExpectedRevenue']:.2f}\n")
    print("="*50)

    # 1. Feature Importance
    plt.figure(figsize=(10, 6))
    importances = best_model.feature_importances_
    indices = np.argsort(importances)[::-1]
    sns.barplot(x=importances[indices], y=features.columns[indices], palette="Blues_r")
    plt.title("Customer Features Driving Future Lifetime Value (12 Months)")
    plt.xlabel("Relative Importance Score")
    plt.tight_layout()
    plt.savefig('output_plots/1_feature_importance.png', dpi=300)
    plt.close()

    # 2. Distribution Plot
    plt.figure(figsize=(10, 6))
    sns.kdeplot(data=data, x='HoldoutRevenue', label='Actual Revenue', fill=True, alpha=0.3, color='blue')
    sns.kdeplot(data=data, x='Predicted_CLV_12M', label='Predicted CLV', fill=True, alpha=0.3, color='orange')
    plt.xlim(0, data['HoldoutRevenue'].quantile(0.97))
    plt.title("Distribution of Actual Holdout Revenue vs. Predicted 12M CLV")
    plt.xlabel("Value ($)")
    plt.ylabel("Density")
    plt.legend()
    plt.tight_layout()
    plt.savefig('output_plots/2_actual_vs_predicted_dist.png', dpi=300)
    plt.close()

    # 3. Dynamic Pie Chart
    plt.figure(figsize=(8, 8))
    n_bins = len(segment_summary)
    explode = tuple(0.1 if i == n_bins - 1 else 0.0 for i in range(n_bins))
    colors = sns.color_palette("copper", n_bins)
    
    plt.pie(
        segment_summary['TotalExpectedRevenue'], 
        labels=segment_summary['CLV_Segment'], 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=colors,
        explode=explode 
    )
    plt.title("Percentage of Future Revenue Sourced by Customer Segments")
    plt.tight_layout()
    plt.savefig('output_plots/3_revenue_contribution_pie.png', dpi=300)
    plt.close()
    
    print("Visualizations successfully saved inside 'output_plots/'.")


if __name__ == "__main__":
    print("="*60)
    print("      LAUNCHING CUSTOMER LIFETIME VALUE SYSTEM")
    print("="*60)
    
    csv_file = "customer_transactions.csv"
    if os.path.exists(csv_file):
        raw_transactions = pd.read_csv(csv_file)
        raw_transactions["TransactionDate"] = pd.to_datetime(raw_transactions["TransactionDate"])
    else:
        raw_transactions = generate_synthetic_transactions(num_customers=2000, days=730)
    
    calibration_end = datetime(2025, 6, 30)
    model_data = build_rfm_features(raw_transactions, calibration_end)
    
    trained_models, evaluation, scaler, X, y = train_predictive_clv_models(model_data)
    
    rf_model = trained_models["Random Forest Regressor"]
    run_business_analytics_and_plots(model_data, rf_model, X, y)
    
    print("\nExecution completed successfully!")
    print("="*60)       