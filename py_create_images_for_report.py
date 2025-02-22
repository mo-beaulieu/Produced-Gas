#!"C:\Production_Python_Scripts\Produced Gas Daily Report/venv_pg_daily_email_report/Scripts/python.exe"
from cmath import nan
import string
from unicodedata import name
import json

from pyparsing import line
import pandas as pd
import numpy as np
import time
import datetime as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import py_get_tag_data
#import py_create_pdf_report
import plotly.io as pio
import dateutil.relativedelta
from scipy.stats import linregress

import traceback
import sys

pio.kaleido.scope.mathjax = None

rootDir = "C:\PG Gas Script Edits for MB"
print('under root dir')

f = open(rootDir + "/Log.txt","a+")
f.write("\r\n")
f.write("\r\n")
f.write("-----------------------------------\r\n")
str_msg = str(dt.datetime.today()) + " - Starting Code"
f.write(str_msg + "\r\n")
f.close()


try:
	#attempts to create df out of pickle. If not exists it will pull data and recreate pickle
	print('in try')
	#padInput = input("Enter pad number ex. '103' and hit enter.")

	rootDir = "C:\PG Gas Script Edits for MB"

	endDate = dt.datetime.combine(dt.date.today (), dt.time(hour=5, minute=55))
	pg_roc_lookback_list = [2,7,14]

	df_pg_roc_data = pd.DataFrame()
	df_pg_roc_data['mp'] = ''
	for i in pg_roc_lookback_list:
		df_pg_roc_data[str(i) + 'd'] = nan


	
	#get SRU, plant process gas, and field emulsion data for SRU summary plot
	df = py_get_tag_data.create_sru_plot_png()
	print(df)

	fig_sru_plot = make_subplots(specs=[[{"secondary_y": True}]])

	fig_sru_plot.add_trace(go.Scatter(

		x=df['date'].tolist(), y=df['field_emul'].tolist(),
		hoverinfo='x+y',
		mode='lines',
		name = 'Emulsion (2nd)',
		line=dict(width=1.5, color='rgb(0, 0, 0)', ),
		),
		secondary_y = True
	)

	fig_sru_plot.add_trace(go.Scatter(

		x=df['date'].tolist(), y=df['plant_sum'].tolist(),
		hoverinfo='x+y',
		mode='lines',
		name = 'Plant Gas (1st)',
		line=dict(width=1, color='blue'),
		stackgroup='pg'
		), # define stack group
		secondary_y = False
	)
	fig_sru_plot.add_trace(go.Scatter(

		x=df['date'].tolist(), y=df['res_gas'].tolist(),
		hoverinfo='x+y',
		mode='lines',
		name = 'Reservoir Gas (1st)',
		line=dict(width=1, color='red'),
		stackgroup='pg'
		), # define stack group
		secondary_y = False
	)



	sru_constraint_data = [12700]*len(df['date'].tolist())

	fig_sru_plot.add_trace(go.Scatter(
		x=df['date'].tolist(), y=sru_constraint_data,
		hoverinfo='x+y',
		mode='lines',
		name = 'SRU Constraint (1st)',
		line=dict(width=5, color='darkred', dash='dash'),
		), # define stack group
		secondary_y = False
	)

	sru_constraint_data_2 = [10500]*len(df['date'].tolist())

	fig_sru_plot.add_trace(go.Scatter(
		x=df['date'].tolist(), y=sru_constraint_data_2,
		hoverinfo='x+y',
		mode='lines',
		name = 'SRU Constraint (1st)',
		line=dict(width=5, color='orange', dash='dash'),
		), # define stack group
		secondary_y = False
	)


	fig_sru_plot.update_yaxes(title_text="Produced Gas (m3/h)", titlefont = dict(size = 20), tickfont = dict(size=20), secondary_y=False)
	fig_sru_plot.update_yaxes(title_text="Emulsion (m3/h)",titlefont = dict(size = 20), tickfont = dict(size=20), secondary_y=True)
	#fig_sru_plot.update_layout(yaxis_range=(0, 100))

	fig_sru_plot.update_layout(width=1200, height = 500, margin=dict(l= 0, r= 0, t=0, b=0))
	fig_sru_plot.update_layout(legend=dict(yanchor="top", y=0.20, xanchor="left", x=0))
	#fig_sru_plot.write_image(rootDir + "/prod_report_images/sru_plot.png", format="png", scale=3, engine="kaleido") 


	print('about to enter get well status data')
	df = py_get_tag_data.create_cut_wells_status_data()
	print(df)
	print('well status data df should be above')

	fig_well_cuts = go.Figure()

	for index, row in df.iterrows():

		well = row['well']
		low = row['low_freq']
		high = row['high_freq']
		curr = row['current_freq']

		
		if curr < 10:
			x_text = well + '<br>(offline)'
		
		else:
			x_text = well



		fig_well_cuts.add_trace(go.Scatter(
			x=[x_text], y=[high],
			mode='markers+text',
			marker=dict(
				color='red',
				size=15,
				line = dict(
					color = 'red',
					width = 4
				),
			),
			text = [high],
			textposition="top center",
			textfont=dict(
				family="sans serif",
				size=20,
				color='red'
			),
			marker_symbol = 'line-ew', 
			name=well + ' high', 
			legendgroup = well)
		)

		fig_well_cuts.add_trace(go.Scatter(
			x=[x_text], y=[low],
			mode='markers+text',
			marker=dict(
				color='red',
				size=15,
				line = dict(
					color = 'red',
					width = 4
				),
			),
			text = [low],
			textposition="bottom center",
			textfont=dict(
				family="sans serif",
				size=20,
				color='red'
			),
			marker_symbol = 'line-ew', 
			name=well + ' low', 
			legendgroup = well)
		)

		#adding this trace at the end so it is over top of the high/low markers. 
		if curr >= 10:
			fig_well_cuts.add_trace(go.Scatter(
				x=[x_text], y=[curr],
				mode='markers+text',
				marker=dict(
					color='black',
					size=20,
					line = dict(
						color = 'black',
						width = 4
					),
				),
				text = [curr],
				textposition="middle right",
				textfont=dict(
					family="sans serif",
					size=20,
					color='black'
				),
				marker_symbol = 'line-ew', 
				name=well + ' current', 
				legendgroup = well)
			)


	fig_well_cuts.update_yaxes(title_text="Freq (hz)", titlefont = dict(size = 20), tickfont = dict(size=20))
	fig_well_cuts.update_xaxes(tickfont = dict(size=15))
	fig_well_cuts.update_layout(width=1500, height = 180, showlegend=False, margin=dict(l= 0, r= 0, t=0, b=0))
	fig_well_cuts.update_yaxes(range=[30, 65])
	#fig_well_cuts.write_image(rootDir + "/prod_report_images/well_cuts_plot.png", format="png", scale=3, engine="kaleido") 

	measurementPoints = ['P91_92', 'P105', 'P106', 'P107', 'P108', 'P110', 'P114', 'P115', 'P116', 'P117', 'P112', 'P121']
	#measurementPoints = ['P106']


	all_events = []
	for mp in measurementPoints:

		wellsPickleName = 'data_wells_'+ str(mp) + '.pkl'
		padsPickleName = 'data_pads_'+ str(mp) + '.pkl'


		prodMode = False
		if prodMode == True:
			py_get_tag_data.function_get_pi_data_create_pickle_wells(str(mp))
			df_all_data_wells = pd.read_pickle(rootDir + "/prod_pickle_files/" + wellsPickleName)

			if mp == 'P91_92':
				py_get_tag_data.function_get_pi_data_create_pickle_P9192()
			else:
				py_get_tag_data.function_get_pi_data_create_pickle_pads(str(mp))

			df_all_data_pads = pd.read_pickle(rootDir + "/prod_pickle_files/" + padsPickleName)

		else:

			try:
				df_all_data_wells = pd.read_pickle(rootDir + "/prod_pickle_files/" + wellsPickleName)
			except:
				
				py_get_tag_data.function_get_pi_data_create_pickle_wells(str(mp))
				df_all_data_wells = pd.read_pickle(rootDir + "/prod_pickle_files/" + wellsPickleName)

			try:
				df_all_data_pads = pd.read_pickle(rootDir + "/prod_pickle_files/" + padsPickleName)
			except:

				if mp == 'P91_92':
					py_get_tag_data.function_get_pi_data_create_pickle_P9192()
				else:
					py_get_tag_data.function_get_pi_data_create_pickle_pads(str(mp))

				df_all_data_pads = pd.read_pickle(rootDir + "/prod_pickle_files/" + padsPickleName)


		uniqueAttributes = df_all_data_wells['attribute'].unique()

		df_all_data_wells_esp_frequency = df_all_data_wells.loc[df_all_data_wells['attribute'] == 'esp_frequency']
		df_all_data_wells_esp_frequency_pivot = df_all_data_wells_esp_frequency.reset_index().pivot_table(index='date', columns='well', values='value')

		df_all_data_wells_temp_tubing = df_all_data_wells.loc[df_all_data_wells['attribute'] == 'temp_tubing']
		df_all_data_wells_temp_tubing_pivot = df_all_data_wells_temp_tubing.reset_index().pivot_table(index='date', columns='well', values='value')


		df_all_data_wells_casing_valve_test_status=df_all_data_wells.loc[df_all_data_wells['attribute'] == 'casing_valve']
		
		wells = df_all_data_wells_esp_frequency_pivot.columns

		df_all_data_pads_pg = df_all_data_pads.loc[df_all_data_pads['attribute'] == 'produced_gas']
		#df_all_data_pads_emulsion= df_all_data_pads.loc[df_all_data_pads['attribute'] == 'real_time_pad_flow']

		#script that will take the linear regression (rate of change) over different time periods for produced gas and store in a data frame
		#temp_df = pd.DataFrame(data={'mp': [mp]})
		df_roc_data_temp = pd.DataFrame()
		df_roc_data_temp['mp'] = [mp]
		for dayslookback in pg_roc_lookback_list:

			df_temp =df_all_data_pads_pg[~(df_all_data_pads_pg['date'] < (endDate - dateutil.relativedelta.relativedelta(days = dayslookback)))]


			iCount = 0
			step = 0.6
			timeHourlyStep = []
			for i in df_temp['date'].tolist():
				timeHourlyStep.append(step*iCount)
				iCount = iCount +1
			


			try:
				roc = linregress(timeHourlyStep, df_temp['value'].tolist()).slope
				df_roc_data_temp[str(dayslookback)+'d'] = [round(roc*24, 1)]
			except:
				df_roc_data_temp[str(dayslookback)+'d'] = 'err'


		df_pg_roc_data = pd.concat([df_pg_roc_data, df_roc_data_temp])

		


		trip_well_names = []

		#fig = go.Figure()
		fig = make_subplots(specs=[[{"secondary_y": True}]])

		fig.add_trace(go.Scatter(
			x=df_all_data_pads_pg['date'].tolist(),
			y=df_all_data_pads_pg['value'].tolist(),
			mode='lines',
			line=dict(
				color='black',
				),
			name='PG'),
			secondary_y=False, 
		)

		# fig.add_trace(go.Scatter(
		# 	x=df_all_data_pads_emulsion['date'].tolist(),
		# 	y=df_all_data_pads_emulsion['value'].tolist(),
		# 	mode='lines',
		# 	line=dict(
		# 		color='yellow',
		# 		),
		# 	name='Emulsion'),
		# 	secondary_y=True, 
		# )

		

		trip_dates = []
		trip_desc = []
		trip_pgVal = []

		start_dates=[]
		start_desc = []
		start_pgVal = []

		#df_casing_valve_postiion = pd.DataFrame(columns = ['well', '48hr']))
		# = pd.DataFrame(data={'well': trip_dates, 'vals': trip_desc})
		well_csg_valve_lookback_list = [2, 7, 14]
		df_csg_valve_data= pd.DataFrame()
		df_csg_valve_data['Well'] = ''
		for i in well_csg_valve_lookback_list:
			df_csg_valve_data[str(i) + 'd'] = nan
		
		tempThreasholdForFlowing = 140
		for well in wells:

			print(well)

			#get the 48hour average casing valve position and append to a dataframe
			df_csg = df_all_data_wells_casing_valve_test_status.loc[df_all_data_wells['well'] == well]

			df_csg_valve_data_temp = pd.DataFrame()
			df_csg_valve_data_temp['Well'] = [well]
			for dayslookback in well_csg_valve_lookback_list:

				df_temp =df_csg[~(df_csg['date'] < (endDate - dateutil.relativedelta.relativedelta(days = dayslookback)))]
				list_vals = df_temp['value'].tolist()
				try:
					avg_valve_pos = sum(list_vals)/len(list_vals)
				except:
					avg_valve_pos = 0
				df_csg_valve_data_temp[str(dayslookback)+'d'] = [round(avg_valve_pos, 1)]

			df_csg_valve_data = pd.concat([df_csg_valve_data, df_csg_valve_data_temp])

			lastEventTrip = False #for deadehad logic
			deadheadEventDetected = False
			speedUpEventsDetected = False
			
			#x_anno = []
			#y_anno = []
			#text_anno = []

			for rowNum, (index, row) in enumerate(df_all_data_wells_esp_frequency_pivot.iterrows()):


				if rowNum ==0:
					prevVal = row[well]
				else:
					currentVal = row[well]
					diff = currentVal-prevVal

					if rowNum > 5 and deadheadEventDetected == True:
						#check to see if well has started flowing again
						#(established by the last 5 points being greater than flowing temp threashhold and then cancel deadhead event true so that it can be detected again)
						try:
							dateDiffLastDeadhead = df_all_data_wells_esp_frequency_pivot.index.tolist()[rowNum] - lastDeadheadDate
							daysDiff = dateDiffLastDeadhead.days
							tempList=[]
							#print(rowNum)
							#print(df_all_data_wells_temp_tubing_pivot[well])
							#print(len(df_all_data_wells_temp_tubing_pivot[well].tolist()))
							#print('list length above')

							#print('length of esp pivot table below')
							#print(df_all_data_wells_esp_frequency_pivot[well])
							#print('------')
							#print(df_all_data_wells_esp_frequency_pivot)

							for i in range(1,6):
								#print(rowNum)
								tempList.append(df_all_data_wells_temp_tubing_pivot[well].tolist()[rowNum-i])

							if all(i >= (tubingTempPriorToDeadhead-10) for i in tempList) and daysDiff >1:
								deadheadEventDetected = False
						except:
							deadheadEventDetected = False
						
						#print(tubingTempPriorToDeadhead)
						#print(tempList)
						#print('curr date', df_all_data_wells_esp_frequency_pivot.index.tolist()[rowNum])
						#print('lastdeadhead date', dateDiffLastDeadhead)
						#print(daysDiff)
						#print(deadheadEventDetected)


						
						#input('')
						


					if diff < -20:
						lastEventTrip = True
						deadheadEventDetected = False
						trip_desc_str = 'ESP Trip', index, well, ' ESP went from ', prevVal, 'hz to ', currentVal, 'hz'
						print(trip_desc_str)
						date = df_all_data_wells_esp_frequency_pivot.index.tolist()[rowNum]
						annotation = well + ' trip'
						#print(df_all_data_pads_pg)
						trip_dates.append(date)
						trip_desc.append(annotation)
						all_events.append({'well':well, 'date': date.strftime('%Y-%m-%d %X'), 'desc': annotation}) #############

						#x_anno.append(date)
						#y_anno.append(df_all_data_pads_pg['value'].loc[df_all_data_pads_pg['date']==date].tolist()[0])
						#text_anno.append(well)

						
						fig.add_trace(go.Scatter(
							x=[date], y=[df_all_data_pads_pg['value'].loc[df_all_data_pads_pg['date']==date].tolist()[0]],
							mode='markers + text',
							marker=dict(
								color='red',
								size=10,
							),
							text = [well],
							textposition="middle left",
							textfont=dict(
								family="sans serif",
								size=8,
								color='red'
							),
							marker_symbol = 'triangle-down', 
							name=annotation, 
							legendgroup = well),
							secondary_y=False,
						)

						# fig.add_annotation(text=well, x=date, y=df_all_data_pads_pg['value'].loc[df_all_data_pads_pg['date']==date].tolist()[0], showarrow=False, textangle=-90,
						# 	font=dict(
						# 		family="sans serif",
						# 		size=8,
						# 		color='red'
						# 	), yshift = -20)


					elif diff >20:
						lastEventTrip = False
						deadheadEventDetected = False
						trip_desc_str = 'ESP Start', index, well, ' ESP went from ', prevVal, 'hz to ', currentVal, 'hz'
						print(trip_desc_str)
						date = df_all_data_wells_esp_frequency_pivot.index.tolist()[rowNum]
						annotation = well + ' start'
						start_dates.append(date)
						start_desc.append(annotation)
						all_events.append({'well':well, 'date': date.strftime('%Y-%m-%d %X'), 'desc': annotation}) #############

						


						fig.add_trace(go.Scatter(
							x=[date], y=[df_all_data_pads_pg['value'].loc[df_all_data_pads_pg['date']==date].tolist()[0]],
							mode='markers + text',
							marker=dict(
								color='green',
								size=10,
							),
							text = [well],
							textposition="middle left",
							textfont=dict(
								family="sans serif",
								size=8,
								color='green'
							),
							marker_symbol = 'triangle-up',
							name=annotation, 
							legendgroup = well),
							secondary_y=False,
						)

						# fig.add_annotation(text=well, x=date, y=df_all_data_pads_pg['value'].loc[df_all_data_pads_pg['date']==date].tolist()[0], showarrow=False, textangle=-90,
						# 	font=dict(
						# 		family="sans serif",
						# 		size=8,
						# 		color='green'
						# 	), yshift = 20)

					
					elif lastEventTrip ==False: #no esp trip or start detected. Determine if deadhead event is occuring. 
						#create better logic. Right now the +40 = 4hrs at 6min data intervale
						if rowNum >40:
							if deadheadEventDetected != True:
								try: #it will not be able to perform this check on the first 4 hours of data.
									if df_all_data_wells_temp_tubing_pivot[well].tolist()[rowNum-40] > tempThreasholdForFlowing: #logic added so that wells that are offline with temps are not 
											
										temp_tubing_4hr_slope=(df_all_data_wells_temp_tubing_pivot[well].tolist()[rowNum] - df_all_data_wells_temp_tubing_pivot[well].tolist()[rowNum-40])/4
										if temp_tubing_4hr_slope <=-5:
											deadheadEventDetected = True
											tubingTempPriorToDeadhead = df_all_data_wells_temp_tubing_pivot[well].tolist()[rowNum-40]
											date = df_all_data_wells_temp_tubing_pivot.index.tolist()[rowNum-40]
											lastDeadheadDate = date
											#print(lastDeadheadDate)
											#input('')
											annotation = well + ' NFE'

											trip_dates.append(date)
											trip_desc.append(annotation)
											all_events.append({'well':well, 'date': date.strftime('%Y-%m-%d %X'), 'desc': annotation}) #############

											print('deadhead event found. ', 'current temp: ', df_all_data_wells_temp_tubing_pivot[well].tolist()[rowNum], '. temp @-4hrs: ', df_all_data_wells_temp_tubing_pivot[well].tolist()[rowNum-40], '. slope:', temp_tubing_4hr_slope, '. Date: ', date)

											fig.add_trace(go.Scatter(
												x=[date], y=[df_all_data_pads_pg['value'].loc[df_all_data_pads_pg['date']==date].tolist()[0]],
												mode='markers + text',
												marker=dict(
													color='blue',
													size=10,
												),
												text = [well],
												textposition="middle left",
												textfont=dict(
													family="sans serif",
													size=8,
													color='blue'
												),
												marker_symbol = 'x',
												name=annotation, 
												legendgroup = well),
												secondary_y=False,
											)							

											# fig.add_annotation(text=well, x=date, y=df_all_data_pads_pg['value'].loc[df_all_data_pads_pg['date']==date].tolist()[0], showarrow=False, textangle=-90,
											# 	font=dict(
											# 		family="sans serif",
											# 		size=8,
											# 		color='blue'
											# 	), yshift = 20)


								except:
									continue
					
					try:
						if rowNum >=10:
							if df_all_data_wells_esp_frequency_pivot[well].tolist()[rowNum] - df_all_data_wells_esp_frequency_pivot[well].tolist()[rowNum-10] >2:
								if speedUpEventsDetected ==False:
									#create new lists to enter data during the speed up event. 
									speedUpDates = []
									speedUpEmulsionVals = []
									speedUpESPSpeeds = []
									#this is the first detection and we will put in all 10pts used to make this realization that a speed up is occuring. Afterwards only the new point
									i = rowNum-10 
									while i <= rowNum:
										date = df_all_data_wells_esp_frequency_pivot.index.tolist()[i]
										speedUpDates.append(date)
										#speedUpEmulsionVals.append(df_all_data_pads_emulsion['value'].loc[df_all_data_pads_emulsion['date']==date].tolist()[0])
										speedUpESPSpeeds.append(df_all_data_wells_esp_frequency_pivot[well].tolist()[i])
										i=i+1
									speedUpEventsDetected = True
								elif speedUpEventsDetected ==True:
								
									date = df_all_data_wells_esp_frequency_pivot.index.tolist()[rowNum]
									speedUpDates.append(date)
									#speedUpEmulsionVals.append(df_all_data_pads_emulsion['value'].loc[df_all_data_pads_emulsion['date']==date].tolist()[0])
									speedUpESPSpeeds.append(df_all_data_wells_esp_frequency_pivot[well].tolist()[rowNum])

							else:
								if speedUpEventsDetected ==True:
									freqChange = speedUpESPSpeeds[len(speedUpESPSpeeds)-1]-speedUpESPSpeeds[0]
									if freqChange < 25: #this indicates a start up and it will already be captured in other anontations. 
										
										annotation = well + ' +' + str(round(freqChange,2)) + ' hz'
										print(annotation)
										#print('line prior to speed up print statement zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
										#print(annotation)
										#print(speedUpDates)
										#print(speedUpESPSpeeds)
										#print('line after to speed up print statement zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
										start_dates.append(speedUpDates[0])
										start_desc.append(annotation)
										all_events.append({'well':well, 'date': date.strftime('%Y-%m-%d %X'), 'desc': annotation}) #############

										
										#!!!!!!!!!!!!!!!!! - - uncomment to insert emulsion line to plot -- --!!!!!!!!!
										# fig.add_trace(go.Scatter(
										# 	x=[speedUpDates[0], speedUpDates[len(speedUpESPSpeeds)-1]],
										# 	y=[max(speedUpEmulsionVals), max(speedUpEmulsionVals)],
										# 	mode='lines',
										# 	line=dict(
										# 		color='red',
										# 		),
										# 	name=annotation),
										# 	secondary_y=True,
										# )
										#!!!!!!!!!!!!!!!!! - - uncomment to insert emulsion line to plot -- --!!!!!!!!!
									speedUpEventsDetected =False

					except:
						prevVal = currentVal
						continue

					prevVal = currentVal
		

		####Write main PG plot to png

		scale_input = 5

		fig.update_layout(width=600, height = 300, showlegend=False, margin=dict(l= 0, r= 0, t=0, b=0))
		fig.update_xaxes(range=[(endDate - dateutil.relativedelta.relativedelta(days = 14)), endDate])
		#fig.show()
		#fig.write_image(rootDir + "/prod_report_images/" + mp + "_pg_plot.png", format="png", scale=scale_input, engine="kaleido") 
		#fig.write_html(rootDir + "/prod_report_images/" + mp + "_pg_plot.html")
		
		#write tables
		#table generic set up inputs:
		header_height = 19
		header_font_size = 13
		cells_height=19
		cells_font_size=11

		#create trips / nfe table: 
		temp_sorting_df = pd.DataFrame(data={'date': trip_dates, 'vals': trip_desc})
		temp_sorting_df['date'] = pd.to_datetime(temp_sorting_df['date'])
		temp_sorting_df = temp_sorting_df[~(temp_sorting_df['date'] < (endDate - dateutil.relativedelta.relativedelta(days = 1)))]
		temp_sorting_df = temp_sorting_df.sort_values(by='date', ascending = True)
		outerWhileLoopCount = 0
		while len(temp_sorting_df) > 8: #need to search for group trips and / or delete
			outerWhileLoopCount = outerWhileLoopCount +1
			linesThatAreNotSingleTrips = 0 
			for index, row in temp_sorting_df.iterrows():
				if 'trip' in row['vals'] and 'trips' not in row['vals']: #trip detected
					indexListToDelete = []
					referenceDate = row['date']
					referenceIndex = index
					countOfNearbyTrips = 0	
					for index, row in temp_sorting_df.iterrows():
						if index != referenceIndex and 'trip' in row['vals'] and 'trips' not in row['vals']:
							dateDiff = row['date'] - referenceDate
							days, seconds = dateDiff.days, dateDiff.seconds
							hoursDiff = days * 24 + seconds // 3600
							if hoursDiff <=3:
								countOfNearbyTrips = countOfNearbyTrips +1
								indexListToDelete.append(index)
					if countOfNearbyTrips >0:
						indexListToDelete.append(referenceIndex)
						temp_sorting_df = temp_sorting_df.drop(indexListToDelete)
						temp = pd.DataFrame(data={'date': [referenceDate], 'vals': ["Trips (" + str(countOfNearbyTrips) + ")"]})
						#print(temp_sorting_df)
						#print(temp)
						#input('')
						temp_sorting_df=pd.concat([temp_sorting_df, temp])
						temp_sorting_df = temp_sorting_df.sort_values(by='date', ascending = True)
						break
				else:
					linesThatAreNotSingleTrips = linesThatAreNotSingleTrips +1
					if linesThatAreNotSingleTrips == len(temp_sorting_df) or outerWhileLoopCount == 8:
						temp_sorting_df = temp_sorting_df.sort_values(by='date', ascending = False)
						#print(temp_sorting_df)
						n=len(temp_sorting_df)-8+1
						temp_sorting_df = temp_sorting_df.iloc[:-n , :]
						temp = pd.DataFrame(data={'date': [endDate - dateutil.relativedelta.relativedelta(days = 1)], 'vals': ["Overflow..."]})
						temp_sorting_df=pd.concat([temp_sorting_df, temp])
						#print(temp_sorting_df)
						#input('lines were dropped from table')
						break




		temp_sorting_df = temp_sorting_df.sort_values(by='date', ascending = False)

		datestrs = [dt.datetime.strftime(x,'%b-%d %H:%M') for x in temp_sorting_df['date'].tolist()]

		values = []
		values.append(datestrs)
		values.append(temp_sorting_df['vals'].tolist())

		table_fig = go.Figure(data=[go.Table(
		columnorder = [1,2],
		columnwidth = [1,1.6],
		header = dict(
			values = ['Date', 'Event'],
			line_color='darkslategray',
			fill_color='royalblue',
			align=['center','center'],
			font=dict(color='white', size=header_font_size),
			height=header_height
		),
		cells=dict(
			values=values,
			line_color='darkslategray',
			fill=dict(color=['paleturquoise', 'white']),
			align=['left', 'center'],
			font_size=cells_font_size,
			height=cells_height)
			)
		])

		heightCalc = (len(datestrs) * cells_height) +header_height +2
		table_fig.update_layout(width=300, height = heightCalc, margin=dict(l= 0, r= 0, t=0, b=0))
		#table_fig.write_image(rootDir + "/prod_report_images/" + mp + "_trip_nfe.png", format="png", scale=scale_input, engine="kaleido") 

		#create starts/speed ups table: 
		temp_sorting_df = pd.DataFrame(data={'date': start_dates, 'vals': start_desc})
		temp_sorting_df['date'] = pd.to_datetime(temp_sorting_df['date'])
		temp_sorting_df = temp_sorting_df[~(temp_sorting_df['date'] < (endDate - dateutil.relativedelta.relativedelta(days = 1)))]
		temp_sorting_df = temp_sorting_df.sort_values(by='date', ascending = True)

		outerWhileLoopCount = 0
		while len(temp_sorting_df) > 8: #need to search for group trips and / or delete
			outerWhileLoopCount = outerWhileLoopCount +1

			linesThatAreNotSingleStarts = 0 
			for index, row in temp_sorting_df.iterrows():
				if 'start' in row['vals'] and 'starts' not in row['vals']: #trip detected
					indexListToDelete = []
					referenceDate = row['date']
					referenceIndex = index
					countOfNearbyStarts = 0	
					for index, row in temp_sorting_df.iterrows():
						if index != referenceIndex and 'start' in row['vals'] and 'starts' not in row['vals']:
							dateDiff = row['date'] - referenceDate
							days, seconds = dateDiff.days, dateDiff.seconds
							hoursDiff = days * 24 + seconds // 3600
							if hoursDiff <=3:
								countOfNearbyStarts = countOfNearbyStarts +1
								indexListToDelete.append(index)
					if countOfNearbyStarts >0:
						indexListToDelete.append(referenceIndex)
						temp_sorting_df = temp_sorting_df.drop(indexListToDelete)
						temp = pd.DataFrame(data={'date': [referenceDate], 'vals': ["Starts (" + str(countOfNearbyStarts) + ")"]})
						#print(temp_sorting_df)
						#print(temp)
						#input('')
						temp_sorting_df=pd.concat([temp_sorting_df, temp])
						temp_sorting_df = temp_sorting_df.sort_values(by='date', ascending = True)
						break
				else:
					linesThatAreNotSingleStarts = linesThatAreNotSingleStarts +1
					if linesThatAreNotSingleStarts == len(temp_sorting_df) or outerWhileLoopCount == 8:
						temp_sorting_df = temp_sorting_df.sort_values(by='date', ascending = False)
						#print(temp_sorting_df)
						#input('')
						n=len(temp_sorting_df)-8+1
						temp_sorting_df = temp_sorting_df.iloc[:-n , :]
						#temp_sorting_df = temp_sorting_df.drop(df.tail(len(temp_sorting_df)-(8+1)).index, inplace = True)
						#print(temp_sorting_df)
						temp = pd.DataFrame(data={'date': [endDate - dateutil.relativedelta.relativedelta(days = 1)], 'vals': ["Overflow..."]})
						temp_sorting_df=pd.concat([temp_sorting_df, temp])
						#print(temp_sorting_df)
						#input('lines were dropped from table')
						break


		temp_sorting_df = temp_sorting_df.sort_values(by='date', ascending = False)
		datestrs = [dt.datetime.strftime(x,'%b-%d %H:%M') for x in temp_sorting_df['date'].tolist()]

		values = []
		values.append(datestrs)
		values.append(temp_sorting_df['vals'].tolist())

		table_fig = go.Figure(data=[go.Table(
		columnorder = [1,2],
		columnwidth = [1,1.5],
		header = dict(
			values = ['Date', 'Event'],
			line_color='darkslategray',
			fill_color='royalblue',
			align=['center','center'],
			font=dict(color='white', size=header_font_size),
			height=header_height
		),
		cells=dict(
			values=values,
			line_color='darkslategray',
			fill=dict(color=['paleturquoise', 'white']),
			align=['center', 'center'],
			font_size=cells_font_size,
			height=cells_height)
			)
		])

		heightCalc = (len(datestrs) * cells_height) +header_height +2
		table_fig.update_layout(width=300, height = heightCalc, margin=dict(l= 0, r= 0, t=0, b=0))
		#table_fig.write_image(rootDir + "/prod_report_images/" + mp+ "_start_speedup.png", format="png", scale=scale_input, engine="kaleido") 

		#create overall rate of change table

		values = []
		for col in df_pg_roc_data.columns:
			values.append(df_pg_roc_data[col].tolist())
		
		#values.append(datestrs)
		#values.append(temp_sorting_df['vals'].tolist())

		table_fig = go.Figure(data=[go.Table(
		columnorder = [1,2,3,4],
		columnwidth = [1, 0.75, 0.75, 0.75],
		header = dict(
			values = df_pg_roc_data.columns,
			line_color='darkslategray',
			fill_color='royalblue',
			align=['center','center'],
			font=dict(color='white', size=header_font_size),
			height=header_height
		),
		cells=dict(
			values=values,
			line_color='darkslategray',
			fill=dict(color=['paleturquoise', 'white']),
			align=['center', 'center'],
			font_size=cells_font_size,
			height=cells_height)
			)
		])

		heightCalc = (len(df_pg_roc_data['mp']) * cells_height) +header_height +2
		table_fig.update_layout(width=250, height = heightCalc, margin=dict(l= 0, r= 0, t=0, b=0))
		#table_fig.write_image(rootDir + "/prod_report_images/mp_pg_roc.png", format="png", scale=scale_input, engine="kaleido") 

		#create casing valve average position table

		df_csg_valve_data = df_csg_valve_data.sort_values(by=str(well_csg_valve_lookback_list[0])+"d", ascending = False)
		n=len(df_csg_valve_data)-8
		df_csg_valve_data = df_csg_valve_data.iloc[:-n , :]


		values = []
		for col in df_csg_valve_data.columns:
			values.append(df_csg_valve_data[col].tolist())
		
		#values.append(datestrs)
		#values.append(temp_sorting_df['vals'].tolist())

		table_fig = go.Figure(data=[go.Table(
		columnorder = [1,2,3,4],
		columnwidth = [1, 1, 1, 1],
		header = dict(
			values = df_csg_valve_data.columns,
			line_color='darkslategray',
			fill_color='royalblue',
			align=['center','center'],
			font=dict(color='white', size=header_font_size),
			height=header_height
		),
		cells=dict(
			values=values,
			line_color='darkslategray',
			fill=dict(color=['paleturquoise', 'white']),
			align=['center', 'center'],
			font_size=cells_font_size,
			height=cells_height)
			)
		])

		heightCalc = (len(df_csg_valve_data['Well']) * cells_height) +header_height +2
		table_fig.update_layout(width=300, height = heightCalc, margin=dict(l= 0, r= 0, t=0, b=0))
		#table_fig.write_image(rootDir + "/prod_report_images/" + mp + "_csg_valve.png", format="png", scale=scale_input, engine="kaleido")
		# Open a file in write mode.
	
	print(all_events) 
	with open('events.csv', 'w') as f:
		# Write all the dictionary keys in a file with commas separated.
		f.write(','.join(all_events[0].keys()))
		f.write('\n') # Add a new line
		for row in all_events:
			# Write the values in a row.
			f.write(','.join(str(x) for x in row.values()))
			f.write('\n') # Add a new line

	

	print('images are created. Starting creating report to PDF.')
	#py_create_pdf_report.create_report()

	f = open(rootDir + "/Log.txt","a+")
	f.write("\r\n")
	str_msg = str(dt.datetime.today()) + " - Code is complete"
	f.write(str_msg + "\r\n")
	f.write("-----------------------------------\r\n")
	f.write("\r\n")
	f.close()
	print('script complete')
except:
	print(traceback.format_exc())
	f = open(rootDir + "/Log.txt","a+")
	f.write("\r\n")
	f.write(str(dt.datetime.today()) + "\r\n")
	f.write(str(traceback.format_exc()) + "\r\n")
	f.write("\r\n")
	f.write("-----------------------------------\r\n")
	f.close()
