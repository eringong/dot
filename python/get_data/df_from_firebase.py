import json
import pandas as pd
import numpy as np
import requests
import datetime
import re
import dateutil
import os

#define where dataframes will be saved
out_path = "data/from_firebase/"
out_path_archive = "data/from_firebase/df_archive/"

#which beacons will be included in the training files and analysis
beacon_ids = ['11057',
    '12647',
    '12724',
    '13846',
    '19896',
    '28873',
    '31853',
    '34946',
    '38215',
    '38591',
    '40399',
    '47682']

def data_transform(v, J, test_round):
    visitor_history = J[v]
    reformatted_history = []

    # pull out relevant fields: visitor_id, timestamp, location, beacon readings
    for reading in visitor_history.values():
        reading_dict = {
            'visitor_history_id' : v,
            'timestamp' : re.findall('time=(.*?), visitor', reading)[0],
            'location' : re.findall('location=(.*?) end', reading)[0],
        }
        beacon_list = re.findall('CLBeacon \(.*?major:(\d+), minor:(\d+).*?, rssi:(-?\d+)\)', reading)
        for (major, minor, rssi) in beacon_list:
            reading_dict[major] = rssi
        reformatted_history.append(reading_dict)

    # transform reformatted_history into pandas dataframe D
    D = pd.DataFrame(reformatted_history)

    # turn timestamp into actual timestamp and sort by time
    D.timestamp = D.timestamp.str.strip('PST')
    D.timestamp = D.timestamp.apply(dateutil.parser.parse)
    D = D.sort(['timestamp'])

    # fill in any missing beacon columns from beacon_ids
    for b in beacon_ids:
        if b not in D.columns:
            D[b] = None

    # reformat rssi's
    for id in D[beacon_ids]:
        D[id].fillna(-500,inplace=True)
        D[id] = D[id].astype(int)
        D[id].replace(0,-100,inplace = True)
        D[id] = D[id]*-1

    # write D to csv file
    D.reset_index(inplace=True)
    D.drop('index',axis=1, inplace=True)
    if test_round = True:
        D.to_csv(out_path+"reshaped_rssi_"+"round_"+v+".csv", index=False)
        D.to_csv(save_directory+"reshaped_rssi_"+"round_"+v+".csv", index=False)
    else:
        D.to_csv(out_path+"reshaped_rssi_"+v+".csv", index=False)
        D.to_csv(save_directory+"reshaped_rssi_"+v+".csv", index=False)

# get data from firebase 
# call function data_transform to generate dataframes
# data_loc specifies which directories in Firebase to go to (dot/tests, dot/data, or both)
def main(data_loc, firebase_path):
    for x in data_loc:
        if x == "tests":
            test_round = True
        else:
            test_round = False
        result = requests.get(firebase_path+x+".json")
        J = result.json()
        visitor_history_keys = J.keys()
        for v in visitor_history_keys:
            data_transform(v, J, test_round)

if __name__ == "__main__":
    current_time = datetime.datetime.now().isoformat()
    os.mkdir(out_path_archive+str(current_time)+"/")
    save_directory = out_path_archive+str(current_time)+"/"
    firebase_path = "https://myfirebasepath.firebaseio.com"
    main(['data','tests'], firebase_path)