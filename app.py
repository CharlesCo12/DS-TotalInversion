# Import the necessary libraries to use streamlit
import streamlit as st
import numpy as np
import matplotlib.pylab as plt
import pandas as pd
import pyreadr

import warnings
warnings.filterwarnings("ignore")

# Setting page configuration and initial information
st.set_page_config(page_title="Inversion on Research and Development Plot")

st.title("Total Inversion on Research and Development during the last decade (2010 - 2020)")
st.subheader("By Carlos Córdoba-Caycedo")
st.write(""" 
Below you will find a bar plot of the Total inversion on Research and Development in the different provinces of Canada during the last decade and by selecting a specific science type (All Sciences, Natural Sciences or Social Sciences) on the dropdown below, the plot will display information only about the specific selection.
""")

#Importing the dataset and transforming the data to generate the tidy_data for the analysis
data = pyreadr.read_r("Database.RData")['database']
index_missingvalues = np.where(np.isnan(pd.to_numeric(data["VALUE"])))[0]
data["VALUE"][index_missingvalues]=0
data_reduced = data[["REF_DATE","GEO","Funder","Performer","Science.type","Prices","VALUE"]]

tidy_data = data_reduced[(data_reduced["Prices"]=="Current prices")
                         &(data_reduced["REF_DATE"]>=2010)
                         &(data_reduced["Funder"]=="Funder: total, all sectors")
                         &(data_reduced["Performer"]=="Performer: total, all sectors")
                         &(data_reduced["GEO"]!="Canada")] [["REF_DATE","GEO","Science.type","VALUE"]]
#Create a new column of values by grouping the data on the main 5 locations that impact the economic inversion
new_cities = list(tidy_data["GEO"])
for i in range(len(new_cities)):
    if((new_cities[i]!="Alberta")&(new_cities[i]!="British Columbia")&(new_cities[i] !="Ontario")&(new_cities[i] !="Quebec")):
        new_cities[i]="Other provinces"
        
tidy_data["Provinces"]=new_cities

#Create lists of unique values. The list for s_types will be used for the dropdown.
years = list(set(tidy_data["REF_DATE"]))
unique_provinces = list(set(tidy_data["Provinces"]))
s_types = sorted(list(set(tidy_data["Science.type"])))
added_values = []
indexes=[]
for i in years:
    for j in unique_provinces:
        for k in s_types:
            added_values.append([i,j,k,np.sum(tidy_data[(tidy_data["REF_DATE"]==i)
                                                        &(tidy_data["Provinces"]==j)&(tidy_data["Science.type"]==k)]["VALUE"])])

# This dataframe contains the information reduced so we can use it for plotting the information.
final_tidy_data = pd.DataFrame(added_values, columns = ["Year","Provinces","Science type","Total_Value"])
final_tidy_data=final_tidy_data.sort_values(by=["Year"])

# Creating the Science type dropdown
option_selected = st.selectbox(
    'Select a Science Type for the Analysis:',
     s_types)


# We will only use information for the Science type selected in the app.
Science_Type = option_selected
plot_data = final_tidy_data[final_tidy_data["Science type"]==Science_Type]
mean = list(plot_data.groupby("Provinces").Total_Value.mean())
        
# We sort the provinces in ascending ording with respect to the mean of the inversion througout the decade
index_sorted = np.argsort(np.array(mean))
sorted_provinces = np.array(sorted(unique_provinces))[index_sorted]
        
# Plot the bars representing the inversion by Province for the specific Science type
fig, ax = plt.subplots(figsize=(8,6))
N=len(years)
x_labelpos = np.arange(N)  
width = 0.18
for k in range(len(sorted_provinces)):
    province = sorted_provinces[k]
    y_data = plot_data[plot_data["Provinces"]==province]["Total_Value"]
    x_off = (k - N/2)*width + width/2
    ax.bar(x_labelpos+x_off,y_data,label=province,width=width)
    
ax.grid(linewidth = 0.5)
ax.legend(loc=0.0)
ax.set_ylabel("Total Inversion (X1000000 CAD)")
ax.set_xlabel("Year")
ax.set_xticks(labels=sorted(years),ticks=x_labelpos-(2*len(unique_provinces)/3)*width)
ax.set_title("Total Inversion per Year by Province for "+Science_Type)

st.pyplot(fig)