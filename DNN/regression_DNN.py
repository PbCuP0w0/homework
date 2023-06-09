# -*- coding: utf-8 -*-
"""House_Rent(Regression)_ANN_Demo_for_class_2023_student_ver(Colab).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sdAN2R43g9LQotZBLhlhj7dkvs7H3XYg
"""

# Basic packages always been used
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Data scaling
from sklearn.preprocessing import MinMaxScaler

# Function for spilting training & testing data set
from sklearn.model_selection import train_test_split

# Tensorflow sequential models
from tensorflow import keras
from keras import backend as clear
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import BatchNormalization
from keras.optimizers import SGD
from keras.optimizers import Adam

# Functions for evaluation
from sklearn.metrics import mean_absolute_error #MAE
from sklearn.metrics import mean_squared_error #MSE,RMSE
from sklearn.metrics import mean_absolute_percentage_error #MAPE

from google.colab import drive
drive.mount('/content/drive')

"""# Note: Some metrics need to be defined manually"""

# Symmetric Mean Absolute Percentage Error (SMAPE)
def SMAPE_calulate(y_true, y_pred):
    n = len(y_true)
    SMAPE=(100 / n) * np.sum(2 * np.abs(y_pred - y_true) / (np.abs(y_pred) + np.abs(y_true)))
    return SMAPE

# Relative Absolute Error (RAE)
def RAE_calculate(y_true, y_pred):
    abs_errors = np.abs(y_true - y_pred)
    denominator = np.sum(np.abs(y_true - np.mean(y_true)))
    RAE=np.sum(abs_errors/denominator)
    return RAE

# Mean Relative Absolute Error (MRAE)
def MRAE_calculate(y_true, y_pred):
    n=len(y_true)
    abs_errors = np.abs(y_true - y_pred)
    denominator = np.sum(np.abs(y_true - np.mean(y_true)))
    RAE=np.sum(abs_errors/denominator)
    MRAE=RAE/n
    return MRAE

# Median Relative Absolute Error (MdRAE) comparing with benchmark
# Note: By default, the bench value is the mean of actual value
def MdRAE_calculate(y_true, y_pred, bench=None):
    if bench==None:
        bench=np.mean(y_true)
        MdRAE=np.median(np.abs(y_true - y_pred)/np.abs(y_true - bench))
        return MdRAE,bench
    else:
        MdRAE=np.median(np.abs(y_true - y_pred)/np.abs(y_true - bench))
        return MdRAE
    
# Relative Squared Error (RSE) & Root Relative Squared Error (RRSE)
def RSE_calculate(y_true, y_pred, Root=False):
    mse = np.mean((y_true - y_pred)**2)
    denominator = np.var(y_true)
    RSE=mse/denominator
    
    if Root==True:
        return np.sqrt(RSE)
    else:
        return RSE

#load data(sometimes need to use "/")
df = pd.read_csv('/content/drive/MyDrive/House_Rent_Dataset.csv')
# Colab
#df = pd.read_csv('')
df

"""# 1. Quick overview to get a grasp of the data set

key function: pd.info(); pd.astype(); describe(); pd.value_counts()
"""

# 1.1 Easiest way to check data type and if there are any missing value
df.info()

# 1.2 When using the describe function in default, pandas automatically selects the numerical columns
df.describe()

"""Note: Pclass is categorical data with dummies, so converting to correct data type is required"""

# 1.3 Using value_counts function to count frequency in categorical column
print(df[['Furnishing Status']].value_counts(sort=True))
print('+-----------------------+')
print(df[['City']].value_counts(sort=True))
print('+-----------------------+')

"""# 2. Data preprocessing

key function: pd.dropma() unique(); LabelEncoder(); pd.get_dummies
"""

#2.1 Using pd.get_dummies function to generate dummies
dummied_df=pd.get_dummies(df,columns=['Furnishing Status','City'])
dummied_df

"""Note: get_dummies function generates the onehotencode style dummies"""

# Export to CSV file Note: preset folder path is required
dummied_df.to_csv('/content/drive/MyDrive/House_Rent_Dataset.csv',index=False, header=True)
# Colab
#dummied_new_df.to_csv('House_Rent_dummied.csv',index=False, header=True)
print('Export complete...')

"""# 3. Set dependent variable(Y or target) & independent variable(X) """

#set x (make prediction) with minimax
x=dummied_df.drop(['Rent'],axis=1).copy()

#set y (want to predict)
y=dummied_df['Rent'].copy()

"""Note: Target variable Y does not need to be scaled, so we  need to separate dependent variabe and independent variables first

# 4. Data scaling with minimax technique

Key function: MinMaxScaler()
"""

#minimax scaling
MMscaler=MinMaxScaler(feature_range=(0, 1))
scaling=MMscaler.fit_transform(x)
scaled_x=pd.DataFrame(data=scaling)
scaled_x.columns=x.columns
scaled_x.head()

