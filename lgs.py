
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

# 1. Create a sample dataset
data = {
    "mileage": [20000, 30000, 40000, 50000, 60000,
                70000, 80000, 90000, 100000, 110000],
    "year": [2023, 2022, 2021, 2020, 2019,
             2018, 2017, 2016, 2015, 2014],
    "engine_size": [1200, 1200, 1500, 1200, 1500,
                    1600, 1500, 1200, 1600, 1500],
    "price": [900000, 820000, 750000, 680000, 600000,
              520000, 450000, 380000, 320000, 270000]
}

df = pd.DataFrame(data)

# 2. Select features and target
X = df[["mileage", "year", "engine_size"]]
y = df["price"]

# 3. Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. Train Linear Regression model
model = LinearRegression()
model.fit(X_train, y_train)

# 5. Predict prices
y_pred = model.predict(X_test)

# 6. Evaluate model
print("Mean Absolute Error:", mean_absolute_error(y_test, y_pred))
print("R2 Score:", r2_score(y_test, y_pred))

# 7. Predict the price of a new car
new_car = pd.DataFrame({
    "mileage": [35000],
    "year": [2021],
    "engine_size": [1200]
})

predicted_price = model.predict(new_car)
print("Predicted Car Price: ₹", round(predicted_price[0], 2))

# 8. Visualize actual vs predicted prices
plt.scatter(y_test, y_pred)
plt.xlabel("Actual Price (₹)")
plt.ylabel("Predicted Price (₹)")
plt.title("Used Car Price Prediction")
plt.show()
