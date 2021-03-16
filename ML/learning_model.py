# 1 Importing libraries
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# 2 Importing the dataset
dataset = pd.read_csv('../model/testdata1.csv')
X = dataset.iloc[:, 1:4].values.astype(float)
Y = dataset.iloc[:, 1].values.astype(float)

# 3 Feature Scaling
sc_X = StandardScaler()
sc_Y = StandardScaler()
X = sc_X.fit_transform(X)
Y = sc_Y.fit_transform(Y)

# 4 Fitting the Support Vector Regression Model to the dataset
# Creating support vector regressor here
regressor = SVR(kernel='rbf')
regressor.fit(X, Y)

# 5 Predicting a new result
Y_pred = regressor.predict('SOMETHING')

# 6 Visualising the Support Vector Regression results
plt.scatter(X, Y, color='magenta')
plt.plot(X, regressor.predict(X), color='green')
plt.title('MicroGrid Energy Support Vector Regression Model')
plt.xlabel('SOMETHING')
plt.ylabel('SOMETHING')
plt.show()
