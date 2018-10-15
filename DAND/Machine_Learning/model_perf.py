#!/usr/bin/pickle

""" a basic script for importing student's POI identifier,
    and checking the results that they get from it 
 
    requires that the algorithm, dataset, and features list
    be written to my_classifier.pkl, my_dataset.pkl, and
    my_feature_list.pkl, respectively

    that process should happen at the end of poi_id.py
"""

import pickle
import sys
sys.path.append("../tools/")
from feature_format import featureFormat, targetFeatureSplit
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score, StratifiedShuffleSplit
import numpy as np

def dataset_summary(dataset):
    print "****************"
    print "Dataset Summary:"
    print "****************"
    print "Number of records in the dataset: ", len(dataset)
    print "Number of fields in the dataset: ", len(dataset["FASTOW ANDREW S"])
    print "Variables in dataset: ", dataset["FASTOW ANDREW S"].keys()
    poi = 0
    non_poi = 0
    for key in dataset:
        if dataset[key]["poi"] == 1:
            poi += 1
        else:
            non_poi +=1
    print "number of Persons of Interest: ", poi
    print "number of Non Persons of Interest: ", non_poi

def get_kbest_feat(clf, feature_list):
    print "******************"
    print "Feature list used:"
    print "******************"
    print feature_list
    select_stage = clf.named_steps["select"]
    feature_scores = ['%.2f' % elem for elem in select_stage.scores_]
    features_selected_tuple = [(feature_list[i + 1], feature_scores[i]) for i in select_stage.get_support(indices=True)]
    features_selected_tuple = sorted(features_selected_tuple, key=lambda feature: float(feature[1]), reverse=True)
    print "****************"
    print "SelectK summary:"
    print "****************"
    print "k value -> {}".format(len(features_selected_tuple))
    print "SelectKBest Feature Rank:"
    rank = 0
    for feat, score in features_selected_tuple:
        rank+=1
        print "Rank {0} -> Score: {2} - Feature: {1}".format(rank, feat, score)

def model_perf(estimator, feature_list, dataset, cv):
    data = featureFormat(dataset, feature_list, sort_keys=True)
    labels, features = targetFeatureSplit(data)
    features = np.array(features)
    labels = np.array(labels)
    # Using nested cross validation (cross_val_score) to calculate the nested f1 score
    f1_nested_scores = cross_val_score(estimator, features, labels, cv=cv, scoring="f1")
    f1_nested_scores_avg = f1_nested_scores.mean()
    print "************************************************************"
    print "Calculating nested f1 score using cross_val_score() function"
    print "************************************************************"
    print "Nested cross_val f1 scores array: ", f1_nested_scores
    print "cross_val f1 avg score: {:.3f}".format(f1_nested_scores_avg)
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
    precision = 1.0 * tp_sum / (tp_sum + fp_sum)
    recall = 1.0 * tp_sum / (tp_sum + fn_sum)
    f1 = 2.0 * ((precision * recall) / (precision + recall))
    print "CV Split Precision: {}".format(precision)
    print "CV Split Recall: {}".format(recall)
    print "CV Split F1: {}".format(f1)

def dump_classifier_and_data(clf, dataset, feature_list):
    with open(CLF_PICKLE_FILENAME, "w") as clf_outfile:
        pickle.dump(clf, clf_outfile)
    with open(DATASET_PICKLE_FILENAME, "w") as dataset_outfile:
        pickle.dump(dataset, dataset_outfile)
    with open(FEATURE_LIST_FILENAME, "w") as featurelist_outfile:
        pickle.dump(feature_list, featurelist_outfile)

def load_classifier_and_data(estimator):
    if estimator == "randomforest":
        CLF_PICKLE_FILENAME = "./RandomForest/best_score/my_classifier.pkl"
        DATASET_PICKLE_FILENAME = "./RandomForest/best_score/my_dataset.pkl"
        FEATURE_LIST_FILENAME = "./RandomForest/best_score/my_feature_list.pkl"
    elif estimator == "adaboost":
        CLF_PICKLE_FILENAME = "./adaboost/best_score/my_classifier.pkl"
        DATASET_PICKLE_FILENAME = "./adaboost/best_score/my_dataset.pkl"
        FEATURE_LIST_FILENAME = "./adaboost/best_score/my_feature_list.pkl"
    elif estimator == "gnb":
        CLF_PICKLE_FILENAME = "./GNB/best_score/my_classifier.pkl"
        DATASET_PICKLE_FILENAME = "./GNB/best_score/my_dataset.pkl"
        FEATURE_LIST_FILENAME = "./GNB/best_score/my_feature_list.pkl"

    with open(CLF_PICKLE_FILENAME, "r") as clf_infile:
        clf = pickle.load(clf_infile)
    with open(DATASET_PICKLE_FILENAME, "r") as dataset_infile:
        dataset = pickle.load(dataset_infile)
    with open(FEATURE_LIST_FILENAME, "r") as featurelist_infile:
        feature_list = pickle.load(featurelist_infile)

    return clf, dataset, feature_list

def main():
    #Cross validation algorithm
    sss = StratifiedShuffleSplit(n_splits=10, random_state=42)
    #Loading the AdaBoost classifier
    rcv_ab, dataset_ab, features_ab = load_classifier_and_data("adaboost")
    clf_ab = rcv_ab.best_estimator_
    # Loading the Guassian-Naive Bayes classifier
    gcv_gbn, dataset_gbn, features_gbn = load_classifier_and_data("gnb")
    clf_gbn = gcv_gbn.best_estimator_
    # Loading the RandomForest classifier
    rcv_rf, dataset_rf, features_rf = load_classifier_and_data("randomforest")
    clf_rf = rcv_rf.best_estimator_

    print "************************************************************"
    print "AdaBoost algorithm Validation scores - Best Performing model"
    print "************************************************************"
    print "Best Model found using Randomised Search CV:"
    print rcv_ab.best_estimator_
    print "Algorithm parameters:"
    print rcv_ab.best_params_
    dataset_summary(dataset_ab)
    get_kbest_feat(clf_ab, features_ab)
    model_perf(clf_ab, features_ab, dataset_ab, sss)
    print "\n"
    print "*****************************"
    print "RandomForest Classifier Model"
    print "*****************************"
    print "Best Model found using Randomised Search CV:"
    print rcv_rf.best_estimator_
    print "Algorithm parameters:"
    print rcv_rf.best_params_
    dataset_summary(dataset_rf)
    get_kbest_feat(clf_rf, features_rf)
    model_perf(clf_rf, features_rf, dataset_rf, sss)
    print "\n"
    print "**************************"
    print "Guassian-Naive Bayes Model"
    print "**************************"
    print "Best Model found using Grid Search CV:"
    print gcv_gbn.best_estimator_
    print "Algorithm parameters:"
    print gcv_gbn.best_params_
    dataset_summary(dataset_gbn)
    get_kbest_feat(clf_gbn, features_gbn)
    model_perf(clf_gbn, features_gbn, dataset_gbn, sss)
    print "\n"

if __name__ == '__main__':
    main()
