import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Lasso,Ridge

dataset = fetch_california_housing(as_frame=True)
df = dataset.frame
df['price'] = dataset.target
x = df.drop('MedHouseVal',axis = 1) # independent features all inputs
y = df['MedHouseVal'] # dependent , target features
print(df)

# applying training , testing data
x_train,x_test,y_train,y_test =  train_test_split(x,y,train_size=0.8,test_size=0.2)
lin_reg = LinearRegression()
lin_reg.fit(x_train,y_train)
sample = x_test.iloc[0].values.reshape(1,-1)
pred = lin_reg.predict(sample)
print("predicted value : ",pred[0])
print("True value: ",y_test.iloc[0])
mse = np.mean(cross_val_score(lin_reg,x,y,scoring='neg_mean_squared_error',cv= 5))
print(mse)
# now model is overfit , applying regulrization
lasso = Lasso(alpha = 0.1)
    
lasso.fit(x_train,y_train)
pred_lasso = lasso.predict(sample)
print(pred_lasso[0])