###Import all public health model methods
from public_health_data import get_population_age_profile_data,get_inequalities_england_data, get_region_overview_data, get_england_overview_data, get_entire_dataset,get_overview_indicators_list, get_entire_indicators_list,get_compare_indicators_data,get_compare_areas_data, get_area_profiles_data,get_areas_for_region,get_boxplot_indicator_data, get_boxplot_data_table, get_trends_data
####Import all required bokeh and other libraries
from bokeh.models.widgets import Panel, Tabs
from bokeh.layouts import layout
from bokeh.plotting import curdoc
from bokeh.models.widgets import Select, CheckboxButtonGroup, Paragraph
from bokeh.models import ColumnDataSource, CheckboxGroup,TableColumn,RadioButtonGroup,DataTable, HTMLTemplateFormatter, HoverTool,ResetTool, PanTool, BoxZoomTool, SaveTool
from bokeh.plotting import figure
from bokeh.models.widgets import PasswordInput, TextInput, PreText, Button
from bokeh.layouts import column, row
from bokeh.models.widgets import Div
from bokeh.palettes import Spectral6
###Import pandas and numpy libraries for data processing
import pandas as pd
import numpy as np
######Library for LinearRegression########################################
from sklearn.linear_model import LinearRegression
#####Import library to find rsquare score for linear regression###########
from sklearn.metrics import r2_score

###INITIALIZE TEMPLATE TO FORMAT TABLE DATA#########################################################
template="""
            <div style="background:<%= 
                (function colorfromint(){
                    if(value.split(",")[2]=="Worse"){
                            return("#FF6133")}
                    if(value.split(",")[2]=="Better"){
                            return("#B0EC6F")}
                    if(value.split(",")[2]=="Similar"){
                            return("#FFC300")}
                    }()) %>; 
                color: black;font-size:15px;"> 
                <% if(value!='2015 - 17'){
                     if (Indicator=='Life expectancy at birth Male' || Indicator=='Life expectancy at birth Life expectancy at birth Female' ) {%>
                        <span href="#" class ="highlightme" data-toggle="tooltip" title="<%=value.split(",")[1] %> \n <%= value.split(",",1) %> Years\n\n<%= Indicator %>"><a href="" target=""><%= value.split(",",1) %> </a></span>
                        <%}
                         else {%>
                                  <span href="#" class ="highlightme" data-toggle="tooltip" title="<%=value.split(",")[1] %> \n <%= value.split(",",1) %> per 100,000\n\n<%= Indicator %>"><a href="" target=""><%= value.split(",",1) %> </a></span>
                                  <%}
                         }  
                             else {%>
                                   <span href="#" class ="highlightme"><%= value%> </span>
                                   <%}%>
                    </div>
            """
table_template =""" 
                <div style="color: black;font-size:15px;"> <%=value%></div>
            """

####Hover tool tip
hover = HoverTool(tooltips=[
    ("index", "$index"),
    ("x", "@x per 100,000"),
    ("y", "@y per 1000"),
    ('desc', '@desc'),
])

tools = [hover, BoxZoomTool(), PanTool(), ResetTool(), SaveTool()]
########################################BOKEH CALL BACK METHODS FOR DIFFERENT ACTIONS AND EVENTS################################################################
################################################################################################################################################################
####Overview Tab related bokeh call back methods################################################################################################################
def overview_area_type_on_change(attr, old, new):
    print(overview_area_type_select.value)
    if(overview_area_type_select.value=='Region'):
        overview_regions_select.visible = False
        return None
    else:
        overview_regions_select.visible = True
        region_areas = get_entire_dataset(overview_area_type_select.value)
        regions_list = region_areas.loc[region_areas['Parent Name']!='England']['Parent Name'].dropna().unique().tolist()
        print(areas_list)
        overview_regions_select.value = regions_list[0]
        overview_regions_select.options = regions_list
        temp_dataset = get_region_overview_data(overview_area_type_select.value, overview_regions_select.value,'2015 - 17')
        print(temp_dataset)
        Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=template)) for Ci in temp_dataset.columns]
        overview_data_table.columns = Columns
        overview_data_table.source = ColumnDataSource(temp_dataset)
        overview_data_table.update()
 
def overview_areas_grouped_by_on_change(attr, old, new):
    print(overview_area_grouped_by_select.value)
    
def overview_regions_on_change(attr, old, new):
    areas_list = get_areas_for_region(overview_area_type_select.value,overview_regions_select.value,'2015 - 17')
    # Select options for Areas in region
    overview_areas_of_region_select.value  =  areas_list[0]
    overview_areas_of_region_select.options  =  areas_list
    temp_dataset = get_region_overview_data(overview_area_type_select.value, overview_regions_select.value,'2015 - 17')
    print(temp_dataset)
    Columns = [TableColumn(field=Ci, title=Ci, width=100, formatter=HTMLTemplateFormatter(template=template)) for Ci in temp_dataset.columns]
    overview_data_table.columns = Columns
    overview_data_table.source = ColumnDataSource(temp_dataset)
    overview_data_table.update()

####################################################################################################################################################
####Compare Indicators Tab related bokeh call back methods##########################################################################################    
def compare_indicators_area_type_on_change(attr, old, new):
    print(compare_indicators_area_type_select.value)
    if(compare_indicators_area_type_select.value=='Region'):
        compare_indicators_region_select.visible = False
        return None
    else:
        compare_indicators_region_select.visible = True
        region_areas = get_entire_dataset(compare_indicators_area_type_select.value)
        areas_list = region_areas.loc[region_areas['Parent Name']!='England']['Parent Name'].dropna().unique().tolist()
        print(areas_list)
        compare_indicators_region_select.value = regions_list[0]
        compare_indicators_region_select.options = regions_list  
        result_dataset1 = get_compare_indicators_data(compare_indicators_area_type_select.value, 
                                compare_indicators_region_select.value, 
                                compare_x_indicator_select.value,
                                compare_y_indicator_select.value,
                                '2015 - 17')
        print("inside compare_indicators_area_type_on_change....")
        regression_plot.xaxis.axis_label = compare_x_indicator_select.value
        regression_plot.yaxis.axis_label = compare_y_indicator_select.value
        # add a circle renderer with a size, color, and alpha
        regressor1 = LinearRegression()
        regressor1.fit(np.array(result_dataset['X'])[:, np.newaxis], np.array(result_dataset['Y'])[:, np.newaxis])
        regression_circle_source.data = dict(x=result_dataset1['X'], y=result_dataset1['Y'])
        regression_line_source.data = dict(x=np.array(result_dataset1['X'])[:, np.newaxis], y=regressor1.predict(np.array(result_dataset1['X'].tolist())[:, np.newaxis]))
     
def compare_indicator_areas_grouped_by_on_change(attr, old, new):
    print(compare_indicators_area_grouped_by_select.value)
    
def compare_indicators_area_on_change(attr, old, new):
    compare_indicators_chekbox.labels[0] = "Highlight "+compare_indicators_area_select.value
    
def compare_indicators_region_on_change(attr, old, new):
    print(compare_indicators_region_select.value)
    areas_list = get_areas_for_region(compare_indicators_area_type_select.value,compare_indicators_region_select.value,'2015 - 17')
    # Select options for Areas in region
    compare_indicators_area_select.value  =  areas_list[0]
    compare_indicators_area_select.options  =  areas_list
    result_dataset1 = get_compare_indicators_data(compare_indicators_area_type_select.value, 
                                compare_indicators_region_select.value, 
                                compare_x_indicator_select.value,
                                compare_y_indicator_select.value,
                                '2015 - 17')
    print("inside compare_indicator_areas_grouped_by_on_change")
    regression_plot.xaxis.axis_label = compare_x_indicator_select.value
    regression_plot.yaxis.axis_label = compare_y_indicator_select.value
    print(result_dataset1)
    compare_all_indicators_button_group.labels[0] = "All in "+compare_indicators_region_select.value
    # add a circle renderer with a size, color, and alpha
    regressor1 = LinearRegression()
    regressor1.fit(np.array(result_dataset1['X'])[:, np.newaxis], np.array(result_dataset1['Y'])[:, np.newaxis])
    regression_circle_source.data = dict(x=result_dataset1['X'], y=result_dataset1['Y'])
    regression_line_source.data = dict(x=np.array(result_dataset1['X'])[:, np.newaxis], y=regressor1.predict(np.array(result_dataset1['X'].tolist())[:, np.newaxis]))
    coefficient_of_dermination = r2_score(result_dataset1['Y'], regressor1.predict(np.array(result_dataset1['X'].tolist())[:, np.newaxis]))
    paragraph_coeff.text = str(regressor1.coef_[0][0])+"""x+"""+str(regressor1.intercept_[0])+"""R²="""+str(coefficient_of_dermination)

