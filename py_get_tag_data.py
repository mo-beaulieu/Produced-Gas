import pandas as pd

import sys  
import clr 

import numpy as np
import time
import datetime as dt
import dateutil.relativedelta
import calendar

#add SDK to path
sys.path.append(r'C:\Program Files (x86)\PIPC\AF\PublicAssemblies\4.0')    
clr.AddReference('OSIsoft.AFSDK')
rootDir = "C:\PG Gas Script Edits for MB"
#import key PI libraries
from OSIsoft.AF import *  
from OSIsoft.AF.PI import *  
from OSIsoft.AF.Asset import *  
from OSIsoft.AF.Data import *    
from OSIsoft.AF.Time import *  
from OSIsoft.AF.UnitsOfMeasure import * 


import dateutil.relativedelta

def get_PI_data(tag, col):
	print(tag)
	pt = PIPoint.FindPIPoint(piServer,tag.replace(" ",""))

	#pulls interpolated data between timerange and at given frequency defined by span
	interpolated = pt.InterpolatedValues(timeRange, span, "", False)

	#creates lists to store data and date associated with that PI tag
	data = []
	date = []     

	#appends data and date to lists 
	for event in interpolated:
		try:
			float(event.Value)
			tagVal = event.Value
			if col == 'esp_frequency':
				newVal = event.Value
				
			if col == 'temp_tubing':
				if tagVal >=0 and tagVal <= 300:
					newVal = event.Value
				else:
					newVal = None			
			else:
				newVal = tagVal
			data.append(newVal)
			date.append(event.Timestamp.LocalTime)
		except:
			data.append(None)
			date.append(event.Timestamp.LocalTime)
			continue

	#changes the date format/type
	try:
		date = [dt.datetime.strptime(str(date), '%m/%d/%Y %I:%M:%S %p') for date in date]
	except:
		date = [dt.datetime.strptime(str(date), '%Y-%m-%d %I:%M:%S %p') for date in date]
	return(data, date)


def function_get_pi_data_create_pickle_wells(pad):

	df_tags= pd.read_excel (rootDir + '/Tags.xlsx', sheet_name='tags_well')
	print(df_tags)
	df_tags = df_tags.loc[df_tags['pad']==pad]
	print(df_tags)
	cols = df_tags.iloc[:,2:].columns
	df_all_data = pd.DataFrame(columns=['pad', 'well', 'date', 'value', 'attribute'])

	for index, row in df_tags.iterrows():
		print(row['well'])
		for col in cols:
			tag = row[col]

			if tag != "NO TAG":

				tag_data_from_PI = get_PI_data(tag,col)
				date = tag_data_from_PI[1]
				values = tag_data_from_PI[0]

				count = len(date)

				temp_padList = [row['pad']]*count
				temp_wellList = [row['well']]*count
				temp_attributeList = [col]*count

				temp_df = pd.DataFrame(data={'pad':temp_padList, 'well':temp_wellList, 'date': date, 'value': values, 'attribute':temp_attributeList})
				df_all_data = pd.concat([df_all_data, temp_df])
				#df_all_data = df_all_data.append(temp_df)

	print(df_all_data)
	df_all_data = df_all_data.reset_index()
	df_all_data['value'] = pd.to_numeric(df_all_data['value'], errors='coerce')

	df_all_data.to_pickle(rootDir + "/prod_pickle_files/data_wells_" + pad + ".pkl")


