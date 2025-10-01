import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression


a = fetch_california_housing()
dataset = pd.DataFrame(a.data) # coverting into dataframe
print(dataset)
#print(x.target)

dataset['price'] = a.target
#print(dataset)
# now marking independent and dependent features
x = dataset.iloc[:,:-1] # all rows , all columns except last one
y = dataset.iloc[:,-1] # all rows and culms except the last

# applying linear regression
lin_reg = LinearRegression()
mse = cross_val_score(lin_reg,x,y,scoring= 'neg_mean_squared_error',cv=5) # cv is no of times cross validation
print(mse)

# now improving this with ridge regularization