import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
import re
import glob
import dot_classifier

#Generate accuracy score
def get_accuracy(actual,predicted):
    results = zip(actual, predicted)
    pred = [r[0]==r[1] for r in results]
    accuracy = sum(pred)*1./len(pred)
    return accuracy

accuracy_list = []
kn_accuracy_list = []
test_file_list = []
actual_list = []
hmm_pred_list = []

classifier_files = glob.glob("data/training/*.csv")
for test_file in classifier_files:
    
    #Create training df
    training_set = []
    for training_file in classifier_files:
        if test_file != training_file:
            training_set.append(training_file)
    train_df_long = pd.concat([pd.read_csv(f) for f in training_set], keys=training_set)
    train_df = dot_classifier.prep_file(train_df_long)
    train_df.dropna(inplace=True)

    #Create testing df
    test_df_long = pd.read_csv(test_file)
    test_df = dot_classifier.prep_file(test_df_long)
    test_df.dropna(inplace=True)

    X, Y = dot_classifier.get_x_y(train_df)
    X2, Y2 = dot_classifier.get_x_y(test_df)
    knc = dot_classifier.create_classifier(X, Y)

    Y2_prob = knc.predict_proba(X2)
    Y2hat = list(knc.predict(X2))
    results = zip(Y2, Y2hat)

    knc_result_df = dot_classifier.get_knc_result_df(X, Y, knc, train_df['timestamp'])
    hmm_result_df = dot_classifier.get_hmm_result_df(knc_result_df)

    clean_df = hmm_result_df.drop(hmm_result_df.tail(10).index)
    clean_df = hmm_result_df.drop(hmm_result_df.head(5).index)

    hmm_accuracy = get_accuracy(clean_df.y, clean_df.hmm_pred)
    k_neighbors_accuracy = get_accuracy(clean_df.y, clean_df.yhat)

    actual_temp = clean_df.y
    for a in actual_temp:
        actual_list.append(a)

    hmm_pred_temp = clean_df.hmm_pred
    for h in hmm_pred_temp:
        hmm_pred_list.append(h)

    test_file_list.append(test_file)
    accuracy_list.append(hmm_accuracy)
    kn_accuracy_list.append(k_neighbors_accuracy)

actual_series = pd.Series(actual_list)
pred_series = pd.Series(hmm_pred_list)
cm_all = pd.crosstab(actual_series,pred_series)
cm_all_perc = pd.crosstab(actual_series,pred_series).apply(lambda r: r*1.0/r.sum(), axis=1)
cm_all_perc['max'] = cm_all_perc.max()
rooms = cm_all_perc.max()
rooms.sort()

print np.mean(accuracy_list)
print np.mean(kn_accuracy_list)
print test_file_list
print rooms
print accuracy_list
print kn_accuracy_list
print cm_all
print cm_all_perc
