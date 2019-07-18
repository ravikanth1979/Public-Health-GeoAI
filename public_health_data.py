import pandas as pd
import numpy as np


###Load entire dataset from csv files
districtua_data = pd.read_csv('DistrictUA.csv')
countyua_data = pd.read_csv('CountyUA.csv')
region_data = pd.read_csv('RegionUA.csv')


######################## Data access methods common to all tabs###################################################################################
def get_all_regions(input_dataset):
    return input_dataset.loc[input_dataset['Parent Name']!='England']['Parent Name'].dropna().unique().tolist()

###Return the data set based on area type selected
def get_entire_dataset(area_type):
    if(area_type=='DistrictUA'):
        return districtua_data
    elif(area_type=='CountyUA'):
        return countyua_data
    elif(area_type=='Region'):
        return region_data
    else:
        return None

####Data set for selected area
def get_entire_data_for_area(input_dataset, area_name):
    output_dataset  = input_dataset.loc[input_dataset['Area Name']==area_name]
    return output_dataset

####Data set for selected region
def get_entire_data_for_region(input_dataset, region):
    output_dataset  = input_dataset.loc[input_dataset['Parent Name']==region]
    print("inside get entire data for region.....")
    print(output_dataset.head())
    return output_dataset

###Data set for time period
def get_entire_data_for_timeperiod(input_dataset, timeperiod):
    output_dataset = input_dataset.loc[input_dataset['Time period']==timeperiod]
    print("inside get entire data for time period.....")
    #print(output_dataset.head())
    return output_dataset

##############################################################Overview Tab related methods#####################################################################
#####Grouped Overview Data#
def get_overview_grouped_data(input_data):
    grouped_data_frame = pd.DataFrame(input_data.groupby(['Indicator Name','Time period','Area Name'])['Value'].mean())
    grouped_data_frame['Indicator_Area']=grouped_data_frame.index.tolist()
    indicator= grouped_data_frame['Indicator_Area'].apply(lambda x:x[0] )
    period= grouped_data_frame['Indicator_Area'].apply(lambda x:x[1] )
    area= grouped_data_frame['Indicator_Area'].apply(lambda x:x[2] )
    grouped_data_frame['Area_Name']=area
    grouped_data_frame['Time_period']=period
    grouped_data_frame['Indicator_Name']=indicator
    return grouped_data_frame

#####Overview Indicator List#
def get_overview_indicators_list(area_type, region, timeperiod):
    return get_region_overview_data(area_type, region, timeperiod)['Indicator'].tolist()

def get_entire_indicators_list(area_type,timeperiod):
    return get_entire_dataset(area_type)['Indicator Name'].dropna().unique().tolist()

####Overview data for the given region and time period
def get_overview_data_for_region_timeperiod(area_type, region, timeperiod):
    input_dataset = get_entire_dataset(area_type)
    input_dataset = get_entire_data_for_region(input_dataset,region)
    input_dataset = get_entire_data_for_timeperiod(input_dataset,timeperiod)
    output_dataset = input_dataset.loc[input_dataset['Indicator Name'].isin(input_dataset['Indicator Name'].dropna().unique().tolist()[0:6])]
    return output_dataset

####Entire data for the given region and time period 
def get_entire_data_for_region_timeperiod(area_type, region, timeperiod):
    input_dataset = get_entire_dataset(area_type)
    input_dataset = get_entire_data_for_region(input_dataset,region)
    input_dataset = get_entire_data_for_timeperiod(input_dataset,timeperiod)
    return input_dataset.loc[input_dataset['Indicator Name'].isin(input_dataset['Indicator Name'].dropna().unique().tolist())]

####Overview data for the given area and time period
def get_overview_data_for_area_timeperiod(area_type, area, timeperiod):
    input_dataset = get_entire_dataset(area_type)
    output_dataset = get_entire_data_for_area(input_dataset,area)
    output_dataset = get_entire_data_for_timeperiod(output_dataset,timeperiod)
    return output_dataset.loc[output_dataset['Indicator Name'].isin(output_dataset['Indicator Name'].dropna().unique().tolist()[0:6])]

####Overview empty list to populate required Overview Data
def get_overview_empty_list(input_dataset, region,timeperiod):
    area_list = input_dataset['Area Name'].dropna().unique().tolist()
    return pd.DataFrame(columns=area_list)

