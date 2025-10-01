"""
Scikit learn uses mccp minimal cost - complexity prunning
controlled by parameter cpp_alpha
"""
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier, plot_tree
import matplotlib.pyplot as plt

iris = load_iris()
classifier = DecisionTreeClassifier()
classifier.fit(iris.data,iris.target)

