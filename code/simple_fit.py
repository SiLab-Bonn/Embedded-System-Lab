import numpy as np
import matplotlib.pyplot as plt

# Generate some sample data
x = np.linspace(0, 10, 100)
y = 4 + 2 * x + np.random.randn(100)

# Fit a linear regression model
coefficients = np.polyfit(x, y, 1)
fit = np.poly1d(coefficients)

print(coefficients)

# Plot the data points and the fitted line
plt.scatter(x, y, label='Data')
plt.plot(x, fit(x), color='red', label='Fit')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend(['Data', f'Fit: y = {coefficients[0]:.2f} x + {coefficients[1]:.2f}'])
plt.show()