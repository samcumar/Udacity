README
======
This project was for the module "Introduction to Machine Learning". For this project, an algorithm was to be built and it was to identify Enron Employees who may have committed fraud based on the public Enron financial dataset.

Contents of the project is as follows:
* Directories adaboost, RandomForest & GNB
By default, the programs poi_id_Adaboost.py, poi_id_GNB.py and poi_id_RandomForest.py
will output the dataset, classifier and feature list to pickle files stored under
these directories. Under these directories, there is also a subdirectory called
"best_score". This subdirectory contains the pickle files that hold the
classifier models that produced the best evaluation output.

* model_perf.py
This program loads the pickle files that hold the classifier information of the
evaluated models that produced the best precision, recall and f1 scores. These
pickle files are stored under ./RandomForest/best_score, ./adaboost/best_score
 & ./GNB/best_score directories.

* poi_id_GNB.py, poi_id_Adaboost.py and poi_id_RandomForest.py
These files were used to evaluate and generate the models.

* poi_id.py
This program contains the classifier that produced the best score.

* poi_id_no_eng.py
This program contains the classifier documented in poi_id.py and runs it against
the features that contain no engineered features.