def compare_indicator_checkbox_onchange(attr, old, new):
    result_dataset1 = get_compare_indicators_data(compare_indicators_area_type_select.value, 
                            compare_indicators_region_select.value,
                            compare_x_indicator_select.value,
                            compare_y_indicator_select.value,
                            '2015 - 17')
    lines_to_plot = [compare_indicators_chekbox.labels[i] for i in compare_indicators_chekbox.active]
    print(lines_to_plot)
    regression_plot.xaxis.axis_label = compare_x_indicator_select.value
    regression_plot.yaxis.axis_label = compare_y_indicator_select.value
    regression_line.visible  =   'Add regression line & R²' in lines_to_plot 
    regressor1 = LinearRegression()
    regressor1.fit(np.array(result_dataset1['X'])[:, np.newaxis], np.array(result_dataset1['Y'])[:, np.newaxis])
    coefficient_of_dermination = r2_score(result_dataset1['Y'], regressor1.predict(np.array(result_dataset1['X'].tolist())[:, np.newaxis]))
    print(regressor1.intercept_[0])
    if(coefficient_of_dermination > 0.15):
        paragraph_reg_exp.text = """Regression Equation="""+str(regressor1.coef_[0][0])+"""x+"""+str(regressor1.intercept_[0])
        paragraph_coeff.text = """R²="""+str(coefficient_of_dermination)
        regression_line.visible = 'Add regression line & R²' in lines_to_plot 
        paragraph_coeff.visible = 'Add regression line & R²' in lines_to_plot 
        paragraph_reg_exp.visible = 'Add regression line & R²' in lines_to_plot   
    else: 
        paragraph_coeff.text ="""Trend line not drawn when \n R2 is below 0.15(R²="""+str(coefficient_of_dermination)+""")"""
        paragraph_coeff.visible = 'Add regression line & R²' in lines_to_plot 
        paragraph_reg_exp.visible = 'Add regression line & R²' in lines_to_plot        
        regression_line.visible = False

def compare_y_indicator_on_change(attr, old, new):
    lines_to_plot = [compare_indicators_chekbox.labels[i] for i in compare_indicators_chekbox.active]
    print(compare_y_indicator_select.value)
    result_dataset1 = get_compare_indicators_data(compare_indicators_area_type_select.value, 
                                compare_indicators_region_select.value, 
                                compare_x_indicator_select.value,
                                compare_y_indicator_select.value,
                                '2015 - 17')
    print("inside compare_y_indicator_on_change")
    print(result_dataset1)
    regression_plot.xaxis.axis_label = compare_x_indicator_select.value
    regression_plot.yaxis.axis_label = compare_y_indicator_select.value
    # add a circle renderer with a size, color, and alpha
    regressor1 = LinearRegression()
    regressor1.fit(np.array(result_dataset1['X'])[:, np.newaxis], np.array(result_dataset1['Y'])[:, np.newaxis])
    print(regressor1.intercept_[0])
    regression_circle_source.data = dict(x=result_dataset1['X'], y=result_dataset1['Y'])
    regression_line_source.data = dict(x=np.array(result_dataset1['X'])[:, np.newaxis], y=regressor1.predict(np.array(result_dataset1['X'].tolist())[:, np.newaxis]))
    coefficient_of_dermination = r2_score(result_dataset1['Y'], regressor1.predict(np.array(result_dataset1['X'].tolist())[:, np.newaxis]))
    if(coefficient_of_dermination > 0.15):
        paragraph_reg_exp.text = """Regression Equation="""+str(regressor1.coef_[0][0])+"""x+"""+str(regressor1.intercept_[0])
        paragraph_coeff.text = """R²="""+str(coefficient_of_dermination)
        regression_line.visible = 'Add regression line & R²' in lines_to_plot 
        paragraph_coeff.visible = 'Add regression line & R²' in lines_to_plot 
        paragraph_reg_exp.visible = 'Add regression line & R²' in lines_to_plot   
    else: 
        paragraph_coeff.text ="""Trend line not drawn when \n R2 is below 0.15(R²="""+str(coefficient_of_dermination)+""")"""
        paragraph_coeff.visible = 'Add regression line & R²' in lines_to_plot 
        paragraph_reg_exp.visible = 'Add regression line & R²' in lines_to_plot        
        regression_line.visible = False

    
def compare_x_indicator_on_change(attr, old, new):
    print(compare_x_indicator_select.value)
    result_dataset1 = get_compare_indicators_data(compare_indicators_area_type_select.value, 
                                compare_indicators_region_select.value, 
                                compare_x_indicator_select.value,
                                compare_y_indicator_select.value,
                                '2015 - 17')
    print("inside compare_indicator_areas_grouped_by_on_change")
    print(result_dataset1)
    regression_plot.xaxis.axis_label = compare_x_indicator_select.value
    regression_plot.yaxis.axis_label = compare_y_indicator_select.value
    regressor1 = LinearRegression()
    regressor1.fit(np.array(result_dataset1['X'])[:, np.newaxis], np.array(result_dataset1['Y'])[:, np.newaxis])
    print(regressor1.intercept_[0])
    regression_circle_source.data = dict(x=result_dataset1['X'], y=result_dataset1['Y'])
    regression_line_source.data = dict(x=np.array(result_dataset1['X'])[:, np.newaxis], y=regressor1.predict(np.array(result_dataset1['X'].tolist())[:, np.newaxis]))
    coefficient_of_dermination = r2_score(result_dataset1['Y'], regressor1.predict(np.array(result_dataset1['X'].tolist())[:, np.newaxis]))
    if(coefficient_of_dermination > 0.15):
        paragraph_reg_exp.text = """Regression Equation="""+str(regressor1.coef_[0][0])+"""x+"""+str(regressor1.intercept_[0])
        paragraph_coeff.text = """R²="""+str(coefficient_of_dermination)
        regression_line.visible = 'Add regression line & R²' in lines_to_plot 
        paragraph_coeff.visible = 'Add regression line & R²' in lines_to_plot 
        paragraph_reg_exp.visible = 'Add regression line & R²' in lines_to_plot   
    else: 
        paragraph_coeff.text ="""Trend line not drawn when \n R2 is below 0.15(R²="""+str(coefficient_of_dermination)+""")"""
        paragraph_coeff.visible = 'Add regression line & R²' in lines_to_plot 
        paragraph_reg_exp.visible = 'Add regression line & R²' in lines_to_plot        
        regression_line.visible = False

def compare_all_indicators_button_group_on_change(attr, old, new):
    result_dataset1 = None
    if(compare_all_indicators_button_group.active==1):
        result_dataset1 = get_compare_indicators_data(compare_indicators_area_type_select.value, 
                                    "England", 
                                    compare_x_indicator_select.value,
                                    compare_y_indicator_select.value,
                                    '2015 - 17')
        print("inside compare_y_indicator_on_change")
    if(compare_all_indicators_button_group.active==0):
        result_dataset1 = get_compare_indicators_data(compare_indicators_area_type_select.value, 
                                    compare_indicators_region_select.value, 
                                    compare_x_indicator_select.value,
                                    compare_y_indicator_select.value,
                                    '2015 - 17')
        print("inside compare_y_indicator_on_change")
    print(result_dataset1)    
    regression_plot.xaxis.axis_label = compare_x_indicator_select.value
    regression_plot.yaxis.axis_label = compare_y_indicator_select.value
    # add a circle renderer with a size, color, and alpha
    regressor1 = LinearRegression()
    regressor1.fit(np.array(result_dataset1['X'])[:, np.newaxis], np.array(result_dataset1['Y'])[:, np.newaxis])
    print(regressor1.intercept_[0])
    regression_circle_source.data = dict(x=result_dataset1['X'], y=result_dataset1['Y'])
    regression_line_source.data = dict(x=np.array(result_dataset1['X'])[:, np.newaxis], y=regressor1.predict(np.array(result_dataset1['X'].tolist())[:, np.newaxis]))
    coefficient_of_dermination = r2_score(result_dataset1['Y'], regressor1.predict(np.array(result_dataset1['X'].tolist())[:, np.newaxis]))
    if(coefficient_of_dermination > 0.15):
        paragraph_reg_exp.text = """Regression Equation="""+str(regressor1.coef_[0][0])+"""x+"""+str(regressor1.intercept_[0])
        paragraph_coeff.text = """R²="""+str(coefficient_of_dermination)
        regression_line.visible = 'Add regression line & R²' in lines_to_plot 
    else: 
        paragraph_coeff.text ="""Trend line not drawn when \n R2 is below 0.15(R²="""+str(coefficient_of_dermination)+""")"""
        paragraph_coeff.visible = 'Add regression line & R²' in lines_to_plot 
        paragraph_reg_exp.visible = 'Add regression line & R²' in lines_to_plot        
        regression_line.visible = False