def function_get_pi_data_create_pickle_pads(pad):

	df_tags= pd.read_excel (rootDir + '/Tags.xlsx', sheet_name='tags_pad')
	df_tags = df_tags.loc[df_tags['pad']==pad]
	cols = df_tags.iloc[:,1:].columns
	df_all_data = pd.DataFrame(columns=['pad', 'date', 'value', 'attribute'])

	for index, row in df_tags.iterrows():
		print(row['pad'])
		for col in cols:
			tag = row[col]

			if tag != "NO TAG":

				tag_data_from_PI = get_PI_data(tag,col)
				date = tag_data_from_PI[1]
				values = tag_data_from_PI[0]

				count = len(date)

				temp_padList = [row['pad']]*count
				temp_attributeList = [col]*count

				temp_df = pd.DataFrame(data={'pad':temp_padList, 'date': date, 'value': values, 'attribute':temp_attributeList})
				df_all_data = pd.concat([df_all_data, temp_df])
				#df_all_data = df_all_data.append(temp_df)

	print(df_all_data)
	df_all_data = df_all_data.reset_index()
	df_all_data['value'] = pd.to_numeric(df_all_data['value'], errors='coerce')

	df_all_data.to_pickle(rootDir + "/prod_pickle_files/data_pads_" + pad + ".pkl")

def function_get_pi_data_create_pickle_P9192 ():
	
	
	meaurement_points = {
		'p91': '91FI-14001/PV.CV',
		'p92': '92FI-1022/PV.CV',
	}


	parseTime = '.1h'
	span = AFTimeSpan.Parse(parseTime)

	#endDate = dt.date.today()
	startDate = (endDate - dateutil.relativedelta.relativedelta(days = 14))
	timeRange = AFTimeRange(str(startDate), str(endDate))

	piServers = PIServers()    
	piServer = piServers["firebagpi"]

	df_P9192_data = pd.DataFrame()
	tagCount = 0
	for key in meaurement_points:
		print(key)
		print(meaurement_points[key])
		tag = meaurement_points[key]

		print(tag)
		pt = PIPoint.FindPIPoint(piServer,tag.replace(" ",""))

		#pulls interpolated data between timerange and at given frequency defined by span
		interpolated = pt.InterpolatedValues(timeRange, span, "", False)

		#creates lists to store data and date associated with that PI tag
		data = []
		date = []     

		#appends data and date to lists 
		for event in interpolated:
			try:
				float(event.Value)
				tagVal = event.Value
				data.append(tagVal)
				date.append(event.Timestamp.LocalTime)
			except:
				data.append(None)
				date.append(event.Timestamp.LocalTime)
				continue

		#changes the date format/type
		try:
			date = [dt.datetime.strptime(str(date), '%m/%d/%Y %I:%M:%S %p') for date in date]
		except:
			date = [dt.datetime.strptime(str(date), '%Y-%m-%d %I:%M:%S %p') for date in date]
		
		if tagCount ==0:
			df_P9192_data['date'] = date
			df_P9192_data[key] = data
		else:
			df_P9192_data[key] = data

		tagCount = tagCount+1

	df_P9192_data['gas_sum'] = df_P9192_data[['p91', 'p92']].sum(axis=1)

	countOfVals = len(df_P9192_data['gas_sum'].tolist())
	temp_padList = ['P91_92'] * countOfVals
	temp_attributeList = ['produced_gas']* countOfVals

	df_to_pickle = pd.DataFrame(data={'pad':temp_padList, 'date': df_P9192_data['date'].tolist(), 'value': df_P9192_data['gas_sum'].tolist(), 'attribute':temp_attributeList})
	df_to_pickle.to_pickle(rootDir + "/prod_pickle_files/data_pads_P91_92.pkl")