####Overview data for selected region
def get_region_overview_data(area_type, region, timeperiod):
    input_dataset = get_overview_data_for_region_timeperiod(area_type, region, timeperiod)
    grouped_data_frame = get_overview_grouped_data(input_dataset)
    new_dataframe =  get_overview_empty_list(input_dataset, region,timeperiod) 
    column_names =new_dataframe.columns.tolist()
    column_names.append(region)
    column_names.append('England ')
    for column_name in new_dataframe.columns:
        new_dataframe[column_name] = [round(element, 2) for element in pd.to_numeric(grouped_data_frame.loc[grouped_data_frame['Area_Name']== column_name]['Value'].values)]
    new_dataframe = new_dataframe.sort_index(axis=1)
    new_dataframe.insert(loc=0, column='Period', value='2015 - 17')
    new_dataframe.insert(loc=1, column='England ', value=[round(element, 2) for element in pd.to_numeric(get_overview_grouped_data(get_overview_data_for_area_timeperiod(area_type, 'England',timeperiod))['Value'].values)])
    new_dataframe.insert(loc=2, column=region, value=[round(element, 2) for element in pd.to_numeric(get_overview_grouped_data(get_overview_data_for_area_timeperiod(area_type, region, timeperiod))['Value'].values)])
    #empty_list[region] =  pd.to_numeric(get_overview_grouped_data(get_overview_data_for_area_timeperiod(area_type, region, timeperiod))['Value'].values)
    new_dataframe['Indicator'] = grouped_data_frame['Indicator_Name'].unique()
    new_dataframe.set_index('Indicator', inplace = True)
    new_dataframe.reset_index( inplace = True)
    for index, row in new_dataframe.iterrows():
        for col_name in column_names:
            if(int(row['England '])-int(row[col_name])>=1):
                new_dataframe.loc[index,col_name] = str(row[col_name])+','+col_name+',Worse'
            elif(int(row['England '])-int(row[col_name])<=-1):
                new_dataframe.loc[index,col_name] = str(row[col_name])+','+col_name+',Better'
            else:
                new_dataframe.loc[index,col_name] = str(row[col_name])+','+col_name+',Similar'
    return new_dataframe

###Over data for entire country england
def get_england_overview_data(area_type, region, timeperiod):
    input_dataset = get_overview_data_for_region_timeperiod(area_type, region, timeperiod)
    grouped_data_frame = get_overview_grouped_data(input_dataset)
    new_dataframe =  get_overview_empty_list(input_dataset, region,timeperiod) 
    column_names =new_dataframe.columns.tolist()
    column_names.append(region)
    column_names.append('England ')
    for column_name in new_dataframe.columns:
        new_dataframe[column_name] = [round(element, 2) for element in pd.to_numeric(grouped_data_frame.loc[grouped_data_frame['Area_Name']== column_name]['Value'].values)]
    new_dataframe = new_dataframe.sort_index(axis=1)
    new_dataframe.insert(loc=0, column='Period', value='2015 - 17')
    new_dataframe.insert(loc=1, column=region, value=[round(element, 2) for element in pd.to_numeric(get_overview_grouped_data(get_overview_data_for_area_timeperiod(area_type, region, timeperiod))['Value'].values)])
    #empty_list[region] =  pd.to_numeric(get_overview_grouped_data(get_overview_data_for_area_timeperiod(area_type, region, timeperiod))['Value'].values)
    new_dataframe['Indicator'] = grouped_data_frame['Indicator_Name'].unique()
    new_dataframe.set_index('Indicator', inplace = True)
    new_dataframe.reset_index( inplace = True)
    return new_dataframe

########################################################Compare Indicators Tab related###############################################################################
####Entire data for indicator filtered by indicator name
def get_entire_data_for_indicator(input_dataset,indicator_name):
    return input_dataset.loc[input_dataset['Indicator Name']==indicator_name]

###Entire indicator list
def get_entire_data_for_indicator_list(input_dataset,indicator_list):
    return input_dataset.loc[input_dataset['Indicator Name'] in indicator_list]

###Grouped indicator data
def get_grouped_region_indicator_data(input_data):
    grouped_quantile_data = input_data.groupby(['Time period'])['Value']
    return grouped_quantile_data