####################################################################################################################################################        
####Trends Tab related bokeh call back methods######################################################################################################      
def trends_area_type_on_change(attr, old, new):
    print(trends_area_type_select.value)
    if(trends_area_type_select.value=='Region'):
        trends_region_select.visible = False
        return None
    else:
        trends_region_select.visible = True
        trends_regions_list = region_areas.loc[region_areas['Parent Name']!='England']['Parent Name'].dropna().unique().tolist() 
        trends_region_select.value = trends_regions_list[0]
        trends_region_select.options = trends_regions_list     
        areas_list = get_areas_for_region(trends_area_type_select.value,trends_region_select.value,'2015 - 17') 
        trends_area_select.value = areas_list[0]
        trends_area_select.options = areas_list
        trends_indicators_list = get_overview_indicators_list(trends_area_type_select.value, trends_region_select.value,'2015 - 17')
        trends_indicator_select.value = trends_indicators_list[0]
        trends_indicator_select.options = trends_indicators_list
        trends_result_dataset1 = get_trends_data(trends_area_type_select.value, 
                                        trends_area_select.value, 
                                        trends_region_select.value,
                                        trends_indicator_select.value)        
        trends_plot = figure(plot_width=600, plot_height=400)
        trends_plot.line(trends_result_dataset1['Period'].tolist(), trends_result_dataset1['Value'].tolist(), line_width=3)
        Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in trends_result_dataset1.columns] # bokeh columns
        trends_data_table.columns = Columns
        trends_data_table.source = ColumnDataSource(trends_result_dataset1)
        trends_data_table.update()
        trends_area_line_source.data = dict(x=trends_result_dataset1.index.tolist(), y=trends_result_dataset1['Value'].tolist())
        trends_england_line_source.data = dict(x=trends_result_dataset1.index.tolist(), y=trends_result_dataset['England'].tolist())
        
def trends_region_on_change(attr, old, new):   
    areas_list = get_areas_for_region(trends_area_type_select.value,trends_region_select.value,'2015 - 17') 
    trends_area_select.value = areas_list[0]
    trends_area_select.options = areas_list
    trends_indicators_list = get_overview_indicators_list(trends_area_type_select.value, trends_region_select.value,'2015 - 17')
    trends_indicator_select.value = trends_indicators_list[0]
    trends_indicator_select.options = trends_indicators_list
    trends_result_dataset1 = get_trends_data(trends_area_type_select.value, 
                                    trends_area_select.value, 
                                    trends_region_select.value,
                                    trends_indicator_select.value)        
    trends_plot = figure(plot_width=600, plot_height=400)
    trends_plot.line(trends_result_dataset1['Period'].tolist(), trends_result_dataset1['Value'].tolist(), line_width=3)
    Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in trends_result_dataset1.columns] # bokeh columns
    trends_data_table.columns = Columns
    trends_data_table.source = ColumnDataSource(trends_result_dataset1)
    trends_data_table.update()
    trends_area_line_source.data = dict(x=trends_result_dataset1.index.tolist(), y=trends_result_dataset1['Value'].tolist())
    trends_england_line_source.data = dict(x=trends_result_dataset1.index.tolist(), y=trends_result_dataset['England'].tolist())
    
        
def trends_area_on_change(attr, old, new):
    trends_indicators_list = get_overview_indicators_list(trends_area_type_select.value, trends_region_select.value,'2015 - 17')
    trends_indicator_select.value = trends_indicators_list[0]
    trends_indicator_select.options = trends_indicators_list
    trends_result_dataset1 = get_trends_data(trends_area_type_select.value, 
                                    trends_area_select.value, 
                                    trends_region_select.value,
                                    trends_indicator_select.value)        
    trends_plot = figure(plot_width=600, plot_height=400)
    trends_plot.line(trends_result_dataset1['Period'].tolist(), trends_result_dataset1['Value'].tolist(), line_width=3)
    Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in trends_result_dataset1.columns] # bokeh columns
    trends_data_table.columns = Columns
    trends_data_table.source = ColumnDataSource(trends_result_dataset1)
    trends_data_table.update() 
    trends_area_line_source.data = dict(x=trends_result_dataset1.index.tolist(), y=trends_result_dataset1['Value'].tolist())
    trends_england_line_source.data = dict(x=trends_result_dataset1.index.tolist(), y=trends_result_dataset['England'].tolist())

    
def trends_indicator_on_change(attr, old, new):
    trends_result_dataset1 = get_trends_data(trends_area_type_select.value, 
                                    trends_area_select.value, 
                                    trends_region_select.value,
                                    trends_indicator_select.value)        
    trends_plot = figure(plot_width=600, plot_height=400)
    trends_plot.line(trends_result_dataset1['Period'].tolist(), trends_result_dataset1['Value'].tolist(), line_width=3)
    Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in trends_result_dataset1.columns] # bokeh columns
    trends_data_table.columns = Columns
    trends_data_table.source = ColumnDataSource(trends_result_dataset1)
    trends_data_table.update() 
    trends_area_line_source.data = dict(x=trends_result_dataset1.index.tolist(), y=trends_result_dataset1['Value'].tolist())
    trends_england_line_source.data = dict(x=trends_result_dataset1.index.tolist(), y=trends_result_dataset['England'].tolist())

####################################################################################################################################################
####Compare areas Tab related bokeh call back methods###############################################################################################     
def compare_areas_area_type_on_change(attr, old, new):
    print(compare_indicators_area_type_select.value)
    if(compare_areas_area_type_select.value=='Region'):
        compare_areas_areas_in_region_select.visible = False
        return None
    else:
        compare_areas_areas_in_region_select.visible = True
        region_areas = get_entire_dataset(compare_indicators_area_type_select.value)
        areas_list = region_areas.loc[region_areas['Parent Name']!='England']['Parent Name'].dropna().unique().tolist()
        print(areas_list)
        compare_areas_areas_in_region_select.value = areas_list[0]
        compare_areas_areas_in_region_select.options = areas_list  
        result_dataset1 = get_compare_areas_data(compare_areas_area_type_select.value, 
                                    compare_areas_areas_in_region_select.value, 
                                    compare_areas_indicator_select.value,
                                    '2015 - 17')
        Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in result_dataset1.columns] # bokeh columns
        compare_areas_data_table.columns = Columns
        compare_areas_data_table.source = ColumnDataSource(result_dataset1)
        compare_areas_data_table.update()

def compare_areas_areas_in_region_on_change(attr, old, new):
    result_dataset1 = get_compare_areas_data(compare_areas_area_type_select.value, 
                                compare_areas_areas_in_region_select.value, 
                                compare_areas_indicator_select.value,
                                '2015 - 17')
    compare_areas_indicators_button_group.labels[0] = "All in "+compare_areas_areas_in_region_select.value
    Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in result_dataset1.columns] # bokeh columns
    compare_areas_data_table.columns = Columns
    compare_areas_data_table.source = ColumnDataSource(result_dataset1)
    compare_areas_data_table.update()

   
def compare_areas_indicator_on_change(attr, old, new):
    result_dataset1 = get_compare_areas_data(compare_areas_area_type_select.value, 
                                compare_areas_areas_in_region_select.value, 
                                compare_areas_indicator_select.value,
                                '2015 - 17')
    compare_areas_indicators_button_group.labels[0] = "All in "+compare_areas_areas_in_region_select.value
    Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in result_dataset1.columns] # bokeh columns
    compare_areas_data_table.columns = Columns
    compare_areas_data_table.source = ColumnDataSource(result_dataset1)
    compare_areas_data_table.update()
    
####################################################################################################################################################
####Area Profiles Tab related bokeh call back methods###############################################################################################    
def area_profiles_area_type_on_change(attr, old, new):
    if(area_profiles_area_type_select.value=='Region'):
        area_profiles_areas_in_region_select.visible = False
        return None
    else:
        area_profiles_areas_in_region_select.visible = True
        area_profiles_dataset = get_area_profiles_data(area_profiles_area_type_select.value,area_profiles_areas_of_region_select.value,'2015 - 17')
        Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in area_profiles_dataset.columns] # bokeh columns
        area_profiles_data_table.columns = Columns
        area_profiles_data_table.source = ColumnDataSource(area_profiles_dataset)
        area_profiles_data_table.update()

def area_profiles_areas_in_region_on_change(attr, old, new):
    areas_list = get_areas_for_region(area_profiles_area_type_select.value,area_profiles_areas_in_region_select.value,'2015 - 17')
    # Select options for Areas in region
    area_profiles_areas_of_region_select.value  =  areas_list[0]
    area_profiles_areas_of_region_select.options  =  areas_list
    area_profiles_dataset = get_area_profiles_data(area_profiles_area_type_select.value,area_profiles_areas_of_region_select.value,'2015 - 17')
    Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in area_profiles_dataset.columns] # bokeh columns
    area_profiles_data_table.columns = Columns
    area_profiles_data_table.source = ColumnDataSource(area_profiles_dataset)
    area_profiles_data_table.update()

def area_profiles_areas_of_region_on_change(attr, old, new):
    area_profiles_dataset = get_area_profiles_data(area_profiles_area_type_select.value,area_profiles_areas_of_region_select.value,'2015 - 17')
    Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in area_profiles_dataset.columns] # bokeh columns
    area_profiles_data_table.columns = Columns
    area_profiles_data_table.source = ColumnDataSource(area_profiles_dataset)
    area_profiles_data_table.update()    

