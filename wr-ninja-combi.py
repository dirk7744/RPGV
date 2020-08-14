# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 14:50:44 2020

@author: Dirk
"""


from netCDF4 import Dataset, num2date
import numpy as np
from pathlib import Path
#import cartopy.crs as ccrs
#import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import xarray as xr


######################Load Datasets#################
#Load weather regime dataset
data_folder = Path("../data/")
# filename = data_folder / 'wr-gph-djf-daily-mean.nc'
f_in = data_folder / 'wr_time2.nc'
#f_out = data_folder / 'results/mean_wr_country_c4.csv'

wr_time = xr.open_dataset(f_in)
#dates = num2date(time, ncin.variables['time'].units)

#Load renewable ninja dataset
filename = data_folder / 'ninja/ninja_europe_pv_v1.1/ninja_pv_europe_v1.1_merra2.csv'
ninja = pd.read_csv(filename)


######################Calculate ninja CF mean for every weather regime#######

#Format time of wr data
# day = [int(d.strftime('%Y%m%d')) for d in dates]
#day = list(dict.fromkeys(day))
#d = [datetime.strptime(str(d), '%Y%m%d') for d in day]
# wr_time.time.dt.strftime("%Y%m%d")

#Format time of ninja data
ninja_day = [i.replace('-','') for i in ninja.time[:]]
for i in range(0, len(ninja_day)): 
    ninja_day[i] = int(ninja_day[i][:8])
    
ninja_day = list(dict.fromkeys(ninja_day))

#get ninja time index for every weather regime
# wr_day = wr_time.where(wr_time==0, drop=True).time.dt.strftime("%Y%m%d")
# temp = []


# if int(wr_day[300]) == ninja_day[3306]:
# #     print('ja')


# for a in wr_day:
#    temp.extend([i for i, e in enumerate(ninja_day) if e == int(a)])
   
ninja_wr_index =[]

for b in range(0,int(wr_time.wr.max())+1):
#for b in range(0,2):
    wr_day = wr_time.where(wr_time==b, drop=True).time.dt.strftime("%Y%m%d")
    temp = []
    for a in wr_day:
        temp.extend([i for i, e in enumerate(ninja_day) if e == int(a)])
    ninja_wr_index.append(temp)

#all ninja days found in all weather regimes
flattened_nina_wr_index = [y for x in ninja_wr_index for y in x]



#Calculate mean per weather regime and country
mean_wr_country = pd.DataFrame()

for a in range(0, int(wr_time.wr.max())+1):
    temp2 = pd.DataFrame()
    for i in ninja.drop(['time'], axis=1):
        temp = pd.DataFrame([ninja[i][ninja_wr_index[a]].mean(axis=0)], index=[i], columns=['WR'+str(a)])
        temp2 = temp2.append(temp)
    mean_wr_country = pd.concat([mean_wr_country, temp2], axis=1)
 
    
#calculate mean per country
mean_country = pd.DataFrame()
for i in ninja.drop(['time'], axis=1):
    mean_country_temp = pd.DataFrame([ninja[i][flattened_nina_wr_index].mean(axis=0)], index=[i], columns=['all WR'])
    mean_country = mean_country.append((mean_country_temp))                                                                                        


#calculate anomaly per weather region relative to mean per country
relative_mean_wr_country = pd.DataFrame()

#np.array(mean_country['all WR']) - np.array(mean_wr_country['WR0'])

for i in mean_wr_country:
    relative_mean_temp = pd.DataFrame(np.array(mean_country['all WR']) - np.array(mean_wr_country[i]), index=mean_wr_country.index, columns=[str(i)])
    relative_mean_wr_country = pd.concat([relative_mean_wr_country, relative_mean_temp], axis=1)


#save results as csv
#♦mean_wr_country.to_csv(f_out)


#########MAP data#############
import geopandas as gpd
shapefile = data_folder / 'map/NUTS_RG_01M_2021_4326.shp/NUTS_RG_01M_2021_4326.shp'
#Read shapefile using Geopandas
eu = gpd.read_file(shapefile)[['NAME_LATN', 'CNTR_CODE', 'geometry']]
#Rename columns.
eu.columns = ['country', 'country_code', 'geometry']
eu.head()


for_plotting = eu.merge(relative_mean_wr_country*100, left_on = 'country_code', right_index=True)
for_plotting.info()

f, ax = plt.subplots(
    ncols=2,
    nrows=2,
    figsize=(18, 12),
)
k=0        
for i in range(0,2):
    for a in range(0,2):
        for_plotting.dropna().plot(ax = ax[i,a], column='WR'+str(k), cmap =    
                                        'YlGnBu',   
                                         scheme='quantiles', k=8, legend =  
                                          True,);
        #add title to the map
        ax[i,a].set_title('Capacity factor per country for weather regime'+str(k)+' in winter', fontdict= 
                    {'fontsize':15})
        #remove axes
        ax[i,a].set_axis_off()
        #move legend to an empty space
        ax[i,a].get_legend().set_bbox_to_anchor((.12,1))
        ax[i,a].set_xlim(left=-20, right=40)
        ax[i,a].set_ylim(bottom=30, top=80)

        k = k+1
        