def create_sru_plot_png ():

	parseTime = '.1h'
	span = AFTimeSpan.Parse(parseTime)

	#endDate = dt.date.today()
	#endDate = dt.datetime(2022, 4, 14, 6, 45, 0, 0)
	startDate = (endDate - dateutil.relativedelta.relativedelta(days = 14))
	timeRange = AFTimeRange(str(startDate), str(endDate))

	piServers = PIServers()    
	piServer = piServers["firebagpi"]

	df_sru_plot_data = pd.DataFrame()

	sru_plot_tags_dict = {
		'plant_1': '93FI-81150/PV.CV',
		'plant_2': '99FI-40559/ALM1/PV.CV',
		'plant_3': '93FI-22203/ALM1/PV.CV',
		'plant_4': '92FI-2020/PV.CV',
		'plant_5': '91FI-47408/PV.CV',
		'plant_6': '91FI-13001/PV.CV',
		'plant_7': '91FI-27408/PV.CV',
		'sru': '91FC-1019/PID1/PV.CV',
		'field_emul': 'FB_TOTAL_EMULSION_CORRECTED',
	}
	
	tagCount = 0
	for key in sru_plot_tags_dict:
		print(key)
		print(sru_plot_tags_dict[key])
		tag = sru_plot_tags_dict[key]



		print(tag)
		pt = PIPoint.FindPIPoint(piServer,tag.replace(" ",""))

		#pulls interpolated data between timerange and at given frequency defined by span
		interpolated = pt.InterpolatedValues(timeRange, span, "", False)

		#creates lists to store data and date associated with that PI tag
		data = []
		date = []     

		#appends data and date to lists 
		for event in interpolated:
			try:
				float(event.Value)
				tagVal = event.Value
				data.append(tagVal)
				date.append(event.Timestamp.LocalTime)
			except:
				data.append(None)
				date.append(event.Timestamp.LocalTime)
				continue

		#changes the date format/type
		try:
			date = [dt.datetime.strptime(str(date), '%m/%d/%Y %I:%M:%S %p') for date in date]
		except:
			date = [dt.datetime.strptime(str(date), '%Y-%m-%d %I:%M:%S %p') for date in date]
		
		if tagCount ==0:
			df_sru_plot_data['date'] = date
			df_sru_plot_data[key] = data
		else:
			df_sru_plot_data[key] = data

		tagCount = tagCount+1

	df_sru_plot_data['plant_sum'] = df_sru_plot_data[['plant_1', 'plant_2', 'plant_3', 'plant_4', 'plant_5', 'plant_6', 'plant_7']].sum(axis=1)
	df_sru_plot_data['res_gas'] = df_sru_plot_data['sru'] - df_sru_plot_data['plant_sum']

	return df_sru_plot_data
		
def create_cut_wells_status_data ():

	df_well_info= pd.read_excel (rootDir + '/Tags.xlsx', sheet_name='high_gas_offenders')
	print(df_well_info)


	parseTime = '.1h'
	span = AFTimeSpan.Parse(parseTime)

	#endDate = dt.date.today()
	startDate = endDate 
	timeRange = AFTimeRange(str(startDate), str(endDate))

	piServers = PIServers()    
	piServer = piServers["firebagpi"]


	df_all_data = pd.DataFrame(columns=['well', 'low_freq', 'high_freq', 'current_freq'])

	for index, row in df_well_info.iterrows():
		well = row['well']
		esp_freq_tag = row['esp_freq_tag']
		print(esp_freq_tag)

		df_temp = pd.DataFrame()
		df_temp['well'] = well

		pt = PIPoint.FindPIPoint(piServer,esp_freq_tag.replace(" ",""))

		interpolated = pt.InterpolatedValues(timeRange, span, "", False)

		#creates lists to store data associated with that PI tag
		data = []    
		#appends data  to lists 
		for event in interpolated:
			try:
				float(event.Value)
				tagVal = event.Value
				data.append(tagVal)
			except:
				data.append(0)
		print(data)
		freq_val = round(data[0],1)
		temp_df = pd.DataFrame(data={'well':[well], 'low_freq':row['low'], 'high_freq': row['high'], 'current_freq':[freq_val]})
		df_all_data = pd.concat([df_all_data, temp_df])

	return df_all_data

#########PI DATA SETUP#############

endDate = dt.datetime.combine(dt.date.today (), dt.time(hour=5, minute=55))
print(endDate)

parseTime = '.1h'
span = AFTimeSpan.Parse(parseTime)

#endDate = dt.date.today()
startDate = (endDate - dateutil.relativedelta.relativedelta(days = 14))
timeRange = AFTimeRange(str(startDate), str(endDate))

piServers = PIServers()    
piServer = piServers["firebagpi"]
######################################







