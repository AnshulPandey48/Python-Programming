import numpy as np
import pandas as pd 
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,confusion_matrix,ConfusionMatrixDisplay
import matplotlib.pyplot as plt 
import seaborn as sns
from sklearn.datasets import load_iris

iris = load_iris()
X , y = iris.data,iris.target
#converting it into dataframe
df = pd.DataFrame(X,columns=iris.feature_names)
df['target'] = y
print(df['target'])

X_train , x_test , y_train , y_test = train_test_split(X,y,test_size=0.3,random_state=42,stratify=y)
print(df.head())

rf = RandomForestClassifier(
    n_estimators= 100,
    max_features= 'sqrt',
    bootstrap= True, # sampling with replacement
    random_state= 42
)

rf_model = rf.fit(X_train,y_train)
y_pred = rf_model.predict(x_test)
print("Acuracy : ",accuracy_score(y_test,y_pred))
cm = confusion_matrix(y_test,y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm,display_labels=iris.target_names)
disp.plot()
plt.show()
