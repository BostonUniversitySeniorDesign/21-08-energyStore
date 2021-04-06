#  1 Importing libraries
import sklearn
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# 2 Importing the dataset
# dataset = pd.read_csv('../model/testdata1.csv')
# dataset = pd.read_csv('../model/testdata_30day.csv')  # past simulation
# dataset = pd.read_csv('../model/testdata_1month.csv') # new simulation
dataset = pd.read_csv('../model/new_testdata_6month.csv')
X = dataset.iloc[:, 1:].values.astype(float)

# randomize rows before splitting
np.random.shuffle(X)
# assign labels
Y = X[:, 1]

(n, dims) = X.shape

# split it up into training and testing (TENTATIVE FOR TESTING PURPOSES)
X_train = X[:int(np.floor(n*.8))]
X_test = X[int(np.floor(n*.8)):]
Y_train = Y[:int(np.floor(n*.8))]
Y_test = Y[int(np.floor(n*.8)):]

(n_train, d_tr) = X_train.shape
(n_test, d_tt) = X_test.shape

print(X_train)

# 3 Feature Scaling
sc_X = StandardScaler()
sc_Y = StandardScaler()

X_train = sc_X.fit_transform(X_train)
X_test = sc_X.fit_transform(X_test)
Y_train = sc_Y.fit_transform(Y_train.reshape(-1, 1)).ravel()
Y_test = sc_Y.fit_transform(Y_test.reshape(-1, 1)).ravel()

# # 4 Fitting the Support Vector Regression Model to the dataset
# # Creating support vector regressor here
regressor = SVR(kernel='rbf')
regressor.fit(X_train, Y_train)

# # 5 Predicting a new result
Y_pred = sc_Y.inverse_transform(regressor.predict(X_test))
Y_labels = sc_Y.inverse_transform(Y_test)

ccr = 0
for (i, prediction) in enumerate(Y_pred):
    if (prediction < Y_labels[i]):
        ccr += 1


print("\n\nThe percentage of predicted points that were less than")
print("the actual price in {} test points was {:2.2%}\n".format(
    n_test, float(ccr/n_test)))

# # 6 Visualising the Support Vector Regression results
# plt.scatter(, Y_labels, color='magenta')
plt.plot(Y_pred, color='green', linewidth=1)
plt.plot(Y_labels, color='blue', linewidth=.5)
plt.title('MicroGrid Energy Support Vector Regression Model')
plt.xlabel('time (s)')
plt.ylabel('energy price ($)')
plt.legend(['Predictions', 'Prices'])
plt.show()


'''
    Next Steps:
        



'''
