from sklearn.ensemble  import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score

#load dataset
X,y = load_iris(return_X_y=True) # returns x features and y labels
#making a weak learner
dt = DecisionTreeClassifier(max_depth=1)
#adaboost with samme 
classifier = AdaBoostClassifier(estimator=dt,n_estimators=100,algorithm="SAMME")# number of weak learners
#base_estimator is a type of weak learner, if n_est = 50 , it will train 50 classifiers
classifier.fit(X,y)

y_pred = classifier.predict(X)
print("accuracy: ",accuracy_score(y,y_pred))

#now applying samme r 
classifier1 = AdaBoostClassifier(estimator=dt,n_estimators=100)
classifier1.fit(X,y)
y_predd = classifier1.predict(X)
print("accuracy: ",accuracy_score(y,y_predd))