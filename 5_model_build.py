"""
Build the prediction model
"""
import warnings
import pymongo
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC, LinearSVC
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn import metrics
import numpy as np
from collections import Counter
from sklearn.metrics import classification_report
import imblearn.over_sampling as imb


def all_list(arr):
    """
    Create the dictionary with a list
    [key:value] ——> [value:times]
    """
    result = {}
    for i in range(len(set(arr))):
        result[i] = arr.count(i)
    return result


def data_get(condition):
    """
    Get the data from database according to condition
    """
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']
    cursor = collection.find(condition)
    cited_years = []
    cited_nos = []
    citation_years = []
    locations = []
    for docu in cursor:
        cited_year = docu["cited_year"]
        cited_no = docu["cited_no"]
        citation_year = docu["citation_year"]
        location = docu["location_no"]
        for i in range(len(location)):
            cited_years.append(cited_year)
            citation_years.append(citation_year)
            cited_nos.append(cited_no)
        for loc in location:
            locations.append(loc)
    for i in range(len(locations)-1,-1,-1):
        if locations[i] == 0 or locations[i] == 4:
            locations.pop(i)
            cited_years.pop(i)
            citation_years.pop(i)
    print(all_list(locations))
    return citation_years, cited_years, locations


def data_remove(range_max):
    """
    Filter "highly methodological" papers
    """
    remove_list = []
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']
    for i in range(21, range_max+1):
        condition = {'$and': [{"cited_no": i}, {"location_no": {"$exists": True}}, {"location_no": {"$ne": None}}]}
        # condition = {'$and': [{"cited_no": i}, {"location_no": {'$exists': True}}]}
        cursor = collection.find(condition)
        locations = []
        for docu in cursor:
            location = docu["location_no"]
            for loc in location:
                locations.append(loc)
        loc_list = all_list(locations)
        for k, v in loc_list.items():
            if v/len(locations) >= 0.7:
                remove_list.append(i)
    return remove_list


def model_svm(X, y):
    """
    Build the model with SVM algorithm
    Input: X  Output: y
    """
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    # model = SVC(gamma= 0.001, C= 0.15)

    model = SVC(gamma= 0.001, class_weight='balanced', C=0.15, probability=True, decision_function_shape='ovr')
    score = cross_val_score(model, X, y, scoring='accuracy', cv=4)
    return round(score.mean(), 2)

    # learning curve
    # train_sizes, train_loss, test_loss = learning_curve(model, X, y, cv=10,
    # scoring='neg_mean_squared_error',train_sizes=[0.1, 0.25, 0.5, 0.75, 1])
    # train_loss_mean = -np.mean(train_loss, axis=1)
    # test_loss_mean = -np.mean(test_loss, axis=1)
    # plt.plot(train_sizes, train_loss_mean, 'o-', color="r",label="Training")
    # plt.plot(train_sizes, test_loss_mean, 'o-', color="g",label="Cross-validation")
    # plt.xlabel("Training examples")
    # plt.ylabel("Loss")
    # plt.legend(loc="best")
    # plt.show()


def parameter_tune(range_max):
    """
    Tune the parameters of the model
    range_max: determine how much data would be put to train the model
    """
    condition = {'$and': [{"cited_no": {"$gt": 20, "$lte": range_max}},
                          {"location_no": {"$exists": True}}, {"location_no": {"$ne": None}}]}
    year_diff, cited_years, locations = data_get(condition)
    X = list(zip(cited_years, year_diff))
    y = locations
    tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4], 'C': [1, 10, 100, 1000]},
                        {'kernel': ['linear'], 'C': [1, 0.1, 10, 0.15, 0.08]}]
    grid = GridSearchCV(SVC(class_weight='balanced'), tuned_parameters)
    grid.fit(X, y)
    print("The best parameters are %s with a score of %0.2f" % (grid.best_params_, grid.best_score_))