####################################################################################################################################################
####Inequalities Tab related bokeh call back methods################################################################################################     
def inequalities_area_type_on_change(attr, old, new):
    print(compare_indicators_area_type_select.value)
    if(inequalities_area_type_select.value=='Region'):
        inequalities_regions_select.visible = False
        return None
    else:
        inequalities_regions_select.visible = True
        region_areas = get_entire_dataset(overview_area_type_select.value)
        regions_list = region_areas.loc[region_areas['Parent Name']!='England']['Parent Name'].dropna().unique().tolist()
        inequalities.value = regions_list[0]
        inequalities_regions_select.options = regions_list
        areas_list = get_areas_for_region(inequalities_area_type_select.value,inequalities_regions_select.value,'2015 - 17')
        # Select options for Areas in region
        inequalities_areas_select.value  =  areas_list[0]
        inequalities_areas_select.options  =  areas_list 
        result_dataset1 = get_inequalities_england_data(inequalities_area_type_select.value, 
                            inequalities_indicator_select.value,
                            '2015 - 17')
        print(result_dataset1)
        Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in result_dataset1.columns] # bokeh columns
        inequalities_data_table.columns = Columns
        inequalities_data_table.source = ColumnDataSource(result_dataset1)
        inequalities_data_table.update()
        categories = result_dataset1['Category'].tolist()
        values = [float(i) for i in result_dataset1['Value'].tolist()]
        source.data.update(dict(categories=categories, values=values, color=Spectral6))
        inequalities_plot = figure(x_range=categories, y_range=(int(min(values))-5,int(max(values))+5),plot_height=450, title=inequalities_indicator_select.value,
                   toolbar_location=None, tools="",plot_width=700)    
        inequalities_plot.vbar(x='categories', top='values', width=0.3, color='color', legend="values", source=source)   
        inequalities_plot.xgrid.grid_line_color = None
        inequalities_plot.legend.orientation = "horizontal"
        inequalities_plot.legend.location = "top_center"
        inequalities_plot.xaxis.major_label_orientation = "vertical"
        
def inequalities_regions_on_change(attr, old, new):
    areas_list = get_areas_for_region(inequalities_area_type_select.value,inequalities_regions_select.value,'2015 - 17')
    # Select options for Areas in region
    inequalities_areas_select.value  =  areas_list[0]
    inequalities_areas_select.options  =  areas_list
    result_dataset1 = get_inequalities_england_data(inequalities_area_type_select.value, 
                            inequalities_indicator_select.value,
                            '2015 - 17')
    print(result_dataset1)
    Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in result_dataset1.columns] # bokeh columns
    inequalities_data_table.columns = Columns
    inequalities_data_table.source = ColumnDataSource(result_dataset1)
    inequalities_data_table.update()
    categories = result_dataset1['Category'].tolist()
    values = [float(i) for i in result_dataset1['Value'].tolist()]
    print(min(values))
    source.data.update(dict(categories=categories, values=values, color=Spectral6))
    inequalities_plot = figure(x_range=categories, y_range=(int(min(values))-5,int(max(values))+5),plot_height=450, title=inequalities_indicator_select.value,
               toolbar_location=None, tools="",plot_width=700)    
    inequalities_plot.vbar(x='categories', top='values', width=0.3, color='color', legend="values", source=source)   
    inequalities_plot.xgrid.grid_line_color = None
    inequalities_plot.legend.orientation = "horizontal"
    inequalities_plot.legend.location = "top_center"
    inequalities_plot.xaxis.major_label_orientation = "vertical"
    
def inequalities_areas_on_change(attr, old, new):
    result_dataset1 = get_inequalities_england_data(inequalities_area_type_select.value, 
                            inequalities_indicator_select.value,
                            '2015 - 17')
    print(result_dataset1)
    inequalities_areas_button_group.labels[1] = inequalities_areas_select.value
    Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in result_dataset1.columns] # bokeh columns
    inequalities_data_table.columns = Columns
    inequalities_data_table.source = ColumnDataSource(result_dataset1)
    inequalities_data_table.update()
    categories = result_dataset1['Category'].tolist()
    values = [float(i) for i in result_dataset1['Value'].tolist()]
    print(min(values))
    source.data.update(dict(categories=categories, values=values, color=Spectral6))
    inequalities_plot = figure(x_range=categories, y_range=(int(min(values))-5,int(max(values))+5),plot_height=450, title=inequalities_indicator_select.value,
               toolbar_location=None, tools="",plot_width=700)    
    inequalities_plot.vbar(x='categories', top='values', width=0.3, color='color', legend="values", source=source)   
    inequalities_plot.xgrid.grid_line_color = None
    inequalities_plot.legend.orientation = "horizontal"
    inequalities_plot.legend.location = "top_center"
    inequalities_plot.xaxis.major_label_orientation = "vertical"
    inequalities_plot.y_range = (int(min(values))-5,int(max(values))+5)
    
def inequalities_indicator_on_change(attr, old, new):
    result_dataset1 = get_inequalities_england_data(inequalities_area_type_select.value, 
                            inequalities_indicator_select.value,
                            '2015 - 17')
    print(result_dataset1)
    inequalities_areas_button_group.labels[1] = inequalities_areas_select.value
    Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in result_dataset1.columns] # bokeh columns
    inequalities_data_table.columns = Columns
    inequalities_data_table.source = ColumnDataSource(result_dataset1)
    inequalities_data_table.update()
    categories = result_dataset1['Category'].tolist()
    values = [float(i) for i in result_dataset1['Value'].tolist()]
    print(min(values))
    source.data.update(dict(categories=categories, values=values, color=Spectral6))
    inequalities_plot = figure(x_range=categories, y_range=(int(min(values))-5,int(max(values))+5),plot_height=450, title=inequalities_indicator_select.value,
               toolbar_location=None, tools="",plot_width=700)    
    inequalities_plot.vbar(x='categories', top='values', width=0.3, color='color', legend="values", source=source)   
    inequalities_plot.xgrid.grid_line_color = None
    inequalities_plot.legend.orientation = "horizontal"
    inequalities_plot.legend.location = "top_center"
    inequalities_plot.xaxis.major_label_orientation = "vertical"
    inequalities_plot.y_range = (int(min(values))-5,int(max(values))+5)
       
def inequalities_areas_button_group_on_change(attr, old, new):
    print(inequalities_areas_button_group.labels)

#######################################################################################################################################################      
####England Tab related bokeh call back methods##########################################################################################        
def england_area_type_on_change(attr, old, new):
    temp_dataset1 = get_england_overview_data(england_area_type_select.value,'England','2015 - 17').iloc[:,[0,1,2]]
    Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in temp_dataset1.columns] # bokeh columns
    england_data_table.columns = Columns
    england_data_table.source = ColumnDataSource(temp_dataset1)
    england_data_table.update()

#######################################################################################################################################################  
####Population Tab related bokeh call back methods#####################################################################################################  
def population_area_type_on_change(attr, old, new):
    print(population_regions_select.value)
    if(population_regions_select.value=='Region'):
        population_regions_select.visible = False
        return None
    else:
        population_regions_select.visible = True
        regions = get_entire_dataset(overview_area_type_select.value)
        regions_list = regions.loc[region_areas['Parent Name']!='England']['Parent Name'].dropna().unique().tolist()
        population_regions_select.value = regions_list[0]
        population_regions_select.options = regions_list
        temp_dataset = get_population_age_profile_data(population_area_type_select.value,population_areas_select.value)
        Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in temp_dataset.columns] # bokeh columns
        population_data_table.columns = Columns
        population_data_table.source = ColumnDataSource(temp_dataset)
        population_data_table.update()
  
def population_grouped_by_on_change(attr, old, new):
    None
    
def population_regions_on_change(attr, old, new): 
    areas_list = get_areas_for_region(population_area_type_select.value,population_regions_select.value,'2015 - 17') 
    population_areas_select.value = areas_list[0]
    population_areas_select.options = areas_list
    temp_dataset = get_population_age_profile_data(population_area_type_select.value,population_areas_select.value)
    Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in temp_dataset.columns] # bokeh columns
    population_data_table.columns = Columns
    population_data_table.source = ColumnDataSource(temp_dataset)
    population_data_table.update()
    
def population_areas_on_change(attr, old, new): 
    print("Inside population_areas_on_change")
    temp_dataset = get_population_age_profile_data(population_area_type_select.value,population_areas_select.value)
    print(temp_dataset)
    Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in temp_dataset.columns] # bokeh columns
    population_data_table.columns = Columns
    population_data_table.source = ColumnDataSource(temp_dataset)
    population_data_table.update()

