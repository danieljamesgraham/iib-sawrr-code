import numpy as np
import matplotlib.pyplot as plt

x = np.arange(0, 10.000001, 0.000001)
C = 0.875 / 0.32
D = (1.125/0.32 - 0.875/0.32) / 20
y = np.sin(2 * np.pi * (C + D * x) * x)
pos_sol = 1 / np.sqrt(2)
neg_sol = - pos_sol

last_val = 0
idt_pos_coordinates = []
idt_neg_coordinates = []

# for i in range(len(y)):
#     if (np.abs(y[i]-pos_sol) < 0.000008) and (np.abs(last_val-x[i]) > 0.001):
#         print(f"{round(100*x[i], 10)},30 {round(100*x[i], 10)},190")
#         last_val = x[i]
# print()

# for i in range(len(y)):
#     if (np.abs(y[i]-pos_sol) < 0.000008) and (np.abs(last_val-x[i]) > 0.001):
#         print(f"{round(100*x[i], 10)},30")
#         last_val = x[i]
# print()

# for i in range(len(y)):
#     if (np.abs(y[i]-pos_sol) < 0.000008) and (np.abs(last_val-x[i]) > 0.001):
#         print(f"{round(100*x[i], 10)},190")
#         last_val = x[i]
# print()

# for i in range(len(y)):
#     if (np.abs(y[i]-neg_sol) < 0.000008) and (np.abs(last_val-x[i]) > 0.001):
#         print(f"{round(100*x[i], 10)},10 {round(100*x[i], 10)},170")
#         last_val = x[i]
# print()

# for i in range(len(y)):
#     if (np.abs(y[i]-neg_sol) < 0.000008) and (np.abs(last_val-x[i]) > 0.001):
#         print(f"{round(100*x[i], 10)},10")
#         last_val = x[i]
# print()

# for i in range(len(y)):
#     if (np.abs(y[i]-neg_sol) < 0.000008) and (np.abs(last_val-x[i]) > 0.001):
#         print(f"{round(100*x[i], 10)},170")
#         last_val = x[i]
# print()

for i in range(len(y)):
    if (np.abs(y[i]-pos_sol) < 0.000008) and (np.abs(last_val-x[i]) > 0.001):
        idt_pos_coordinates.append(x[i])
        last_val = x[i]

for i in range(len(y)):
    if (np.abs(y[i]-neg_sol) < 0.000008) and (np.abs(last_val-x[i]) > 0.001):
        idt_neg_coordinates.append(x[i])
        last_val = x[i]

x_reduced = np.arange(0, 10.001, 0.001)
y_reduced = np.sin(2 * np.pi * (C + D * x_reduced) * x_reduced)

y_max = 1.05
y_min = -1.05
delta_y = y_max - y_min

plt.figure(figsize=(12, 5))
plt.plot(100*x_reduced, y_reduced, label='sin')
plt.axhline(1/np.sqrt(2), 0, 1000, color='orange', linestyle='--')
plt.axhline(-1/np.sqrt(2), 0, 1000, color='green', linestyle='--')
coordinates = []
for i in range(int(len(idt_pos_coordinates)/2)):
    plt.fill_betweenx([0, 1/np.sqrt(2)], 100*idt_pos_coordinates[2*i], 100*idt_pos_coordinates[2*i+1], color='orange', alpha=0.3)
for i in range(int(len(idt_neg_coordinates)/2)):
    plt.fill_betweenx([-1/np.sqrt(2), 0], 100*idt_neg_coordinates[2*i], 100*idt_neg_coordinates[2*i+1], color='green', alpha=0.3)
plt.title('')
plt.xlabel('')
plt.ylabel('')
plt.xlim(0, 1000)
plt.ylim(y_min, y_max)
# plt.legend()
# plt.grid(True)
plt.tight_layout()
plt.savefig("idt_coordinates.png", dpi=1000, format='png')