def model_score_visualize(range_max):
    """
    Visualize the data
    line chart ——> accuracy with the quantity of citation papers per cited paper
    bar chart ——> number of cited papers with the quantity of citation papers per cited paper
    stack graph ——> number of citation locations with the quantity of citation papers per cited paper
    range_max: determine how much data would be put to train the model
    """
    per_citation_num = []
    cited_num = []
    cv_score = []
    citation_loc = {}
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']
    highly_citeds = []
    for a in range(0, 260, 20):
        highly_cited = []
        for i in range(21, range_max+1):
            condition = {'$and': [{"cited_no": i},
                        {"location_no": {"$exists": True}},
                        {"location_no": {"$ne": None}},
                        {"cited_year": {"$gt": 1950}},
                        {'$where': "this.citation_year >= this.cited_year"}]}
            if collection.find(condition).count() >= a:
                highly_cited.append(i)
        print(a, ":", len(highly_cited))
        highly_citeds.append(highly_cited)
        condition = {'$and': [{"cited_no": {"$in": highly_cited}},
                              {"location_no": {"$exists": True}},
                              {"location_no":{"$ne": None}},
                              {"cited_year": {"$gt": 1950}},
                              {'$where': "this.citation_year >= this.cited_year"}]}
        citation_years, cited_years, locations = data_get(condition)
        for j in set(locations):
            citation_loc.setdefault(j, []).append(locations.count(j))
        X = list(zip(cited_years, citation_years))
        y = locations

        # oversampling to solve imbalanced problems
        # bal = imb.RandomOverSampler()
        # X, y = bal.fit_sample(X, y)

        model_score = model_svm(X, y)
        cited_num.append(len(highly_cited))
        per_citation_num.append(a)
        # score.append(model[0])
        cv_score.append(model_score)
    diff_cited = []
    for i in range(len(highly_citeds)-1):
        diff_cited.append([item for item in highly_citeds[i] if not item in highly_citeds[i + 1]])
    for i in diff_cited:
        for j in i:
            print(j)
            condition = {'$and': [{"cited_no": j}, {"location_no": {"$exists": True}}, {"location_no": {"$ne": None}}]}
            data_get(condition)
        print('-------------------------------------------')
    fig = plt.figure(figsize=(12, 12))
    ax1 = fig.add_subplot(221)
    ax1.plot(per_citation_num, cv_score, marker='o')
    plt.xticks(np.arange(0, 260, 20))
    for a, b in zip(per_citation_num, cv_score):
        plt.text(a, b, b, ha='center', va='bottom', fontsize=8)
    plt.grid(axis="y")
    plt.xlabel('Number of Citations per Cited paper')
    plt.ylabel('Score of Cross-Validation Accuracy')
    ax2 = fig.add_subplot(222)
    ax2.bar(per_citation_num, cited_num, width = 8)
    plt.xlabel('Number of Citations per Cited paper')
    plt.ylabel('Number of Cited papers')
    plt.xticks(np.arange(0, 260, 20))
    plt.grid(axis="y")
    for a, b in zip(per_citation_num, cited_num):
        plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=8)
    ax3 = fig.add_subplot(212)

    # 3 classes
    # y0 = np.array(citation_loc[1])
    # y1 = np.array(citation_loc[2])
    # y2 = np.array(citation_loc[3])
    # ax3.barh(per_citation_num, y0, color='red', height = 12, label='Introduction and Background')
    # ax3.barh(per_citation_num, y1, left=y0, color='green', height = 12, label='Materials and Methods')
    # ax3.barh(per_citation_num, y2, left=y0 + y1, color='blue', height = 12, label='Results and Discussion')

    # 5 classes
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

    plt.xticks(np.arange(0, 10000, 1000))
    plt.yticks(np.arange(0, 260, 20))
    plt.grid(axis="y")
    plt.xlabel('Number of Overall Citation Locations')
    plt.ylabel('Number of Citations per Cited paper')
    plt.legend()
    plt.show()


def pre_recall():
    """
    Print the classification report
    """
    warnings.filterwarnings("ignore")
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']
    citation_loc = {}
    highly_cited = []
    for i in range(21, 111):
        condition = {'$and': [{"cited_no": i},
                    {"location_no": {"$exists": True}},
                    {"location_no":{"$ne": None}},
                    {"cited_year": {"$gt": 1950}},
                    {'$where': "this.citation_year >= this.cited_year"}]}
        if collection.find(condition).count() >= 160:
            highly_cited.append(i)
    condition = {'$and': [{"cited_no": {"$in": highly_cited}},
                          {"location_no": {"$exists": True}},
                          {"location_no": {"$ne": None}},
                          {"cited_year": {"$gt": 1950}},
                          {'$where': "this.citation_year >= this.cited_year"}]}
    citation_years, cited_years, locations = data_get(condition)
    for j in set(locations):
        citation_loc.setdefault(j, []).append(locations.count(j))
    X = list(zip(cited_years, citation_years))
    y = locations
    ros = imb.RandomOverSampler(random_state=1)
    X, y = ros.fit_sample(X, y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)
    model = SVC(gamma=0.001, class_weight='balanced', C=0.15, probability=True, decision_function_shape='ovr')
    model.fit(X_train, y_train)
    # print(model.predict_proba(X_test))
    y_pred = model.predict(X_test)

    # 3 classes
    target_names = ["Introduction and Background", "Materials and Methods", "Results and Discussion"]

    # 5 classes
    # target_names = ["Others", "Introduction and Background",
    #            "Materials and Methods", "Results and Discussion", "Conclusion"]

    print(classification_report(y_test, y_pred, target_names=target_names))


"""
Main function
"""
# print(data_remove(110))
# parameter_tune(110)
# model_score_visualize(110)
pre_recall()