####################################################################################################################################################################  
####Box Plots Tab related bokeh call back methods###################################################################################################################       
def box_plots_area_type_on_change(attr, old, new):
    print("inside box_plots_area_type_on_change....")
    print(box_plots_area_type_select.value)
    print(box_plots_areas_in_region_select.value)
    print(box_plots_indicator_select.value)
    if(box_plots_area_type_select.value=='Region'):
        box_plots_areas_in_region_select.visible = False
        return None
    else:
        box_plots_areas_in_region_select.visible = True
        region_areas = get_entire_dataset(box_plots_area_type_select.value)
        areas_list = region_areas.loc[region_areas['Parent Name']!='England']['Parent Name'].dropna().unique().tolist()
        print(areas_list)
        box_plots_areas_in_region_select.value = areas_list[0]
        box_plots_areas_in_region_select.options = areas_list  
        grouped_quartile_data1 = get_boxplot_indicator_data(box_plots_area_type_select.value,box_plots_areas_in_region_select.value,box_plots_indicator_select.value)
        box_plot_dataset1 = get_boxplot_data_table(grouped_quartile_data1)
        print(box_plot_dataset1['Minimum'])       
        quantile_min = pd.DataFrame(grouped_quartile_data1.quantile(q=0.00).dropna())
        quantile_1 = pd.DataFrame(grouped_quartile_data1.quantile(q=0.25).dropna())
        quantile_2 = pd.DataFrame(grouped_quartile_data1.quantile(q=0.5).dropna())
        quantile_3 = pd.DataFrame(grouped_quartile_data1.quantile(q=0.75).dropna())
        quantile_max = pd.DataFrame(grouped_quartile_data1.quantile(q=1.00).dropna())         
        iqr = quantile_3-quantile_1
        upper = quantile_3 + 1.5 * iqr
        lower = quantile_1 - 5.5 * iqr       
        upper.Value = [min([x,y]) for (x,y) in zip(list(quantile_max.loc[:,'Value']),upper.Value)]
        lower.Value = [max([x,y]) for (x,y) in zip(list(quantile_min.loc[:,'Value']),lower.Value)] 
        time_period_list1 = box_plot_dataset['Time Period'].dropna().tolist()      
        box_plots = figure(tools=tools, background_fill_color="#efefef", x_range=time_period_list, toolbar_location=None)        
        box_plots.segment(time_period_list1, upper.Value, time_period_list1, quantile_3.Value, line_color="black")
        box_plots.segment(time_period_list1, lower.Value, time_period_list1, quantile_1.Value, line_color="black")       
        box_plots.vbar(time_period_list1, 0.7, quantile_2.Value, quantile_3.Value, fill_color="#E08E79", line_color="black")
        box_plots.vbar(time_period_list1, 0.7, quantile_1.Value, quantile_2.Value, fill_color="#3B8686", line_color="black")       
        box_plots.rect(time_period_list1, lower.Value, 0.2, 0.01, line_color="black")
        box_plots.rect(time_period_list1, upper.Value, 0.2, 0.01, line_color="black")                                 
        box_plots.xgrid.grid_line_color = None
        box_plots.ygrid.grid_line_color = "white"
        box_plots.grid.grid_line_width = 2
        box_plots.xaxis.major_label_text_font_size="12pt"
        Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in box_plot_dataset1.columns] # bokeh columns
        box_plot_data_table.columns = Columns
        box_plot_data_table.source = ColumnDataSource(box_plot_dataset1)
        box_plot_data_table.update()

def box_plots_areas_in_region_on_change(attr, old, new):
    print("inside box_plots_areas_in_region_on_change....")
    print(box_plots_area_type_select.value)
    print(box_plots_areas_in_region_select.value)
    print(box_plots_indicator_select.value)
    grouped_quartile_data1 = get_boxplot_indicator_data(box_plots_area_type_select.value,box_plots_areas_in_region_select.value,box_plots_indicator_select.value)
    box_plot_dataset1 = get_boxplot_data_table(grouped_quantile_data)
    print(box_plot_dataset1['Minimum'])
    quantile_min = pd.DataFrame(grouped_quartile_data1.quantile(q=0.00).dropna())
    quantile_1 = pd.DataFrame(grouped_quartile_data1.quantile(q=0.25).dropna())
    quantile_2 = pd.DataFrame(grouped_quartile_data1.quantile(q=0.5).dropna())
    quantile_3 = pd.DataFrame(grouped_quartile_data1.quantile(q=0.75).dropna())
    quantile_max = pd.DataFrame(grouped_quartile_data1.quantile(q=1.00).dropna())     
    iqr = quantile_3-quantile_1
    upper = quantile_3 + 1.5 * iqr
    lower = quantile_1 - 5.5 * iqr    
    upper.Value = [min([x,y]) for (x,y) in zip(list(quantile_max.loc[:,'Value']),upper.Value)]
    lower.Value = [max([x,y]) for (x,y) in zip(list(quantile_min.loc[:,'Value']),lower.Value)]   
    time_period_list = box_plot_dataset['Time Period'].dropna().tolist()
    box_plots = figure(tools=tools, background_fill_color="#efefef", x_range=time_period_list, toolbar_location=None)    
    box_plots.segment(time_period_list, upper.Value, time_period_list, quantile_3.Value, line_color="black")
    box_plots.segment(time_period_list, lower.Value, time_period_list, quantile_1.Value, line_color="black")    
    box_plots.vbar(time_period_list, 0.7, quantile_2.Value, quantile_3.Value, fill_color="#E08E79", line_color="black")
    box_plots.vbar(time_period_list, 0.7, quantile_1.Value, quantile_2.Value, fill_color="#3B8686", line_color="black")   
    box_plots.rect(time_period_list, lower.Value, 0.2, 0.01, line_color="black")
    box_plots.rect(time_period_list, upper.Value, 0.2, 0.01, line_color="black")                            
    box_plots.xgrid.grid_line_color = None
    box_plots.ygrid.grid_line_color = "white"
    box_plots.grid.grid_line_width = 2
    box_plots.xaxis.major_label_text_font_size="12pt"
    Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in box_plot_dataset1.columns] # bokeh columns
    box_plot_data_table.columns = Columns
    box_plot_data_table.source = ColumnDataSource(box_plot_dataset1)
    box_plot_data_table.update()
    
def box_plots_indicator_on_change(attr, old, new):
    print("inside box_plots_indicator_on_change....")
    print(box_plots_area_type_select.value)
    print(box_plots_areas_in_region_select.value)
    print(box_plots_indicator_select.value)
    grouped_quartile_data1 = get_boxplot_indicator_data(box_plots_area_type_select.value,box_plots_areas_in_region_select.value,box_plots_indicator_select.value)
    box_plot_dataset1 = get_boxplot_data_table(grouped_quartile_data1)
    print(box_plot_dataset1['Minimum'])
    quantile_min = pd.DataFrame(grouped_quartile_data1.quantile(q=0.00).dropna())
    quantile_1 = pd.DataFrame(grouped_quartile_data1.quantile(q=0.25).dropna())
    quantile_2 = pd.DataFrame(grouped_quartile_data1.quantile(q=0.5).dropna())
    quantile_3 = pd.DataFrame(grouped_quartile_data1.quantile(q=0.75).dropna())
    quantile_max = pd.DataFrame(grouped_quartile_data1.quantile(q=1.00).dropna())     
    iqr = quantile_3-quantile_1
    upper = quantile_3 + 1.5 * iqr
    lower = quantile_1 - 5.5 * iqr    
    upper.Value = [min([x,y]) for (x,y) in zip(list(quantile_max.loc[:,'Value']),upper.Value)]
    lower.Value = [max([x,y]) for (x,y) in zip(list(quantile_min.loc[:,'Value']),lower.Value)]    
    time_period_list1 = box_plot_dataset['Time Period'].dropna().tolist()   
    box_plots = figure(tools=tools, background_fill_color="#efefef", x_range=time_period_list, toolbar_location=None)    
    box_plots.segment(time_period_list1, upper.Value, time_period_list1, quantile_3.Value, line_color="black")
    box_plots.segment(time_period_list1, lower.Value, time_period_list1, quantile_1.Value, line_color="black")    
    box_plots.vbar(time_period_list1, 0.7, quantile_2.Value, quantile_3.Value, fill_color="#E08E79", line_color="black")
    box_plots.vbar(time_period_list1, 0.7, quantile_1.Value, quantile_2.Value, fill_color="#3B8686", line_color="black")    
    box_plots.rect(time_period_list1, lower.Value, 0.2, 0.01, line_color="black")
    box_plots.rect(time_period_list1, upper.Value, 0.2, 0.01, line_color="black")                              
    box_plots.xgrid.grid_line_color = None
    box_plots.ygrid.grid_line_color = "white"
    box_plots.grid.grid_line_width = 2
    box_plots.xaxis.major_label_text_font_size="12pt"
    Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in box_plot_dataset1.columns] # bokeh columns
    box_plot_data_table.columns = Columns
    box_plot_data_table.source = ColumnDataSource(box_plot_dataset1)
    box_plot_data_table.update()  
         
def outliers(group):
    cat = group.name
    return group[(group.Value > upper.loc[cat]['Value']) | (group.Value < lower.loc[cat]['Value'])]['Value']

####################################################################################################################################################################
####################################################################OVERVIEW TAB RELATED FUNCTIONALITY##############################################################
overview_area_type_select = Select(title="Area Type", value="CountyUA", options=["CountyUA", "DistrictUA", "Region"])
overview_area_type_select.on_change('value', overview_area_type_on_change)
overview_area_grouped_by_select = Select(title="Area grouped by", value="Region", options=["Region"])
region_areas = get_entire_dataset(overview_area_type_select.value)
regions_list = region_areas.loc[region_areas['Parent Name']!='England']['Parent Name'].dropna().unique().tolist()
overview_regions_select = Select(title="Region", value=regions_list[0], options=regions_list)
overview_regions_select.on_change('value', overview_regions_on_change)
areas_list = get_areas_for_region(overview_area_type_select.value,overview_regions_select.value,'2015 - 17')
overview_areas_of_region_select = Select(title="Area", value=areas_list[0], options=areas_list)
temp_dataset = get_region_overview_data(overview_area_type_select.value, overview_regions_select.value,'2015 - 17')
Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=template)) for Ci in temp_dataset.columns] # bokeh columns
overview_data_table = DataTable(columns=Columns, scroll_to_selection=True,selectable=True,
                       source=ColumnDataSource(temp_dataset),align ="center",
                       fit_columns=True,index_position = None,header_row = True,width_policy = "auto",index_header= "#",
                       width=3000, height=300) 