"""# 5. Spilt the data into train & test set

key function: train_test_split()

key parameters for train_test_spilt(): test_size; random_state
"""

#prepare dataset with scaling
#Split the data (split into 80% training data & 20% testing data) (lock seed)
x_train,x_test,y_train,y_test=train_test_split(scaled_x,y,test_size=0.2,random_state=44)

# 
print('Amount of training samples:',len(y_train))
print('+----------------------------------------+')
print('Amount of testing samples:',len(y_test))

"""# 6. Creating Net """

# Quick recap: Total of 12 features in the data set
scaled_x.head()

# Tips: Using shape to call the amount of features in the data set 
input_features=scaled_x.shape[1]
print('Amount of features:',input_features)

"""# Important: Define customized loss function (RMSE)"""

from keras.losses import mse
from keras.backend import sqrt

def my_RMSE(y_true, y_pred):
    return sqrt(mse(y_true, y_pred))

# Register custom object
#from keras.utils.generic_utils import get_custom_objects for pc
from tensorflow.keras.saving import get_custom_objects
get_custom_objects().update({'my_RMSE': my_RMSE})

"""Note: As far as I know when I'm preparing this in-class material, keras does not have a built-in RMSE function. Rumor has it that a RMSE function is hidden in the latest version, however it needs to be confirmed. For instance, defining RMSE ourself is not difficult, just don't forget to register our custom functions.

# Sequential style coding for creating net
"""

# 6.1 Create the model
clear.clear_session()
model=Sequential()
model.add(Dense(units=24, input_dim=12, activation='linear'))
# add 5 dense layers
model.add(Dense(units=30, activation='linear'))
model.add(Dense(units=36, activation='linear'))
model.add(Dropout(rate=0.3))
model.add(Dense(units=42, activation='linear'))
model.add(Dense(units=48, activation='linear'))
model.add(Dense(units=54, activation='linear'))
# Add dropout layer
model.add(Dropout(rate=0.3))

# Add 5 more dense layers
model.add(Dense(units=60, activation='linear'))
model.add(Dense(units=66, activation='linear'))
model.add(Dense(units=72, activation='linear'))
model.add(Dense(units=78, activation='linear'))
model.add(Dense(units=94, activation='linear'))

model.add(BatchNormalization())
model.add(Dense(units=1, activation='linear'))

# 6.8 Compile the defined Net
opt=Adam(learning_rate=0.006,beta_1=0.9)
model.compile(loss='my_RMSE', optimizer=opt, metrics=['mean_absolute_percentage_error'])

# Finally check the model 
model.summary()

# # 6.1 Create the model
# clear.clear_session()
# model=Sequential()

# # 6.2 Add input layer & first hidden layer
# model.add(Dense(units=24, input_dim=12, activation='relu'))

# # 6.3 Add second hidden layer
# model.add(Dense(units=48, activation='linear'))

# # 6.4 Add third hidden layer
# model.add(Dense(units=96, activation='relu'))

# # 6.5 Add output layer
# model.add(Dense(units=1, activation='linear'))

# # 6.6 Compile the defined Net
# #opt=SGD(learning_rate=0.001,momentum=0.5)
# opt=Adam(learning_rate=0.002,beta_1=0.95)
# model.compile(loss='my_RMSE', optimizer=opt, metrics=['mean_absolute_percentage_error'])

# # Finally check the model 
# model.summary()

"""Note: Remember to clear the session or else some of the left neurans may cause trouble while fitting

# 7. Fit the model

# Note: The validation set should be split manually
"""

# Important
x_training,x_validation,y_training,y_validation=train_test_split(x_train,y_train,test_size=0.2,random_state=444)

# 7.1 Store in the history for more useful information
history=model.fit(x_training, y_training, epochs=200, batch_size=64,verbose=1,validation_data=(x_validation, y_validation))

# Check the dictionary keys
modeling_result=history.history
modeling_result.keys()

# 7.2 Plot the history of training and validation
training_loss_values=modeling_result['loss']
val_loss_values=modeling_result['val_loss']
epochs=range(1,len(training_loss_values)+1)

plt.figure(figsize=(12,10),dpi=300)
plt.xlabel('Epochs',fontsize=20)
plt.ylabel('Loss (Root Mean Squared Error,RMSE)',fontsize=20)
plt.title('House Rent ANN training & validation of Loss result ',fontsize=20)

plt.plot(epochs, training_loss_values,marker='o',label='training Loss')
plt.plot(epochs, val_loss_values,marker='o',label='validation Loss')
plt.legend(loc=1,fontsize=24)
plt.show()

# 7.2 Plot the history of training and validation
training_acc_values=modeling_result['mean_absolute_percentage_error']
val_acc_values=modeling_result['val_mean_absolute_percentage_error']
epochs=range(1,len(training_acc_values)+1)

