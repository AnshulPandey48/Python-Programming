import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier,plot_tree
from sklearn.datasets import load_iris
import matplotlib.pyplot as plt 
iris = load_iris()
classifier = DecisionTreeClassifier(
    max_depth= 3,
    min_samples_leaf= 3,
    random_state= 42,
)
classifier.fit(iris.data,iris.target)   
#plot tree
plt.figure(figsize=(17,12))
plot_tree(classifier,
          filled= True,
          feature_names= iris.feature_names,
          class_names=iris.target_names
         )
plt.show()



