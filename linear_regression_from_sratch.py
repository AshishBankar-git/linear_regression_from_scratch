import pandas as pd
import matplotlib.pyplot as plt

# Load data
data = pd.read_csv("dt.csv")


def loss_function(m, b, points):
    total_error = 0

    for i in range(len(points)):
        x = points.iloc[i]["StudyHours"]
        y = points.iloc[i]["Score"]

        total_error += (y - (m * x + b)) ** 2

    return total_error / len(points)


def gradient_descent(m_now, b_now, points, L):
    m_gradient = 0
    b_gradient = 0

    n = len(points)

    for i in range(n):
        x = points.iloc[i]["StudyHours"]
        y = points.iloc[i]["Score"]

        m_gradient += -(2 / n) * x * (y - (m_now * x + b_now))
        b_gradient += -(2 / n) * (y - (m_now * x + b_now))

    m = m_now - L * m_gradient
    b = b_now - L * b_gradient

    return m, b


m = 0
b = 0
L = 0.001
epochs = 1000

for i in range(epochs):

    if i % 100 == 0:
        print(f"Epoch {i}, Loss = {loss_function(m, b, data)}")

    m, b = gradient_descent(m, b, data, L)

print("\nSlope (m) =", m)
print("Intercept (b) =", b)

# Plot data
plt.scatter(data["StudyHours"], data["Score"], color="black")

x_values = data["StudyHours"]
y_values = [m * x + b for x in x_values]

plt.plot(x_values, y_values, color="red")

plt.xlabel("Study Hours")
plt.ylabel("Score")
plt.title("Study Hours vs Score")

plt.show()