import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification # synthethic dataset

#generating linearly seperable dataset

X, y = make_classification(n_samples=1000, n_features=2, n_redundant=0,
                           n_informative=2, n_clusters_per_class=1, 
                           flip_y=0, class_sep=2, random_state=0)

y = np.where(y == 0,-1 , 1)
w = np.zeros(X.shape[1])
b = 0
lr = 0.1
epochs = 10

for epoch in range(epochs):
    for i in range(len(X)):
        if y[i] * (np.dot(X[i],w) + b)  <= 0:
            w += lr*y[i]*X[i]
            b += lr * y[i]
plt.figure(figsize=(8,6))
plt.scatter(X[:,0],X[:,1], c = y , cmap= 'bwr')
# np.linspace is used to generate an array of evenly spaced numbers over a specified interval
x1_vals = np.linspace(X[:,0].min(),X[:,0].max(),100)
x2_vals =  -(w[0]*x1_vals+b)/w[1]
plt.plot(x1_vals,x2_vals,'k--',label = 'decision boundry')
plt.title("Perceptron Decision Boundary")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
plt.legend()
plt.show()

print(w)
print(b)