####################################################################
# USER DEFINITIONS FOR OUTPUT
####################################################################

# The .csv output file from running model.py 
inputfile_1 = 'house1_data.csv'
inputfile_2 = 'house2_data.csv'
inputfile_3 = 'house3_data.csv'
inputfile_4 = 'house4_data.csv'

# the .csv file output after running learning_model.py
outputfile_1 = 'house1_data_OPT.csv'
outputfile_2 = 'house2_data_OPT.csv'
outputfile_3 = 'house3_data_OPT.csv'
outputfile_4 = 'house4_data_OPT.csv'

# Plot the predicted versus actual points
PLOTS = False

####################################################################
# END USER DEFINITIONS FOR OUTPUT
####################################################################

############################
### IMPORTS ###
import sklearn
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv



############################
### DATAFRAME SETUP

# used for dataframe output to csv
output_optimized_prices = []
features = [
    'datetime', 'energy_price',
    'battery_charge', 'household_demand',
    'solar_produced']

# Importing the datasets
filename_1 = '../model/' + inputfile_1
filename_2 = '../model/' + inputfile_2
filename_3 = '../model/' + inputfile_3
filename_4 = '../model/' + inputfile_4

dataset_1 = pd.read_csv(filename_1)
dataset_2 = pd.read_csv(filename_2)
dataset_3 = pd.read_csv(filename_3)
dataset_4 = pd.read_csv(filename_4)


datasets = [dataset_1, dataset_2, dataset_3, dataset_4]
outputfiles = [outputfile_1, outputfile_2, outputfile_3, outputfile_4]
idx = 0


############################
### RUNNING MODELS

# looping over each dataset tp train separate model for each house
for dataset in datasets:
    output_optimized_prices = []

    print('************** Running Model {0} **************\n'.format((idx+1)))
        
    X = dataset.iloc[:, 1:].values.astype(float)

    # prepare cross validation
    kfold = KFold(4, True, 1)

    # prepare for subplots
    fig, axs = plt.subplots(2,2)

    # enumerate splits
    k = 1
    for train, test in kfold.split(X):

        # split into training and testing
        X_train = X[train]
        X_test = X[test]

        Y_train = X_train[:,1]
        Y_test = X_test[:,1]

        yy = Y_test

        (n_train, d_tr) = X_train.shape
        (n_test, d_tt) = X_test.shape


        # Feature Scaling
        sc_X = StandardScaler()
        sc_Y = StandardScaler()

        X_train = sc_X.fit_transform(X_train)
        X_test = sc_X.fit_transform(X_test)
        Y_train = sc_Y.fit_transform(Y_train.reshape(-1, 1)).ravel()
        Y_test = sc_Y.fit_transform(Y_test.reshape(-1, 1)).ravel()

        # Fitting the Support Vector Regression Model to the dataset
        # Creating support vector regressor here
        regressor = SVR(kernel='rbf')
        regressor.fit(X_train, Y_train)

        # Predicting a new result
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


        print("FOLD {}\n".format(k))
        print("\tThe percentage of predicted points that were less than")
        print("\tthe actual price in {} test points was {:2.2%}\n".format(
            n_test, float(ccr/n_test)))

        # Visualising the Support Vector Regression results
        if PLOTS:
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


    # manipulate price
    new_data = [x / 100 for x in output_optimized_prices]

    # add extra row
    l = len(new_data) - 1
    new_data.append(new_data[l])

    (row, col) = dataset.shape
    row_d = dataset.iloc[row-1]
    dataset = dataset.append(row_d, ignore_index=True)

    # add new pricing to dataframe & convert it to a csv
    dataset["energy_price"] = new_data
    dataset.to_csv(outputfiles[idx], columns=features)

    print('************** Finished Model {0} **************\n'.format(idx+1))
    idx+=1

# actually show plots
if PLOTS:
    plt.show()

















            



