import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import re
import glob
import dot_classifier

def get_test_id(file_name):
    test_id = file_name.split('rssi_')[1]
    test_id = test_id.split('.')[0]
    return test_id

# train classifier
classifier_files = glob.glob("data/training/*.csv")
training_df = dot_classifier.generate_training_df(classifier_files)
X_train, Y_train = dot_classifier.get_x_y(training_df)
knc = dot_classifier.create_classifier(X_train, Y_train)

# run new data through classifier
data_files = glob.glob("data/from_firebase/reshaped*")
for visitor_file in data_files:
    test_name = get_test_id(visitor_file)
    # create testing df
    test_df_long = pd.read_csv(visitor_file)
    test_df = dot_classifier.prep_file(test_df_long)
    test_df.sort('timestamp', inplace = True)
    # run classifier
    X_test, Y_test = dot_classifier.get_x_y(test_df)
    knc_result_df = dot_classifier.get_knc_result_df(X_test, Y_test, knc, test_df['timestamp'])
    hmm_result_df = dot_classifier.get_hmm_result_df(knc_result_df)
    # write to file
    hmm_result_df.to_csv("data/results/visitor_results_"+test_name+".csv", index=False)



