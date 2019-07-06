# -*- coding: utf-8 -*-
"""
Build the prediction model
"""

import pymongo
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC 
from sklearn.cross_validation import cross_val_score
from sklearn.learning_curve import learning_curve

X = list(zip(data['year_pub'],data['year_diff']))
y = data['location']

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
score = cross_val_score(model,X,y,scoring='accuracy')
model.fit(X_train,y_train)
print(score.mean())