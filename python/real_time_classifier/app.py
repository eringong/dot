import tornado.ioloop
import tornado.web
import tornado.options
import re
import pandas as pd
import glob
import dot_classifier

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/cookie", MainHandler),
], debug=True, autoreload=True)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # get data and do a bunch of formatting to get it in the right shape for the classifier
        my_data = self.get_argument('data')
        reformatted_history = []
        reading_dict = {}
        beacon_list = re.findall('CLBeacon \(.*?major:(\d+), minor:(\d+).*?, rssi:(-?\d+)\)', my_data)
        for (major, minor, rssi) in beacon_list:
            reading_dict[major] = rssi
        reformatted_history.append(reading_dict)
        D = pd.DataFrame(reformatted_history)
        D['location'] = 'test_location'
        D['timestamp'] = 'test_time'
        D['visitor_history_id'] = 'test_id'
        col_ids = [x for x in list(D) if re.match('\d{5}', x)!=None]
        for id in col_ids:
            D[id].fillna(-500,inplace=True)
            D[id] = D[id].astype(int)
            D[id].replace(0,-100,inplace = True)
            D[id] = D[id]*-1

        # run through classifier
        X_test, Y_test = dot_classifier.get_x_y(D)
        Y_test_prob = knc.predict_proba(X_test)
        Y_test_hat = [knc.classes_[index] for index in list(Y_test_prob.argmax(axis=1))]
        result = str(Y_test_hat)

        # print results to screen for real-time display
        print '-'*80
        print my_data
        print result
        print '='*80
        self.write(result)

if __name__ == "__main__":
    classifier_files = glob.glob("data/training/*.csv")
    training_df = dot_classifier.generate_training_df(classifier_files)
    X_train, Y_train = dot_classifier.get_x_y(training_df)
    knc = dot_classifier.create_classifier(X_train, Y_train)
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()