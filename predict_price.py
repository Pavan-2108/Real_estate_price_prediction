from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor

from sklearn.linear_model import Ridge, BayesianRidge
from sklearn.ensemble import RandomForestRegressor

from sklearn import preprocessing
from sklearn.model_selection import train_test_split
import pickle
from sklearn.metrics import mean_squared_error
import pandas as pd
import numpy as np

data = pd.read_csv("dataset.csv")
data.head()

#City Code for Hyderabad as 0
df  = data.copy()
all_cities = df['City'].unique()

count = 0
for city in all_cities:
    print(city, ":", count)
    df.loc[df['City'] == city, 'City'] = count
    count += 1

df.head()


#Enumerate all Localities
all_locations = df['Locality'].unique()

count = 0
for locality in all_locations:
    print(locality, ":", count)
    df.loc[df['Locality'] == locality, 'Locality'] = count
    count += 1

df.head()

label_data = pd.DataFrame(df['Price'].copy())


train_data = df.drop(columns=['Price'])

X_train, X_test, y_train, y_test = train_test_split(train_data, label_data, test_size=0.1, random_state=42)

print("Training Model Random Forest Regressor")
# define model

model = RandomForestRegressor()

# fit model
model.fit(X_train, y_train)

print("Model Training Done")
# make a prediction
y_pred = model.predict(X_test)

print("Y Test:", y_test)
print("Y Pred:",y_pred)

mse = mean_squared_error(y_test, y_pred, multioutput='raw_values')
print("BRR MSE:", mse)


def predict_price(inp):
    # inp = [0,1,1600,0,3,2,1] 0, (0,1), sft,type,bhk, furnished,distnce
    inp = pd.DataFrame([inp])
    inp.head()
    op = model.predict(inp)

    print(op)
    return op[0]

if __name__ == "__main__":
    predict_price([0,1,1600,0,3,2,1])