overview_data_table.update()
####################################################################################################################################################################
######################################################COMPARE INDICATORS TAB RELATED FUNCTINALITY###################################################################
compare_indicators_area_type_select = Select(title="Area Type", value="CountyUA", options=["CountyUA", "DistrictUA", "Region"])
compare_indicators_area_type_select.on_change('value', compare_indicators_area_type_on_change)
compare_indicators_area_grouped_by_select = Select(title="Area grouped by", value="Region", options=["Region"])
entire_dataset= get_entire_dataset(compare_indicators_area_type_select.value)
regions_list = region_areas.loc[entire_dataset['Parent Name']!='England']['Parent Name'].dropna().unique().tolist()
compare_indicators_region_select = Select(title="Region", value=regions_list[0], options=regions_list)
compare_indicators_region_select.on_change('value',  compare_indicators_region_on_change)
areas_list = get_areas_for_region(compare_indicators_area_type_select.value,compare_indicators_region_select.value,'2015 - 17')
compare_indicators_area_select = Select(title="Area", value=areas_list[0], options=areas_list)
compare_indicators_area_select.on_change('value',  compare_indicators_area_on_change)
indicators_list = get_overview_indicators_list(compare_indicators_area_type_select.value, compare_indicators_region_select.value,'2015 - 17')
compare_x_indicator_select = Select(title='Indicator', value=indicators_list[0], options=indicators_list)
compare_x_indicator_select.on_change('value', compare_x_indicator_on_change)
all_indicators_list = get_entire_indicators_list(compare_indicators_area_type_select.value,'2015 - 17')
compare_y_indicator_select = Select(title='Indicator on Y axis', value=all_indicators_list[0], options=all_indicators_list)
compare_y_indicator_select.on_change('value', compare_y_indicator_on_change)
compare_all_indicators_button_group = RadioButtonGroup(labels=["All in "+compare_indicators_region_select.value, "All in England"], active=0)
compare_all_indicators_button_group.on_change('active',compare_all_indicators_button_group_on_change)
result_dataset = get_compare_indicators_data(compare_indicators_area_type_select.value, 
                                compare_indicators_region_select.value, 
                                compare_x_indicator_select.value,
                                compare_y_indicator_select.value,
                                None)
regressor = LinearRegression()
regressor.fit(np.array(result_dataset['X'])[:, np.newaxis], np.array(result_dataset['Y'])[:, np.newaxis])
regression_plot = figure(plot_width=1200, plot_height=500, title="Compare Indicators" )
compare_indicators_chekbox = CheckboxGroup(
        labels=["Highlight "+compare_indicators_area_select.value, "Add regression line & R²"], active=[0,1])
compare_indicators_chekbox.active = []
compare_indicators_chekbox.on_change('active',compare_indicator_checkbox_onchange)
regression_circle_source = ColumnDataSource(data=dict(x=result_dataset['X'], y=result_dataset['Y']))
regression_plot.scatter('x', 'y', source = regression_circle_source, size=15, color="navy", alpha=0.5)
regression_plot.xaxis.axis_label = compare_x_indicator_select.value
regression_plot.yaxis.axis_label = compare_y_indicator_select.value
regression_line_source = ColumnDataSource(data=dict(x=np.array(result_dataset['X'])[:, np.newaxis], y=regressor.predict(np.array(result_dataset['X'].tolist())[:, np.newaxis])))
regression_line = regression_plot.line('x', 'y', source = regression_line_source, line_width=3,color="red")
regression_line.visible = False
coefficient_of_dermination = r2_score(result_dataset['Y'], regressor.predict(np.array(result_dataset['X'].tolist())[:, np.newaxis]))
print(coefficient_of_dermination)
paragraph_coeff = Paragraph(text = """R²="""+str(coefficient_of_dermination),
                  width=200, height=100)
paragraph_coeff.visible = False

paragraph_reg_exp = Paragraph(text = """Regression Equation="""+str(regressor.coef_[0][0])+"""x+"""+str(regressor.intercept_[0]),width=200, height=100)
paragraph_reg_exp.visible = False
####################################################################################################################################################################
########################################################COMPARE AREAS TAB RELATED FUNCTIONALITY#####################################################################
compare_areas_area_type_select = Select(title="Area Type", value="CountyUA", options=["CountyUA", "DistrictUA", "Region"])
compare_areas_area_type_select.on_change('value', compare_areas_area_type_on_change)

compare_areas_area_grouped_by_select = Select(title="Area grouped by", value="Region", options=["Region"])
region_areas = get_entire_dataset(compare_areas_area_type_select.value)
compare_areas_list = region_areas.loc[region_areas['Parent Name']!='England']['Parent Name'].dropna().unique().tolist()

compare_areas_areas_in_region_select = Select(title="Region", value=compare_areas_list[0], options=compare_areas_list)
compare_areas_areas_in_region_select.on_change('value',  compare_areas_areas_in_region_on_change)

compare_areas_indicators_list = get_overview_indicators_list(compare_areas_area_type_select.value, compare_areas_areas_in_region_select.value,'2015 - 17')
compare_areas_indicator_select = Select(title='Indicator', value=compare_areas_indicators_list[0], options=compare_areas_indicators_list)
compare_areas_indicator_select.on_change('value', compare_areas_indicator_on_change)

compare_areas_indicators_button_group = RadioButtonGroup(labels=["All in "+compare_areas_areas_in_region_select.value, "All in England"], active=0)

compare_area_result_dataset = get_compare_areas_data(compare_areas_area_type_select.value, 
                                compare_areas_areas_in_region_select.value, 
                                compare_areas_indicator_select.value,
                                '2015 - 17')

Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in compare_area_result_dataset.columns] # bokeh columns
compare_areas_data_table = DataTable(columns=Columns, scroll_to_selection=True,selectable=True,
                       source=ColumnDataSource(compare_area_result_dataset),align ="center",
                       fit_columns=True,index_position = None,header_row = True,row_height=35, width_policy = "auto",index_header= "#",
                      width=1200, height=600) 

compare_areas_data_table.update()
####################################################################################################################################################################
############################################################TRENDS TAB RELATED FUNCTIONALITY##########################################################################
trends_area_type_select = Select(title="Area Type", value="CountyUA", options=["CountyUA", "DistrictUA", "Region"])
trends_area_type_select.on_change('value', trends_area_type_on_change)
trends_area_grouped_by_select = Select(title="Area grouped by", value="Region", options=["Region"])
region_areas = get_entire_dataset(compare_areas_area_type_select.value)
trends_regions_list = region_areas.loc[region_areas['Parent Name']!='England']['Parent Name'].dropna().unique().tolist()
trends_region_select = Select(title="Region", value=trends_regions_list[0], options=trends_regions_list)
trends_region_select.on_change('value',  trends_region_on_change)
areas_list = get_areas_for_region(trends_area_type_select.value,trends_region_select.value,'2015 - 17')
# Select options for Areas in region
trends_area_select = Select(title="Area", value=areas_list[0], options=areas_list)
trends_area_select.on_change('value',  trends_area_on_change)
trends_benchmark_select = Select(title="England", value="England", options=["England", "Region"])
trends_indicators_list = get_overview_indicators_list(trends_area_type_select.value, trends_region_select.value,'2015 - 17')
trends_indicator_select = Select(title='Indicator', value=trends_indicators_list[0], options=trends_indicators_list)
trends_indicator_select.on_change('value', trends_indicator_on_change)
trends_areas_region_button_group = CheckboxButtonGroup(labels=[trends_area_select.value,"All in "+compare_areas_areas_in_region_select.value], active=[0, 1])
trends_result_dataset = get_trends_data(trends_area_type_select.value, 
                                trends_area_select.value, 
                                trends_region_select.value,
                                trends_indicator_select.value)