###Compare Indicators data
def get_compare_indicators_data(area_type,region,indicator_name_x,indicator_name_y,time_period=None):
    input_dataset = get_entire_dataset(area_type)
    input_dataset = get_entire_data_for_region(input_dataset,region)
    output_dataset = pd.DataFrame()
    input_dataset = input_dataset.loc[input_dataset['Indicator Name'].isin([indicator_name_x,indicator_name_y])]
    input_indicator_x_dataset = input_dataset.loc[input_dataset['Indicator Name']==indicator_name_x]
    input_indicator_y_dataset = input_dataset.loc[input_dataset['Indicator Name']==indicator_name_y]
    grouped_x_dataset = input_indicator_x_dataset.groupby(['Area Name'])['Value'].mean()
    grouped_y_dataset = input_indicator_y_dataset.groupby(['Area Name'])['Value'].mean()
    output_dataset['Area']=grouped_x_dataset.index.tolist()
    output_dataset['X']=[round(element, 2) for element in pd.to_numeric(grouped_x_dataset).tolist()]
    output_dataset['Y']=[round(element, 2) for element in pd.to_numeric(grouped_y_dataset).tolist()]
    return output_dataset


##########################################Trends Tab related methods#################################################################################
###Grouped trends data for value attribute
def get_grouped_trends_value_data(input_data):
    grouped_value_data_frame = pd.DataFrame(input_data.groupby(['Time period'])['Value'].mean())
    #grouped_value_data_frame['Time_Period']=grouped_value_data_frame.index.tolist()
    return grouped_value_data_frame

###Grouped trends data for lowerci attribute
def get_grouped_trends_lowerci_data(input_data):
    grouped_lowerci_data_frame = pd.DataFrame(input_data.groupby(['Time period'])['Lower CI 95.0 limit'].mean())
    #grouped_lowerci_data_frame['Time_Period']=grouped_lowerci_data_frame.index.tolist()
    return grouped_lowerci_data_frame

###Grouped trends data for upperci attribute
def get_grouped_trends_upperci_data(input_data):
    grouped_upperci_data_frame = pd.DataFrame(input_data.groupby(['Time period'])['Upper CI 95.0 limit'].mean())
    #grouped_upperci_data_frame['Time_Period']=grouped_upperci_data_frame.index.tolist()
    return grouped_upperci_data_frame

###The final required trends data
def get_trends_data(area_type, area_name, region_name, indicator_name):
    entire_dataset = get_entire_dataset(area_type)
    input_dataset = get_entire_data_for_area(entire_dataset,area_name)
    input_dataset = get_entire_data_for_indicator(input_dataset,indicator_name)
    grouped_trend_value_data = get_grouped_trends_value_data(input_dataset).dropna()
    grouped_trend_lowerci_data = get_grouped_trends_lowerci_data(input_dataset).dropna()
    grouped_trend_upperci_data = get_grouped_trends_upperci_data(input_dataset).dropna()
    result_dataset = pd.DataFrame()
    result_dataset['Value']=[round(element, 2) for element in grouped_trend_value_data['Value']]
    result_dataset['LowerCI']=[round(element, 2) for element in grouped_trend_lowerci_data['Lower CI 95.0 limit']]
    result_dataset['UpperCI']=[round(element, 2) for element in grouped_trend_upperci_data['Upper CI 95.0 limit']]
    result_dataset.insert(loc=0,column='Period',value=grouped_trend_value_data.index.tolist())
    region_dataset = get_entire_data_for_area(entire_dataset,region_name)
    region_dataset = get_entire_data_for_indicator(region_dataset,indicator_name)
    grouped_region_trend_value_data = get_grouped_trends_value_data(region_dataset).dropna()
    result_dataset[region_name]= [round(element, 2) for element in grouped_region_trend_value_data['Value']]
    england_dataset = get_entire_data_for_area(entire_dataset,'England')
    england_dataset = get_entire_data_for_indicator(england_dataset,indicator_name)
    grouped_england_trend_value_data = get_grouped_trends_value_data(england_dataset).dropna()
    result_dataset['England']= [round(element, 2) for element in grouped_england_trend_value_data['Value']]
    return result_dataset

