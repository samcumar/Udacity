#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data, test_classifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedShuffleSplit, RandomizedSearchCV, train_test_split, cross_val_score
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix
import numpy as np

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi"... # You will need to use more features

features_list_no_eng =  ['poi', 'salary', 'total_payments', 'deferral_payments','bonus',
                  'restricted_stock_deferred', 'deferred_income', 'total_stock_value', 'expenses',
                  'exercised_stock_options', 'other', 'long_term_incentive', 'restricted_stock', 'director_fees',
                  'to_messages', 'from_poi_to_this_person', 'from_messages', 'from_this_person_to_poi',
                  'shared_receipt_with_poi']

features_list =  ['poi', 'salary', 'deferral_payments', 'total_payments', 'bonus',
                  'restricted_stock_deferred', 'deferred_income', 'total_stock_value',
                  'expenses', 'exercised_stock_options', 'other', 'long_term_incentive',
                  'restricted_stock', 'director_fees', 'to_messages', 'from_poi_to_this_person',
                  'from_messages', 'from_this_person_to_poi', 'shared_receipt_with_poi',
                  'sal_pkg_pct','pay_stock_ratio', 'ratio_to_msg', 'ratio_from_msg']

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers
TOTAL_element = data_dict.pop("TOTAL")
lockhart_element = data_dict.pop("LOCKHART EUGENE E")
agency_element = data_dict.pop("THE TRAVEL AGENCY IN THE PARK")

### Task 3: Create new feature(s)
for key in data_dict:
    bonus = data_dict[key]["bonus"]
    salary = data_dict[key]["salary"]
    total_payments = data_dict[key]["total_payments"]
    total_stock_value = data_dict[key]["total_stock_value"]
    to_messages = data_dict[key]["to_messages"]
    from_messages = data_dict[key]["from_messages"]
    from_poi = data_dict[key]["from_poi_to_this_person"]
    to_poi = data_dict[key]["from_this_person_to_poi"]

    if total_payments == "NaN":
        data_dict[key]["sal_pkg_pct"] = 0
        total_payments = 0
    else:
        if bonus == "NaN":
            bonus = 0
        if salary == "NaN":
            salary = 0
        data_dict[key]["sal_pkg_pct"] = round((float(bonus + salary)/total_payments), 4)

    if total_stock_value == "NaN":
        data_dict[key]["pay_stock_ratio"] = 0
    else:
        data_dict[key]["pay_stock_ratio"] = round((float(total_payments)/total_stock_value), 4)
    if from_poi == "NaN" or to_messages == "NaN":
        data_dict[key]["ratio_to_msg"] = 0
    else:
        data_dict[key]["ratio_to_msg"] = (float(from_poi)/to_messages)

    if to_poi == "Nan" or from_messages == "NaN":
        data_dict[key]["ratio_from_msg"] = 0
    else:
        data_dict[key]["ratio_from_msg"] = (float(to_poi)/from_messages)

### Store to my_dataset for easy export below.
my_dataset = data_dict


### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list_no_eng, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.
# from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV, StratifiedShuffleSplit
import numpy as np

select = SelectKBest(f_classif, k=13)
DTC = DecisionTreeClassifier(splitter="best", max_depth=3, min_samples_split=5, criterion="entropy", min_samples_leaf=7)
abclf = AdaBoostClassifier(base_estimator = DTC, algorithm="SAMME", n_estimators=56, learning_rate=0.0001)

clf = Pipeline([('select', select), ('clf', abclf)])
sss = StratifiedShuffleSplit(n_splits=10, random_state=42)

### Task 5: Tune your classifier to achieve better than .3 precision and recall
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info:
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html
from sklearn.model_selection import train_test_split
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=42)

# Example starting point. Try investigating other evaluation techniques!
print "Parameters found:"
print clf
print " "
print "features: "
print features_list_no_eng

clf.fit(features_train, labels_train)
prediction = clf.predict(features_test)

precision = precision_score(labels_test, prediction)
recall = recall_score(labels_test, prediction)
f1 = f1_score(labels_test, prediction)

print "Initial calculation of PRECISION: ", precision
print "Initial calculation of RECALL: ",recall
print "Initial calculation of F1: ",f1

def model_perf(estimator, X, y, cv):
    features = np.array(X)
    labels = np.array(y)
    # Using nested cross validation (cross_val_score) to calculate the f1, precision & recall
    f1_nested_scores = cross_val_score(estimator, features, labels, cv=cv, scoring="f1")
    f1_nested_scores_avg = f1_nested_scores.mean()
    print "************************************************************"
    print "Calculating nested f1 score using cross_val_score() function"
    print "************************************************************"
    print "Nested cross_val f1 scores array: ", f1_nested_scores
    print "cross_val f1 avg score: {:.3f}".format(f1_nested_scores_avg)
    print "\n"
    print "***************************************************"
    print "Performing Cross Validation split ie cv.split(X, y)"
    print "***************************************************"
    tn_sum = 0
    fn_sum = 0
    tp_sum = 0
    fp_sum = 0
    for train_idx, test_idx in cv.split(features, labels):
        f_train, f_test = features[train_idx], features[test_idx]
        l_train, l_test = labels[train_idx], labels[test_idx]
        estimator.fit(f_train, l_train)
        pred = estimator.predict(f_test)
        # using confusion matrix to find true -ve, false -ve, true +ve, false +ve
        tn, fp, fn, tp = confusion_matrix(pred, l_test).ravel()
        tn_sum = tn_sum + tn
        fn_sum = fn_sum + fn
        tp_sum = tp_sum + tp
        fp_sum = fp_sum + fp

    # Calculating the scores
    precision = 1.0 * tp_sum / (tp_sum + fp_sum)
    recall = 1.0 * tp_sum / (tp_sum + fn_sum)
    f1 = 2.0 * ((precision * recall) / (precision + recall))
    print "CV Split Precision: {}".format(precision)
    print "CV Split Recall: {}".format(recall)
    print "CV Split F1: {}".format(f1)
    print " "

# Evaluating the performance of the model
model_perf(clf, features, labels, sss)

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.
print "***************************"
print "udacity test - KFolds = 10:"
print "***************************"
test_classifier(clf, my_dataset, features_list_no_eng, 10)

print "******************************"
print "udacity test - KFolds = 1000:"
print "******************************"
test_classifier(clf, my_dataset, features_list_no_eng)


#dump_classifier_and_data(clf, my_dataset, features_list)
