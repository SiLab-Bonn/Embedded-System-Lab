import scipy
import numpy as np


e = np.e
tau = 0.1
# Peak amplitude in Volts
A = 10

# Set threshold in Volts
T = 6.7 

# If f(x) = epx(1) * A *  (x/tau) * exp(-x/tau)
# we solve f(x) > T for two branches of W.

first_tot = - tau * scipy.special.lambertw(- T/A*1/e, k=0)
second_tot = - tau *scipy.special.lambertw(-T/A*1/e, k=-1)

tot = second_tot - first_tot
print(np.real(tot))

# From here on it is only plotting
import matplotlib.pyplot as plt

x = np.linspace(0,np.max([5*tau,second_tot]), 100)
plt.plot(x, e * A * (x/tau) * np.exp(-x/tau))

T = np.ones(len(x)) * T
plt.plot(x, T)

plt.axvline(x=first_tot, color='green', label=f"{first_tot}")
plt.axvline(x=second_tot, color='purple', label=f"{second_tot}")
plt.legend(loc='upper right')

plt.show()