#########################################################################COMPARE AREAS TAB##############################################################
###Compare areas data
def get_compare_areas_data(area_type,region,indicator_name,timeperiod):
    input_dataset = get_entire_data_for_region_timeperiod(area_type,region,timeperiod)
    output_dataset = pd.DataFrame()
    england_dataset = get_overview_data_for_area_timeperiod(area_type ,'England',timeperiod)
    england_dataset = england_dataset.loc[england_dataset['Indicator Name']==indicator_name]
    region_dataset = get_overview_data_for_area_timeperiod(area_type ,region, timeperiod)
    region_dataset = region_dataset.loc[region_dataset['Indicator Name']==indicator_name]
    input_indicator_dataset = input_dataset.loc[input_dataset['Indicator Name']==indicator_name]
    grouped_area_dataset = input_indicator_dataset.groupby(['Area Name'])['Value'].mean()
    output_dataset['Area']=['England',region]+grouped_area_dataset.index.tolist()
    output_dataset['Count']=pd.to_numeric(england_dataset.groupby(['Area Name']).size()).tolist()+pd.to_numeric(region_dataset.groupby(['Area Name']).size()).tolist()+pd.to_numeric(input_indicator_dataset.groupby(['Area Name']).size()).tolist()
    output_dataset['Value']=[round(element, 2) for element in pd.to_numeric(england_dataset.groupby(['Area Name'])['Value'].mean()).tolist()]+[round(element, 2) for element in pd.to_numeric(region_dataset.groupby(['Area Name'])['Value'].mean()).tolist()]+[round(element, 2) for element in pd.to_numeric(grouped_area_dataset).tolist()]
    output_dataset['95% Lower CI'] = [round(element, 2) for element in pd.to_numeric(england_dataset.groupby(['Area Name'])['Lower CI 95.0 limit'].mean()).tolist()]+[round(element, 2) for element in pd.to_numeric(region_dataset.groupby(['Area Name'])['Lower CI 95.0 limit'].mean()).tolist()]+[round(element, 2) for element in pd.to_numeric(input_indicator_dataset.groupby(['Area Name'])['Lower CI 95.0 limit'].mean()).tolist()]
    output_dataset['95% Upper CI'] = [round(element, 2) for element in pd.to_numeric(england_dataset.groupby(['Area Name'])['Upper CI 95.0 limit'].mean()).tolist()]+[round(element, 2) for element in pd.to_numeric(region_dataset.groupby(['Area Name'])['Upper CI 95.0 limit'].mean()).tolist()]+[round(element, 2) for element in pd.to_numeric(input_indicator_dataset.groupby(['Area Name'])['Upper CI 95.0 limit'].mean()).tolist()]
    return output_dataset


##########################################Ineqaulities Tab related methods#################################################################################
###Grouped Ineqaulities data for area
def get_grouped_inequlities_area_data(input_dataset):
    grouped_data_frame = pd.DataFrame(input_dataset.groupby(['Sex'])['Value'].mean())
    grouped_data_frame.insert(loc=0,column='Sex1',value=grouped_data_frame.index.tolist())
    return grouped_data_frame

###Grouped Ineqaulities data for England
def get_grouped_inequlities_england_data(input_dataset):
    grouped_data_frame = pd.DataFrame(input_dataset.groupby(['Category'])['Value'].mean())
    grouped_data_frame['Category']=grouped_data_frame.index.tolist()
    return grouped_data_frame

###returnds data set for inequalities area data
def get_inequalities_area_data(area_type, area_name, indicator_name, timeperiod):
    entire_dataset = get_entire_dataset(area_type)
    input_dataset = get_entire_data_for_area(entire_dataset,area_name)
    input_dataset = get_entire_data_for_timeperiod(input_dataset,timeperiod)
    input_dataset = get_entire_data_for_indicator(input_dataset,indicator_name)
    input_dataset = get_grouped_inequlities_area_data(input_dataset)
    input_dataset = input_dataset.dropna().sort_values(by=['Value'],ascending=False)
    result_dataset = pd.DataFrame()
    result_dataset['Sex'] = input_dataset['Sex1'].tolist()
    result_dataset['Value'] = [round(element, 2) for element in input_dataset['Value']]
    return result_dataset

###returnds data set for inequalities england data
def get_inequalities_england_data(area_type, indicator_name, timeperiod):
    entire_dataset = get_entire_dataset(area_type)
    input_dataset = get_entire_data_for_area(entire_dataset,'England')
    input_dataset = get_entire_data_for_timeperiod(input_dataset,timeperiod)
    input_dataset = get_entire_data_for_indicator(input_dataset,indicator_name)
    input_dataset = get_grouped_inequlities_england_data(input_dataset)
    input_dataset = input_dataset.dropna().sort_values(by=['Value'],ascending=False)
    result_dataset = pd.DataFrame()
    result_dataset['Category'] = input_dataset['Category'].tolist()
    result_dataset['Value'] = [round(element, 2) for element in input_dataset['Value']]
    return result_dataset