plt.figure(figsize=(12,10),dpi=300)
plt.xlabel('Epochs',fontsize=20)
plt.ylabel('Mean Absolute Percentage Error, MAPE',fontsize=20)
plt.title('House Rent ANN training & validation of MAPE result ',fontsize=20)

plt.plot(epochs, training_acc_values,marker='o',label='training MAPE')
plt.plot(epochs, val_acc_values,marker='o',label='validation MAPE')
plt.legend(loc=1,fontsize=24)
plt.show()

# 7.3 Save the trained model
model.save('D:/data_analysis/PyExport/House_Rent_ANN_trained_model.h5')
# Colab
#model.save('House_Rent_ANN_trained_model.h5')
print('Model has been saved...')

# 7.4 Restore the saved model for testing
ANN_model=keras.models.load_model('D:/data_analysis/PyExport/House_Rent_ANN_trained_model.h5')
# Colab
#ANN_model=keras.models.load_model('')
print('Model successfully loaded...')

"""# 8. Testing"""

# 8.1 Make prediction 
prediction=np.round(ANN_model.predict_on_batch(x_test),0)
prediction=prediction.astype('int')
pred_values=[]
for i in range(0,len(prediction)):
    value=prediction[i][0]
    pred_values.append(value)

"""Note: Since Rent value is integer, we need to transform the outputs and convert the data type."""

Results=pd.DataFrame({'Num':range(1,len(prediction)+1),'Y_true':y_test,'Predict':pred_values})
Results['abs Error']=np.abs(Results['Y_true']-Results['Predict'])
Results

# 8.2 Calculating the mertics
MAE=mean_absolute_error(y_test,pred_values)
MSE=mean_squared_error(y_test,pred_values,squared=True)
RMSE=mean_squared_error(y_test,pred_values,squared=False)
MAPE=mean_absolute_percentage_error(y_test,pred_values)
SMAPE=SMAPE_calulate(y_test,pred_values)
RAE=RAE_calculate(y_test,pred_values)
MRAE=MRAE_calculate(y_test,pred_values)
MdRAE=MdRAE_calculate(y_test,pred_values)
RSE=RSE_calculate(y_test,pred_values,Root=False)
RRSE=RSE_calculate(y_test,pred_values,Root=True)

print('MAE:',round(MAE,3))
print('MSE:',round(MSE,3))
print('RMSE:',round(RMSE,3))
print('MAPE:',round(MAPE*100,3),'%')
print('SMAPE:',round(SMAPE,3),'%')
print('RAE:',round(RAE,3))
print('MRAE:',MRAE)
print('MdRAE:',round(MdRAE[0],3),'bench:',round(MdRAE[1],3))
print('RSE:',round(RSE,3))
print('RRSE:',round(RRSE,3))

"""# Scatter plot for comparing true value & predicted value """

# Figure setting
plt.figure(figsize=(30,8),dpi=600)
plt.title('True value vs Predict value',weight='bold',fontsize=36)
plt.xlabel('Observations',fontsize=24,weight='bold')
plt.ylabel('Value',fontsize=24,weight='bold')

# Scatter plot
plt.scatter(Results.iloc[:,0],Results.iloc[:,1],color='blue',label='Y_true')
plt.scatter(Results.iloc[:,0],Results.iloc[:,2],color='red',label='Y_pred')

# Figure setting
plt.legend(loc=1,fontsize=24)
# Set x-axis to let the plot looks nice
plt.xlim(-50,1000)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.show()

"""# Actual by predicted plot"""

# Lock the scale of axis by Y_true
max_value=max(y_test)+100000
min_value=min(y_test)-100000

# Figure setting
plt.figure(figsize=(10,10),dpi=300)
plt.title('Actual by predicted plot',weight='bold',fontsize=24)
plt.xlabel('Y_true',fontsize=18,weight='bold')
plt.ylabel('Prediction',fontsize=18,weight='bold')

# Perfect model reference line
plt.plot([min_value,max_value], [min_value,max_value], linestyle='--',color='red')

# Actual by predicted plot
plt.scatter(Results.iloc[:,1],Results.iloc[:,2],marker='.',color='blue')

# Set the axis
plt.ylim(0,max_value)
plt.xlim(0,max_value)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.show()

max_value=max(y_test)+100000
min_value=min(y_test)-100000

plt.figure(figsize=(10,10),dpi=300)
plt.title('Actual by predicted plot',weight='bold',fontsize=24)
plt.xlabel('Y_true',fontsize=18,weight='bold')
plt.ylabel('Prediction',fontsize=18,weight='bold')
plt.plot([min_value,max_value], [min_value,max_value], linestyle='--',color='red')
plt.scatter(Results.iloc[:,1],Results.iloc[:,2],marker='.',color='blue')

#plt.legend(loc=1,fontsize=18)
plt.ylim(0,100000)
plt.xlim(0,100000)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.show()

