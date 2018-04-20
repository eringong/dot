import pandas as pd
import re
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

def prep_file(df):
    df = df[df.location != 'location not selected']
    df = df[df.location != 'none']

    # dropping beacons that were misplaced and shouldn't be considered
    if '19983' in df.columns:
        df.drop('19983',axis = 1, inplace=True)
    if '26848' in df.columns:
        df.drop('26848',axis = 1, inplace=True)
    if '56184' in df.columns:
        df.drop('56184',axis = 1, inplace=True)

    return df

def generate_training_df(classifier_files):
    train_df = pd.concat([pd.read_csv(f) for f in classifier_files], keys=classifier_files)
    train_df = prep_file(train_df)
    return train_df

def get_x_y(df):
    # select beacons to use, add column for each beacon that populates if no rssi is reported
    beacon_ids = [x for x in list(df) if re.match('\d{5}', x)!=None]
    beacon_ids_with_no_rssi = beacon_ids + [i+"_no_rssi" for i in beacon_ids]
    for i in beacon_ids:
        df[i+"_no_rssi"] = (df[i]==500).map(int)
        df[i][df[i]==500] = 100
        df[i+"_no_rssi"][df[i+"_no_rssi"]==1] = 100
    X = df[beacon_ids_with_no_rssi]
    Y = df['location']
    return X, Y

def create_classifier(X, Y):
    knc = KNeighborsClassifier(n_neighbors=10)
    return knc.fit(X,Y)

def viterbi(obs, states, start_p, trans_p, emit_p):
    V = [{}]
    path = {}
 
    for y in states:
        V[0][y] = np.log(start_p[y]) + np.log(emit_p[y][obs[0]])
        path[y] = [y]
 
    for t in range(1, len(obs)):
        V.append({})
        newpath = {}
 
        for y in states:
            (prob, state) = max((V[t-1][y0] + np.log(trans_p[y0][y]) + np.log(emit_p[y][obs[t]]), y0) for y0 in states)
            V[t][y] = prob
            newpath[y] = path[state] + [y]
 
        path = newpath

    n = 0 # if only one element is observed max is sought in the initialization values
    if len(obs) != 1:
        n = t
    (prob, state) = max((V[n][y], y) for y in states)
    return path

#Gen transition probabilities
def gen_transition_probs(legal_moves,states):
    transition_probability = {}
    for source_state in states:
        transition_probability[source_state] = dict([(dest_state, 0) for dest_state in states])
        for legal_place in legal_moves[source_state]:
            transition_probability[source_state][legal_place] = 0.002/(len(legal_moves[source_state])-1)
        transition_probability[source_state][source_state] = 0.998
    return transition_probability

#Gen emission probabilities
def gen_emission_probs(states):
    emission_probability = {}
    for source_state in states:
        emission_probability[source_state] = dict([(dest_state, 0.85/(len(states)-1)) for dest_state in states])
        emission_probability[source_state][source_state] = 0.15
    return emission_probability

def get_knc_result_df(X_test, Y_test, knc, timestamps):
    #Use the KNN model to predict probabilities for the testing set
    Y_test_prob = knc.predict_proba(X_test)
    #Get the most likely prediction for each second
    Y_test_hat = list(knc.predict(X_test))
    results = zip(Y_test, Y_test_hat)
    prob = Y_test_prob.max(axis=1)

    #Smooth them over a 10 second window
    Y_test_prob_smooth = pd.rolling_mean(Y_test_prob, 100)
    Y_test_prob_smooth = np.roll(Y_test_prob, shift=-50, axis=0)
    Y_test_hat_smooth = [knc.classes_[index] for index in list(Y_test_prob_smooth.argmax(axis=1))]

    result_df = pd.DataFrame({'y':Y_test, 'yhat':Y_test_hat, 'p':prob, 'yhat_smooth':Y_test_hat_smooth, 'timestamp':timestamps})

    cond2 = result_df['p'] > .50
    result_df['yhat_threshold'] = result_df['yhat'][cond2]
    result_df['yhat_threshold'].fillna(method='pad', inplace=True)
    result_df['yhat_threshold'].fillna('1_entrance', inplace = True)

    condition = result_df['p'] < .70
    result_df['p_threshold'] = result_df.p
    result_df.p_threshold[condition] = .2

    return result_df

def get_hmm_result_df(result_df):
    states = ("3_lobby","3_gal","3_sculpture", "3_2_stairs", "2_hist_old", "2_hist_new", "2_lobby", "2_gal_north", "2_gal_south", "2_1_stairs", "1_lobby_aud","1_class_lezin","1_entrance")
    legal_moves = {
        "3_lobby": ["3_lobby","3_gal","3_2_stairs"],
        "3_gal": ["3_gal","3_lobby","3_2_stairs"],
        "3_sculpture": ["3_sculpture","3_2_stairs"],
        "3_2_stairs": ["3_2_stairs","3_sculpture","3_lobby","3_gal","2_lobby","2_1_stairs"],
        "2_hist_old": ["2_hist_old","2_hist_new","2_lobby"],
        "2_hist_new": ["2_hist_new","2_hist_old","2_lobby"],
        "2_lobby": ["2_lobby","2_hist_old","2_hist_new","2_gal_north","2_gal_south","3_2_stairs","2_1_stairs"],
        "2_gal_north": ["2_gal_north","2_gal_south","2_lobby"],
        "2_gal_south": ["2_gal_north","2_gal_south","2_lobby"],
        "2_1_stairs": ["2_1_stairs","3_2_stairs","2_lobby","1_lobby_aud"],
        "1_lobby_aud": ["1_lobby_aud","2_1_stairs","1_class_lezin","1_entrance"],
        "1_class_lezin": ["1_class_lezin","1_lobby_aud"],
        "1_entrance": ["1_entrance","1_lobby_aud"]
    }
    observations = tuple(result_df.yhat.tolist())
    start_probability = {}
    for s in states:
        start_probability[s] = 1.0/(len(states))
    num_observations = list(range(result_df.yhat.count()))
    transition_probability = gen_transition_probs(legal_moves,states)
    emission_probability = gen_emission_probs(states)
    path = viterbi(observations, states, start_probability,transition_probability,emission_probability)
    result_df['hmm_pred'] = path['1_entrance']
    return result_df