########################################################Population Tab related data####################################################################
###Grouped data for Population with age profile data
def get_grouped_age_profile_data(input_data):
    grouped_value_data_frame = pd.DataFrame(input_data.groupby(['Age','Sex'])['Indicator ID'].count()) 
    grouped_value_data_frame['Age_Profile']=grouped_value_data_frame.index.tolist()
    age = grouped_value_data_frame['Age_Profile'].apply(lambda x:x[0])
    sex= grouped_value_data_frame['Age_Profile'].apply(lambda x:x[1])
    grouped_value_data_frame['Age_range']=age
    grouped_value_data_frame['Male_Female']=sex 
    new_grouped_data_male_frame = grouped_value_data_frame.loc[grouped_value_data_frame['Male_Female']=='Male']
    new_grouped_data_female_frame = grouped_value_data_frame.loc[grouped_value_data_frame['Male_Female']=='Female']
    result_dataframe = pd.DataFrame()
    result_dataframe['Age_range'] = new_grouped_data_male_frame['Age_range'].tolist()
    result_dataframe['Male_Count'] = new_grouped_data_male_frame['Indicator ID'].tolist()
    result_dataframe['Female_Count'] = new_grouped_data_female_frame['Indicator ID'].tolist()
    return result_dataframe

###Get Area profile data for selected area and time period
def get_area_profiles_data(area_type,area_name,timeperiod):
    temp_dataset = get_overview_data_for_area_timeperiod(area_type ,area_name,timeperiod)
    temp_dataset = get_overview_grouped_data(temp_dataset)
    output_dataset = pd.DataFrame()
    output_dataset['Indicator'] =  temp_dataset['Indicator_Name']
    output_dataset.insert(loc=1, column='Period', value='2015 - 17') 
    output_dataset['Value'] = [round(element, 2) for element in temp_dataset['Value']]
    return output_dataset

#### Population related age profile data###########
def get_population_age_profile_data(area_type, area_name):
    entire_dataset = get_entire_dataset(area_type)
    input_dataset = get_entire_data_for_area(entire_dataset,area_name)  
    input_dataset = get_grouped_age_profile_data(input_dataset)
    return input_dataset
 
    
########################################################Box Plots Tab related###############################################################################
####Get Box Plot Indicator Data#################
def get_boxplot_indicator_data(area_type, region, indicator_name):
    input_dataset = get_entire_dataset(area_type)
    input_dataset = get_entire_data_for_region(input_dataset,region)
    input_dataset = get_entire_data_for_indicator(input_dataset,indicator_name)
    return get_grouped_region_indicator_data(input_dataset)

###Get Box Plot Data 
def get_boxplot_data_table(grouped_quantile_data):
    quantile_data_frame = pd.DataFrame()
    quantile_data_frame['Time Period'] = np.array(pd.DataFrame(grouped_quantile_data)[0])
    quantile_data_frame['Minimum'] = [round(element, 2) for element in grouped_quantile_data.quantile(q=0.00).tolist()]
    quantile_data_frame['5th Percentile'] = [round(element, 2) for element in grouped_quantile_data.quantile(q=0.05).tolist()]
    quantile_data_frame['25th Percentile'] = [round(element, 2) for element in grouped_quantile_data.quantile(q=0.25).tolist()]
    quantile_data_frame['Median'] = [round(element, 2) for element in grouped_quantile_data.quantile(q=0.5).tolist()]
    quantile_data_frame['75th Percentile'] = [round(element, 2) for element in grouped_quantile_data.quantile(q=0.75).tolist()]
    quantile_data_frame['95th Percentile'] = [round(element, 2) for element in grouped_quantile_data.quantile(q=0.95).tolist()]
    quantile_data_frame['Maximum'] = [round(element, 2) for element in grouped_quantile_data.quantile(q=1.00).tolist()]
    return quantile_data_frame.dropna()

def get_areas_for_region(area_type, region, timeperiod):
    input_dataset = get_entire_data_for_region_timeperiod(area_type,region,timeperiod)
    return input_dataset['Area Name'].dropna().unique().tolist()
    
#temp_dataset =  get_entire_dataset('DistrictUA')
#temp_dataset =  get_grouped_inequlities_england_data(get_entire_data_for_indicator(get_entire_data_for_timeperiod(get_entire_data_for_area(temp_dataset,'Leicester'),'2015 - 17'),'Suicide rate'))
#temp_dataset = get_inequalities_area_data('DistrictUA','Leicester','East Midlands region','Suicide rate','2015 - 17')
temp_dataset = get_population_age_profile_data('DistrictUA', 'Barnet')