trends_area_line_source = ColumnDataSource(data=dict(x=trends_result_dataset.index.tolist(), y=trends_result_dataset['Value'].tolist()))
trends_england_line_source = ColumnDataSource(data=dict(x=trends_result_dataset.index.tolist(),y=trends_result_dataset['England'].tolist()))
trends_plot = figure(tools=tools, background_fill_color="#efefef", x_range=trends_result_dataset['Period'].tolist(), toolbar_location=None, height=500,width=700)
trends_plot.line('x', 'y', source = trends_area_line_source, line_width=3,color="red",legend="Selected Area")
trends_plot.line('x', 'y', source = trends_england_line_source, line_width=3,color="black",legend="England")
trends_plot.legend.location = "top_left"
trends_plot.circle('x', 'y',source = trends_area_line_source, size=10, color="red", alpha=0.5)
trends_plot.circle('x', 'y',source = trends_england_line_source, size=10, color="black", alpha=0.5)
trends_plot.xaxis.major_label_orientation = "vertical"
Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in trends_result_dataset.columns] # bokeh columns
trends_data_table = DataTable(columns=Columns, scroll_to_selection=True,selectable=True,
                       source=ColumnDataSource(trends_result_dataset),align ="center",
                       fit_columns=True,index_position = None,header_row = True,row_height=35, width_policy = "auto",index_header= "#",
                      width=800, height=500) 

trends_data_table.update()
####################################################################################################################################################################
######################################################AREA PROFILES TAB RELATED FUNCTIONALITY#####################################################################
area_profiles_area_type_select = Select(title="Area Type", value="CountyUA", options=["CountyUA", "DistrictUA", "Region"])
area_profiles_area_type_select.on_change('value', area_profiles_area_type_on_change)
area_profiles_area_grouped_by_select = Select(title="Area grouped by", value="Region", options=["Region"])
region_areas = get_entire_dataset(area_profiles_area_type_select.value)
area_profiles_list = region_areas.loc[region_areas['Parent Name']!='England']['Parent Name'].dropna().unique().tolist()
area_profiles_areas_in_region_select = Select(title="Region", value=compare_areas_list[0], options=compare_areas_list)
compare_areas_areas_in_region_select.on_change('value',  area_profiles_areas_in_region_on_change)
areas_list = get_areas_for_region(area_profiles_area_type_select.value,area_profiles_areas_in_region_select.value,'2015 - 17')
area_profiles_areas_of_region_select = Select(title="Area", value=areas_list[0], options=areas_list)
area_profiles_areas_of_region_select.on_change('value',  area_profiles_areas_of_region_on_change)
area_profiles_dataset = get_area_profiles_data(area_profiles_area_type_select.value,area_profiles_areas_of_region_select.value,'2015 - 17')
Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in area_profiles_dataset.columns] # bokeh columns
area_profiles_data_table = DataTable(columns=Columns, scroll_to_selection=True,selectable=True,
                       source=ColumnDataSource(area_profiles_dataset),align ="center",
                       fit_columns=True,index_position = None,header_row = True,row_height=35, width_policy = "auto",index_header= "#",
                      width=1000, height=300) 
area_profiles_data_table.update()
####################################################################################################################################################################
##########################################################INEQUALITIES TAB RELATED FUNCTIONALITY#####################################################################
# Select options for list of all indicators
inequalities_area_type_select = Select(title="Area Type", value="CountyUA", options=["CountyUA", "DistrictUA", "Region"])
inequalities_area_type_select.on_change('value', inequalities_area_type_on_change)
inequalities_area_grouped_by_select = Select(title="Area grouped by", value="Region", options=["Region"])
region_areas = get_entire_dataset(inequalities_area_type_select.value)
inequalities_regions_list = region_areas.loc[region_areas['Parent Name']!='England']['Parent Name'].dropna().unique().tolist()
inequalities_regions_select = Select(title="Region", value=inequalities_regions_list[0], options=inequalities_regions_list)
inequalities_regions_select.on_change('value',  inequalities_regions_on_change)
inequalities_indicators_list = get_overview_indicators_list(inequalities_area_type_select.value, inequalities_regions_select.value,'2015 - 17')
inequalities_indicator_select = Select(title='Indicator', value=inequalities_indicators_list[0], options=inequalities_indicators_list)
inequalities_indicator_select.on_change('value',  inequalities_indicator_on_change)
areas_list = get_areas_for_region(area_profiles_area_type_select.value,area_profiles_areas_in_region_select.value,'2015 - 17')
inequalities_areas_select = Select(title="Area", value=areas_list[0], options=areas_list)
inequalities_areas_select.on_change('value',  inequalities_areas_on_change)
inequalities_areas_button_group = RadioButtonGroup(labels=["England", inequalities_areas_select.value], active=0)
inequalities_areas_button_group.on_change('labels',inequalities_areas_button_group_on_change)
inequalities_dataset = get_inequalities_england_data(inequalities_area_type_select.value, 
                            inequalities_indicator_select.value,
                            '2015 - 17')
Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in inequalities_dataset.columns] # bokeh columns
inequalities_data_table = DataTable(columns=Columns, scroll_to_selection=True,selectable=True,
                       source=ColumnDataSource(inequalities_dataset),align ="center",
                       fit_columns=True,index_position = None,header_row = True,width_policy = "auto",index_header= "#",
                       width=700, height=500) 
inequalities_data_table.update()
categories = inequalities_dataset['Category'].tolist()
values = [float(i) for i in inequalities_dataset['Value'].tolist()]
source = ColumnDataSource(data=dict(categories=categories, values=values, color=Spectral6))
inequalities_plot = figure(x_range=categories, y_range=(int(min(values))-5,int(max(values))+5),plot_height=550, title=inequalities_indicator_select.value,
           toolbar_location=None, tools="",plot_width=700)
inequalities_plot.vbar(x='categories', top='values', width=0.3, color='color', legend="values", source=source)
inequalities_plot.xgrid.grid_line_color = None
inequalities_plot.legend.orientation = "horizontal"
inequalities_plot.legend.location = "top_center"
inequalities_plot.xaxis.major_label_orientation = "vertical"
####################################################################################################################################################################
###################################################################ENGLAND TAB RELATED FUNCTIONALITY####################################################################
england_area_type_select = Select(title="Area Type", value="CountyUA", options=["CountyUA", "DistrictUA", "Region"])
temp_dataset = get_england_overview_data(england_area_type_select.value,'England','2015 - 17').iloc[:,[0,1,2]]
Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in temp_dataset.columns] # bokeh columns
england_data_table = DataTable(columns=Columns, scroll_to_selection=True,selectable=True,
                       source=ColumnDataSource(temp_dataset),
                       fit_columns=True,index_position = None,header_row = True,
                      width=700, height=300) 
england_area_type_select.on_change('value', england_area_type_on_change)
####################################################################################################################################################################
#####################################################POPULATION TAB RELATED FUNCTIONALITY###########################################################################
population_area_type_select = Select(title="Area Type", value="CountyUA", options=["CountyUA", "DistrictUA", "Region"])
population_area_type_select.on_change('value', population_area_type_on_change)
population_areas_grouped_by_select = Select(title="Area grouped by", value="Region", options=["Region"])
region_areas = get_entire_dataset(overview_area_type_select.value)
regions_list = region_areas.loc[region_areas['Parent Name']!='England']['Parent Name'].dropna().unique().tolist()
population_regions_select = Select(title="Region", value=regions_list[0], options=regions_list)
population_regions_select.on_change('value', population_regions_on_change)
areas_list = get_areas_for_region(population_area_type_select.value,population_regions_select.value,'2015 - 17')
population_areas_select = Select(title="Area", value=areas_list[0], options=areas_list)
population_areas_select.on_change('value', population_areas_on_change)
temp_dataset = get_population_age_profile_data(population_area_type_select.value,population_areas_select.value)
Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in temp_dataset.columns] # bokeh columns
population_data_table = DataTable(columns=Columns, scroll_to_selection=True,selectable=True,
                       source=ColumnDataSource(temp_dataset),
                       fit_columns=True,index_position = None,header_row = True,
                      width=700, height=300) 
