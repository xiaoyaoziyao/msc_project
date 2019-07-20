# -*- coding: utf-8 -*-
"""
Build the prediction model
"""

import pymongo
import numpy as np
import matplotlib.pyplot as plt 
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC 
from sklearn.cross_validation import cross_val_score
from sklearn.learning_curve import learning_curve
from sklearn.metrics import classification_report
from sklearn.model_selection import RandomizedSearchCV
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import GridSearchCV

def all_list(arr):
    result = {}
    for i in set(arr):
        result[i] = arr.count(i)
    return result


def data_get(condition):
    client = pymongo.MongoClient('localhost:27017',connect = True)
    db = client['msc_project']
    collection = db['citations']
    cursor = collection.find(condition)
    cited_years = []
    cited_nos = []
    pub_years = []
    year_diff = []
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
            year_diff.append(pub_year-cited_year)
        for loc in location:
            locations.append(loc)        
    print(all_list(locations))
    return (year_diff,cited_years,locations)


def data_remove(range_max):
    remove_list = []
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']
    for i in range(21, range_max+1):
        condition = {'$and': [{"cited_no": i}, {"location_num": {'$exists': True}}]}
        cursor = collection.find(condition)
        locations = []
        for docu in cursor:
            location = docu["location_num"]
            for loc in location:
                locations.append(loc)
        loc_list = all_list(locations)
        for k,v in loc_list.items():
            if v/len(locations) >= 0.7:
                remove_list.append(i)
    return remove_list


def model_svm(X,y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    model = SVC(gamma= 1e-3,C= 1)
    model.fit(X_train,y_train)
#    y_predict = model.predict(X_test)
#     print(round(model.score(X_test,y_test),2))
    score = cross_val_score(model,X,y,scoring='accuracy')
    # print(round(score.mean(),2))
    return (round(model.score(X_test,y_test),2),round(score.mean(),2))
    # train_sizes, train_loss, test_loss = learning_curve(model, X, y, cv=10, scoring='neg_mean_squared_error',train_sizes=[0.1, 0.25, 0.5, 0.75, 1])
    # train_loss_mean = -np.mean(train_loss, axis=1)
    # test_loss_mean = -np.mean(test_loss, axis=1)
    # plt.plot(train_sizes, train_loss_mean, 'o-', color="r",label="Training")
    # plt.plot(train_sizes, test_loss_mean, 'o-', color="g",label="Cross-validation")
    # plt.xlabel("Training examples")
    # plt.ylabel("Loss")
    # plt.legend(loc="best")
    # plt.show()

def parameter_tune(range_max):
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']
    condition = {'$and': [{"cited_no": {"$gt": 20, "$lte": range_max}}, {"location_num": {'$exists': True}}]}
    year_diff, cited_years, locations = data_get(condition)
    X = list(zip(cited_years, year_diff))
    y = locations
    tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                         'C': [1, 10, 100, 1000]},
                        {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]
    grid = GridSearchCV(SVC(), tuned_parameters, cv=5)
    grid.fit(X, y)
    print("The best parameters are %s with a score of %0.2f"% (grid.best_params_, grid.best_score_))


# def model_bayes(X,y):
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
#     model = GaussianNB()
#     model.fit(X_train,y_train)
# #    y_predict = model.predict(X_test)
#     print(model.score(X_test,y_test))
#     score = cross_val_score(model,X,y,scoring='accuracy')
#     print(score.mean())


def model_score_visualize(range_max):
    citation_num = []
    score = []
    cv_score = []
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']
    for a in range(22):
        highly_cited = []
        for i in range(21, range_max+1):
            condition = {'$and': [{"cited_no": i}, {"location_num": {'$exists': True}}]}
            if collection.find(condition).count() >= a * 10:
                highly_cited.append(i)
        print(highly_cited)
        condition = {'$and': [{"cited_no": {"$in": highly_cited}}, {"location_num": {'$exists': True}}]}
        year_diff, cited_years, locations = data_get(condition)
        X = list(zip(cited_years, year_diff))
        y = locations
        model = model_svm(X, y)
        citation_num.append(a * 10)
        score.append(model[0])
        cv_score.append(model[1])
    print(score)
    print(cv_score)
    plt.plot(citation_num, score, label='Accuracy')
    plt.plot(citation_num, cv_score, label='Cross-Validation Accuracy')
    plt.xlabel('Number of Citations')
    plt.ylabel('Score')
    plt.legend()
    plt.show()


# print(data_remove(110))
# parameter_tune(110)
model_score_visualize(110)


