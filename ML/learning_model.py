#  1 Importing libraries
import sklearn
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv


# def run_model(dataset):

# dataset is a pandas df with 60 rows

# print(df.head)

output_optimized_prices = []
features = [
    'datetime', 'energy_price',
    'battery_charge', 'household_demand',
    'solar_produced']


# 2 Importing the dataset
# dataset = pd.read_csv('../model/testdata1.csv')
# dataset = pd.read_csv('../model/testdata_30day.csv')  # past simulation
# dataset = pd.read_csv('../model/testdata_1month.csv')  # new simulation
filename = '../model/house1_pre_covid.csv'

dataset = pd.read_csv(filename)
X = dataset.iloc[:, 1:].values.astype(float)

print(dataset)



# prepare cross validation
kfold = KFold(4, True, 1)

# prepare for plots
fig, axs = plt.subplots(2,2)

# enumerate splits
k = 1
for train, test in kfold.split(X):

    # if i == 0:
    #     r = 0
    #     c = 0
    # elif i == 1:
    #     r = 0
    #     c = 1
    # elif i == 2:
    #     r = 1
    #     c = 0
    # elif i == 3:
    #     r = 1
    #     c = 1
    
	# print('train: %s, test: %s' % (X[train], X[test]))


    # randomize rows before splitting
    # np.random.shuffle(X)
    # assign labels
    # Y = X[:, 1]

    X_train = X[train]
    X_test = X[test]

    Y_train = X_train[:,1]
    Y_test = X_test[:,1]

    yy = Y_test

    print(yy)


    # (n, dims) = X.shape

    # # split it up into training and testing (TENTATIVE FOR TESTING PURPOSES)
    # X_train = X[:int(np.floor(n*.8))]
    # X_test =  X[int(np.floor(n*.8)):]
    # Y_train = Y[:int(np.floor(n*.8))]
    # Y_test = Y[int(np.floor(n*.8)):]

    (n_train, d_tr) = X_train.shape
    (n_test, d_tt) = X_test.shape


    # print(X_train)
    # print(X_test)

    # print(X_train)

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
    # Y_labels = sc_Y.inverse_transform(Y_test)

    Y_labels = yy

    ccr = 0
    optimized_prices = []
    for (i, prediction) in enumerate(Y_pred):
        if (prediction < Y_labels[i] and prediction > 0):
            ccr += 1
            optimized_prices.append(prediction)
        else:
            optimized_prices.append(Y_labels[i])


    # print(len(optimized_prices))

    print("ccr is {} \n".format(ccr))

    print("\n\nThe percentage of predicted points that were less than")
    print("the actual price in {} test points was {:2.2%}\n".format(
        n_test, float(ccr/n_test)))

    # 6 Visualising the Support Vector Regression results
    # plt.scatter(, Y_labels, color='magenta')
    # plt.plot(Y_pred, color='green', linewidth=1)
    plt.subplot(2,2,k)

    plt.plot(Y_labels, color='blue', linewidth=.25)
    plt.plot(optimized_prices, color='red', linewidth=.25)

    title = 'fold {0}'.format(k)
    plt.title(title)
    plt.xlabel('time (s)')
    plt.ylabel('energy price ($)')
    plt.legend(['Labels', 'Optimized'])
   

    k+=1
    output_optimized_prices.extend(optimized_prices)


plt.show()


# print(dataset)

new_data = [x / 100 for x in output_optimized_prices]

# dataset = dataset.drop(["energy_price"], axis=1)
dataset["energy_price"] = new_data

dataset.to_csv('house1_pre_covid_OPT.csv', columns=features)

# print(dataset)


# print(Y_labels)

# plt.subplot(2,2,1)
# plt.plot(output_optimized_prices)

# plt.show()
















            



