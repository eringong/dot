import pandas as pd
import glob
import numpy as np

# r1_df = pd.read_csv("new_MAH_classifier/visitor_files/results_round_1.csv")
# r2_df = pd.read_csv("new_MAH_classifier/visitor_files/results_round_2.csv")

visitor_data_files = glob.glob("data/results/*.csv")
results_df = pd.DataFrame(columns = ['visitor_id','day','date','start_time','end_time','total_time'])
pathways_df = pd.DataFrame()

def sec_to_hrs (x):
	m,s = divmod(x,60)
	h,m = divmod(m,60)
	new_time = '%d:%02d:%02d' % (h,m,s)
	return new_time

# for v_file in visitor_data_files:
# 	visitor_id = v_file.split('results_ ')[1]
# 	visitor_id = int(visitor_id.split('.')[0])
# 	if r2_df['file_name'].apply(lambda x: x == visitor_id).any() == True:
# 		print v_file
# 	else:
# 		print 'invalid file'

area_list = []
time_list = [0,60,120,300,600,1200,1800,2700,3600,4500,5400,7200]
min_list = [0,1,2,5,10,20,30,45,60,75,90,120]
for v_file in visitor_data_files:

	visitor_id = v_file.split('results_ ')[1]
	visitor_id = int(visitor_id.split('.')[0])

	df = pd.read_csv(v_file)
	df['timestamp'] = pd.to_datetime(df['timestamp'])
	df = df.drop_duplicates(cols='timestamp')
	df['sec_count'] = df.index

	time_lapse_df = df.sec_count.isin(time_list)


# counts = pd.DataFrame(df['full_name'].value_counts(), columns=['num_unique'])
# df = df.merge(counts, left_on=['full_name'], right_index=True)

# How long was total visit
	start = df.timestamp.min().strftime("%H:%M:%S")
	end = df.timestamp.max().strftime("%H:%M:%S")
	total_time = df.timestamp.max()-df.timestamp.min()
	day = df.timestamp[0].strftime("%A")
	date = df.timestamp[0].date()

#How many times did they go to different areas

	df.set_index('timestamp', inplace=True)

# How many minutes did visitors spend in each area?

	area_seconds = df.hmm_pred.value_counts()
	area_seconds.name = visitor_id
	area_minutes = area_seconds.apply(lambda x: '%d:%02dmn' % (x / 60, x % 60))	
	area_normalize = df.hmm_pred.value_counts(normalize = True)

	area_list.append(area_seconds)

	s1 = df.hmm_pred.shift(1) != df.hmm_pred
	df['area_change'] = s1

	df['area'] = None
	df['area'] = df['hmm_pred'][df['area_change'] == True]


	path_df = pd.DataFrame(df.area.dropna(columns = ['location']))
	path_df['visitor_id'] = visitor_id
	# path_df['time_spent'] = None
	path_df['tvalue'] = path_df.index
	path_df['delta'] = ((path_df['tvalue'] - path_df['tvalue'].shift()).fillna(0)).shift(-1)
	path_df['delta_int'] = path_df['delta'] / np.timedelta64(1,'s')
	path_df.to_csv("result_march_"+str(visitor_id)+".csv", index=False)

	results_df.loc[len(results_df)+1] = {'visitor_id':visitor_id,'start_time':start,'end_time':end,
		'total_time':total_time,'day':day,'date':date}
	
	pathways_df = pathways_df.append(path_df)


	# print visitor_id
	# print start
	# print end
	# print total_time
	# print area_normalize
	# print area_minutes
	# print path_df

grouped = pathways_df.groupby(pathways_df.area)
for name, group in grouped:
    print(name)
    x = (group.delta_int<60).value_counts(normalize=True)
    # /group.delta_int.count()
    print x


area_all = pd.concat(area_list,axis = 1)
area_by_visitor = area_all.transpose()
results_df.set_index('visitor_id',inplace = True)
final_data = results_df.join(area_by_visitor, how='outer')
area_time = final_data.sum()
area_time.sort(ascending = False)
area_sum = area_time.apply(lambda x: sec_to_hrs(x))


# average time spent in museum
average_time = results_df.total_time.sum()/results_df.total_time.count()

# percent of total visitor time spent in each gallery
area_percent = area_time/sum(area_time)

# what percent of visitors go to the area
visit_area = final_data.count()/len(final_data.index)


final_data_2 = final_data.fillna(0)
final_data_2.drop(['day','date','start_time','end_time','total_time'],axis = 1,inplace = True)

# average minutes spent in each area (minutes spend in each area, averaged across visitors)
final_data_2.mean()
final_data_2.median()
final_data_2.max()

# average (mean or median?) percent of time spent in each area (percent of time spent in each room, averaged across visitors)
perc_area = final_data_2.apply(lambda x: x/x.sum(),axis=1)
perc_area.mean()
perc_area.median()
perc_area.max()

pathways_df.to_csv("result_pathway.csv", index = False)

