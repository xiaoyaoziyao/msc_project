# -*- coding: utf-8 -*-
"""
Build the prediction model
"""

import pymongo
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC 
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RandomizedSearchCV
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import GridSearchCV
from sklearn.externals import joblib
from sklearn import metrics
import numpy as np


def data_get(condition):
    client = pymongo.MongoClient('localhost:27017',connect = True)
    db = client['msc_project']
    collection = db['citations']
    cursor = collection.find(condition)
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
    return (pub_years,cited_years,locations)


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


def model_svm(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    model = SVC(gamma= 1e-3,C= 1)
    model.fit(X_train, y_train)
    score = cross_val_score(model,X,y,scoring='accuracy')
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
    per_citation_num = []
    cited_num = []
    cv_score = []
    citation_loc = {}
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']
    for a in range(0, 275, 25):
        highly_cited = []
        for i in range(21, range_max+1):
            condition = {'$and': [{"cited_no": i}, {"location_num": {'$exists': True}}]}
            if collection.find(condition).count() >= a:
                highly_cited.append(i)
        print(a, ":", len(highly_cited))
        # print(highly_cited)
        condition = {'$and': [{"cited_no": {"$in": highly_cited}}, {"location_num": {'$exists': True}}]}
        pub_years, cited_years, locations = data_get(condition)
        for j in set(locations):
            citation_loc.setdefault(j, []).append(locations.count(j))
        X = list(zip(cited_years, pub_years))
        y = locations
        model = model_svm(X, y)
        cited_num.append(len(highly_cited))
        per_citation_num.append(a)
        # score.append(model[0])
        cv_score.append(model[1])
        if a == 250:
            joblib.dump(model, 'model.pkl')
    print(citation_loc)
    # print(score)
    print(cv_score)
    # plt.plot(citation_num, score, label='Accuracy')
    fig = plt.figure(figsize=(12, 12))
    ax1 = fig.add_subplot(221)
    ax1.plot(per_citation_num, cv_score, marker='o')
    for a, b in zip(per_citation_num, cv_score):
        plt.text(a, b, b, ha='center', va='bottom', fontsize = 12)
    plt.grid(axis="y")
    plt.xlabel('Number of Citations per Cited paper')
    plt.ylabel('Score of Cross-Validation Accuracy')
    ax2 = fig.add_subplot(222)
    ax2.bar(per_citation_num, cited_num, width = 12)
    plt.xlabel('Number of Citations per Cited paper')
    plt.ylabel('Number of Cited papers')
    plt.grid(axis="y")
    for a, b in zip(per_citation_num, cited_num):
        plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize = 12)
    ax3 = fig.add_subplot(212)
    y0 = np.array(citation_loc[0])
    y1 = np.array(citation_loc[1])
    y2 = np.array(citation_loc[2])
    y3 = np.array(citation_loc[3])
    y4 = np.array(citation_loc[4])
    ax3.barh(per_citation_num, y0, color='red', height = 12, label='Others')
    ax3.barh(per_citation_num, y1, left=y0, color='green', height = 12, label='Introduction and Background')
    ax3.barh(per_citation_num, y2, left=y0 + y1, color='blue', height = 12, label='Materials and Methods')
    ax3.barh(per_citation_num, y3, left=y0 + y1 + y2, color='orange', height = 12, label='Results and Discussion')
    ax3.barh(per_citation_num, y4, left=y0 + y1 + y2 + y3, color='purple', height = 12, label='Conclusion')
    plt.grid(axis="y")
    plt.xlabel('Number of Overall Citation Locations')
    plt.ylabel('Number of Citations per Cited paper')
    plt.legend()
    plt.show()


def model_pred():
    condition = {'$and': [{"location_num": {'$exists': True}}]}
    pub_years, cited_years, locations = data_get(condition)
    X = list(zip(cited_years, pub_years))
    y = locations
    model = joblib.load('model.pkl')
    y_pred = model.predict(X)
    print(metrics.precision_score(y, y_pred))


# print(data_remove(110))
# parameter_tune(110)
model_score_visualize(110)
# model_pred()

