# -*- coding: utf-8 -*-
"""
Build the prediction model
"""

import pymongo
import numpy as np
import matplotlib.pyplot as plt 
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC 
from sklearn.cross_validation import cross_val_score
from sklearn.learning_curve import learning_curve
from sklearn import metrics
def all_list(arr):
    result = {}
    for i in set(arr):
        result[i] = arr.count(i)
    return result

client = pymongo.MongoClient('localhost:27017',connect = True)
db = client['msc_project']
collection = db['citations']
cursor = collection.find({'$and':[{"cited_no":{'$gt':20}},
                                  {"location_num":{'$exists':True}}]})
cited_years = []
cited_nos = []
pub_years = []
locations = []
for docu in cursor:
    cited_year = docu["cited_year"]
    cited_no = docu["cited_no"]
    pub_year = docu["pub_year"]
    location = docu["location_num"]
    for i in range(len(location)):
        cited_years.append(cited_year)
        pub_years.append(pub_year)
        cited_nos.append(cited_no)
    for loc in location:
        locations.append(loc)
        
print(all_list(locations))

X = list(zip(cited_years,pub_years))
y = locations

train_sizes, train_loss, test_loss = learning_curve(
    SVC(gamma=0.001), X, y, cv=10, scoring='neg_mean_squared_error',
    train_sizes=[0.25, 0.5, 0.75, 1])
train_loss_mean = -np.mean(train_loss, axis=1)
test_loss_mean = -np.mean(test_loss, axis=1)
plt.plot(train_sizes, train_loss_mean, 'o-', color="r",
         label="Training")
plt.plot(train_sizes, test_loss_mean, 'o-', color="g",
        label="Cross-validation")
plt.xlabel("Training examples")
plt.ylabel("Loss")
plt.legend(loc="best")
plt.show()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
model = SVC()
model.fit(X_train,y_train)
y_predict = model.predict(X_test)

print("score:",model.score(X_test,y_test))

score = cross_val_score(model,X,y,scoring='accuracy')
print("cross_validation accuracy:",score.mean())