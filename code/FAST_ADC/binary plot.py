import matplotlib.pyplot as plt
import numpy as np

# Define the array of integers
int_array =[0x44, 0x18, 0xA3, 0xad, 0xfa, 0xaa, 0x73, 0x3d]

# Assuming byte_array is your array of bytes
byte_array = np.array([int_array], dtype=np.uint8)

# Convert byte array to bit array
bit_array = np.unpackbits(byte_array)

# Create time array
time_array = np.arange(len(int_array))

plt.figure()
plt.xlabel('Time')
plt.ylabel('Channel')

for i in range(8):
  plt.step(time_array, i + 0.5*bit_array[i::8])
 
plt.show()