population_data_table.update()
####################################################################################################################################################################
#####################################################BOX PLOTS TAB RELATED FUNCTIONALITY############################################################################
box_plots_area_type_select = Select(title="Area Type", value="CountyUA", options=["CountyUA", "DistrictUA", "Region"])
box_plots_area_type_select.on_change('value', box_plots_area_type_on_change)
box_plots_area_grouped_by_select = Select(title="Area grouped by", value="Region", options=["Region"])
region_areas = get_entire_dataset(area_profiles_area_type_select.value)
box_plots_regions_list = region_areas.loc[region_areas['Parent Name']!='England']['Parent Name'].dropna().unique().tolist()
box_plots_areas_in_region_select = Select(title="Region", value=box_plots_regions_list[0], options=box_plots_regions_list)
box_plots_areas_in_region_select.on_change('value',  box_plots_areas_in_region_on_change)
box_plots_areas_list = get_areas_for_region(box_plots_area_type_select.value,box_plots_areas_in_region_select.value,'2015 - 17')
box_plots_areas_of_region_select = Select(title="Area", value=box_plots_areas_list[0], options=box_plots_areas_list)
box_plots_indicators_list = get_overview_indicators_list(box_plots_area_type_select.value, box_plots_areas_in_region_select.value,'2015 - 17')
box_plots_indicator_select = Select(title='Indicator', value=box_plots_indicators_list[0], options=box_plots_indicators_list)
box_plots_indicator_select.on_change('value', box_plots_indicator_on_change)
grouped_quantile_data = get_boxplot_indicator_data(box_plots_area_type_select.value,box_plots_areas_in_region_select.value,box_plots_indicator_select.value)
box_plot_dataset = get_boxplot_data_table(grouped_quantile_data)
quantile_05 = pd.DataFrame(grouped_quantile_data.quantile(q=0.05).dropna())
quantile_1 = pd.DataFrame(grouped_quantile_data.quantile(q=0.25).dropna())
quantile_2 = pd.DataFrame(grouped_quantile_data.quantile(q=0.5).dropna())
quantile_3 = pd.DataFrame(grouped_quantile_data.quantile(q=0.75).dropna())
quantile_95 = pd.DataFrame(grouped_quantile_data.quantile(q=0.95).dropna()) 
iqr = quantile_3-quantile_1
upper = quantile_3 + 1.5 * iqr
lower = quantile_1 - 5.5 * iqr
upper.Value = [min([x,y]) for (x,y) in zip(list(quantile_95.loc[:,'Value']),upper.Value)]
lower.Value = [max([x,y]) for (x,y) in zip(list(quantile_05.loc[:,'Value']),lower.Value)]
time_period_list = box_plot_dataset['Time Period'].dropna().tolist()
box_plots = figure(tools=tools, background_fill_color="#efefef", x_range=time_period_list, toolbar_location=None, height=500,width=1500)
box_plots.segment(time_period_list, upper.Value, time_period_list, quantile_3.Value, line_color="black")
box_plots.segment(time_period_list, lower.Value, time_period_list, quantile_1.Value, line_color="black")
box_plots.vbar(time_period_list, 0.7, quantile_2.Value, quantile_3.Value, fill_color="#E08E79", line_color="black")
box_plots.vbar(time_period_list, 0.7, quantile_1.Value, quantile_2.Value, fill_color="#3B8686", line_color="black")
box_plots.rect(time_period_list, lower.Value, 0.2, 0.01, line_color="black")
box_plots.rect(time_period_list, upper.Value, 0.2, 0.01, line_color="black")             
box_plots.xgrid.grid_line_color = None
box_plots.ygrid.grid_line_color = "white"
box_plots.grid.grid_line_width = 2
box_plots.xaxis.major_label_text_font_size="12pt"
Columns = [TableColumn(field=Ci, title=Ci, width=50, formatter=HTMLTemplateFormatter(template=table_template)) for Ci in box_plot_dataset.columns] # bokeh columns
box_plot_data_table = DataTable(columns=Columns, scroll_to_selection=True,selectable=True,
                       source=ColumnDataSource(box_plot_dataset),align ="center",
                       fit_columns=True,index_position = None,header_row = True,row_height=35, width_policy = "auto",index_header= "#",
                      width=2000, height=400) 
box_plot_data_table.update()
####################################################################################################################################################################
###########################################################CREATING PANELS AND TABS#################################################################################
overview = Panel(child=layout([overview_area_type_select, overview_area_grouped_by_select, overview_areas_of_region_select, overview_regions_select],[overview_data_table],width=400), title="Overview")
compare_indicators = Panel(child=layout([compare_indicators_area_type_select,compare_indicators_area_grouped_by_select,compare_indicators_region_select,compare_indicators_area_select],[compare_x_indicator_select,compare_y_indicator_select],
                                        [compare_all_indicators_button_group],[regression_plot,[compare_indicators_chekbox,paragraph_coeff,paragraph_reg_exp]], 
                                        width=400),title="Compare Indicators")
maps = Panel(child=layout([]),title="Map")
trends = Panel(child=layout([trends_area_type_select,trends_area_grouped_by_select,trends_area_select,trends_region_select,trends_benchmark_select],
                            [trends_indicator_select],[trends_plot,trends_data_table],
                            width=400),title="Trends")
compare_areas = Panel(child=layout([compare_areas_area_type_select,compare_areas_area_grouped_by_select,compare_areas_areas_in_region_select,compare_areas_indicator_select], 
                                   [compare_areas_indicators_button_group],
                                   [compare_areas_data_table],
                                   width=400),title="Compare Areas")
area_profiles = Panel(child=layout([area_profiles_area_type_select,area_profiles_area_grouped_by_select],
                                   [area_profiles_areas_of_region_select,area_profiles_areas_in_region_select],
                                   [area_profiles_data_table]),title="Area profiles")
inequalities = Panel(child=layout([inequalities_area_type_select,inequalities_area_grouped_by_select,inequalities_regions_select,inequalities_areas_select],[inequalities_indicator_select],[inequalities_areas_button_group],[inequalities_plot,inequalities_data_table], 
                                   width=400),title="Inequalities")
england = Panel(child=layout([england_area_type_select],[england_data_table]),title="England")
population = Panel(child=layout([population_area_type_select,population_areas_grouped_by_select,population_regions_select],[population_areas_select],[population_data_table]),title="Population")
box_plots_panel = Panel(child=layout([box_plots_area_type_select,box_plots_area_grouped_by_select,
                                      box_plots_areas_in_region_select,box_plots_areas_of_region_select,
                                      box_plots_indicator_select],[box_plots],[box_plot_data_table]),title="Box plots")
definitions = Panel(child=layout([]),title="Definitions")
downloads = Panel(child=layout([]),title="Downloads")
life_exp = Tabs(tabs=[overview,compare_indicators,
                      maps,trends,compare_areas,area_profiles,
                      inequalities,england,population,box_plots_panel,
                      definitions,downloads])
life_exp_panel = Panel(child=life_exp, title="Life expectancy and causes of death")
local_authority_tabs = Tabs(tabs=[ life_exp_panel])
####################################################################################################################################################################
##############################################USER AUTHENTICATION###################################################################################################
def verify_credentials():
    if(user.value=="demo" and pwd.value=="demo"):
        doc1.remove_root(page)
        doc1.add_root(local_authority_tabs)
    else:
        secret.text = "Wrong credentials"
USER = "demo"
PASSWD = "demo"
text = PreText(text=" ")
spaces = PreText(text="                                   ")
spaces1 = PreText(text="             ")
spaces2 = PreText(text="       ")
user = TextInput(placeholder="username", title="User Name:")
pwd = PasswordInput(placeholder="password", title="Password:")
btn = Button(label="GO!",width=150, button_type="success")
btn.on_click(verify_credentials)
secret = PreText() # Secret information displayed if correct password entered
####################################################################################################################################################################
######################USER AUTHENTICATION PAGE LAYOUT###############################################################################################################
div = Div(text="""<style>
img {
  border-radius: 40%;
}
.container {
  position: relative;
  font-family: Arial;
}
.text-block {
  position: absolute;
  bottom: 15px;
  right: 15px;
  background-color: #60CE2B;
  color: white;
  padding-left: 15px;
  padding-right: 15px;
}
</style>
<table align="centre">
                      <tr>
                      <td aligh="centre"><div class="container"><img src="https://i.ibb.co/C7cKnJ0/mo.jpg" alt="HTML5 Icon" width="250" height="250"/>
                        <div class="text-block">
                        <h4>Dr Mo Saraee</h4>
                      </div></div></td>
                      <td aligh="centre"><div class="container"><img src="https://i.ibb.co/51cL6n6/2.jpg" alt="HTML5 Icon" width="250" height="250"/>
                          <div class="text-block">
                          <h4>Charith Silva</h4>
                          </div></div>
                      </td>
                      <td aligh="centre"><div class="container"><img src="https://i.ibb.co/FWhKNsC/3.jpg" alt="HTML5 Icon" width="250" height="250">
                      <div class="text-block">
                          <h4>Sujana Katta</h4>
                          </div></div>
                     </td>
                      <td aligh="centre"><div class="container"><img src="https://i.ibb.co/pd9bFK2/5.jpg" alt="HTML5 Icon" width="250" height="250">
                     <div class="text-block">
                          <h4>Ravikanth</h4>
                          </div></div>
                     </td>
                      <td aligh="centre"><div class="container"><img src="https://i.ibb.co/F58w81q/4.jpg" alt="HTML5 Icon" width="250" height="250">
                     <div class="text-block">
                          <h4>Konstantinos Zeimpekis</h4>
                          </div></div></td>
                      </tr>
</table>
""", width=200, height=100)

logo = Div(text="""
<table align="centre">
                      <tr>
                      <td aligh="centre"><img src="https://i.ibb.co/yq5NhjQ/Logo.png" alt="Logo" border="0" width="1500" height="270"/></td>
                      </tr>
</table>
""",width=200, height=100)

page = column(row(logo),row(text),row(text),row(text),row(text),row(text),row(text),row(column(spaces),column(spaces),column(user)), row(column(spaces),column(spaces),column(pwd)),row(column(spaces),column(spaces),column(spaces2),column(btn)),row(column(spaces1),column(div)),row(secret))
page.align = "center"
doc1 = curdoc()
doc1.add_root(page)
#################################################################################################################################################################
##Running Bokeh Application in Local Machine
#bokeh serve --show public-health.py

##Running Bokeh Application in Kyso cloud
#bokeh serve --show public-health.py --port 8000 --allow-websocket-origin=*

#https://geohealthai-d2eyucnyd1.cloud.kyso.io/lab?

#https://geohealthai-d2eyucnyd1-8000.cloud.kyso.io/public-health