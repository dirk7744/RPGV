# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 08:14:39 2020

@author: Dirk
"""

import numpy as np
from pathlib import Path
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import xarray as xr
import calendar
import pandas as pd
import matplotlib as mpl
import geopandas as gpd
from mapclassify import Quantiles, UserDefined


######################Load Datasets#################

data_folder = Path("../data/")

filename_std_ano = data_folder / 'z_all_std_ano.nc'
filename = data_folder / 'gph-daily-mean.nc'
z_all_std_ano = xr.open_dataset(filename_std_ano)['z']
z_all = xr.open_dataset(filename)['z']

file_wr = data_folder / 'wr_time-c7_std.nc'
wr = xr.open_dataset(file_wr)

file_cf = data_folder / 'results/relative_mean_wr_country_c4.csv'
relative_mean_wr_country = pd.read_csv(file_cf, index_col=0)



######################Plot results#################

#Rows and colums
r = 3
c = wr.wr.max().values+1

#Create subplots and colorbar for wr
cmap = mpl.cm.get_cmap("RdBu_r")
plt.close("all")
f, ax = plt.subplots(
    ncols=c,
    nrows=r,
    subplot_kw={"projection": ccrs.Orthographic(central_longitude=-20, central_latitude=60)},
    figsize=(30, 10),
)
cbar_ax = f.add_axes([0.3, .61, 0.4, 0.02])

###DA warst du#### --> mach mal cax für EU CF plot
cbar_ax2 = f.add_axes([0.3, .61, 0.4, 0.02])

#map infos for relative capacity factors per country
#Read shapefile using Geopandas
shapefile = data_folder / 'map/NUTS_RG_01M_2021_4326.shp/NUTS_RG_01M_2021_4326.shp'
eu = gpd.read_file(shapefile)[['NAME_LATN', 'CNTR_CODE', 'geometry']]
#Rename columns.
eu.columns = ['country', 'country_code', 'geometry']
cf_plotting = eu.merge(relative_mean_wr_country*100, left_on = 'country_code', right_index=True)



vmax_std_ano = 1.5
vmin_std_ano = -1.5

# vmax_cf = 20
# vmin_cf = -20

for i in range(0,wr.wr.max().values+1):
    mean_wr_std_ano = z_all_std_ano[np.where(wr.wr==i)[0][:]].mean(axis=0)
    frequency = len(np.where(wr.wr == i)[0]) / len(wr.wr)
 
    if i != 0:

        #standard anomalie height plot

        title= 'std ano WR' + str(i) + ' ' +  str(np.round(frequency * 100, decimals=1)) + "%"
        ax[0, i].coastlines()
        ax[0, i].set_global()
        mean_wr_std_ano.plot.contourf(ax=ax[0, i], cmap=cmap, vmin=vmin_std_ano, vmax=vmax_std_ano,
                                  transform=ccrs.PlateCarree(), add_colorbar=False)
        ax[0, i].set_title(title, fontsize=16)
        
        
        #Plot CF
        ax[1, i] = plt.subplot(2, c, c + 1 + i)  # override the GeoAxes object
        cf_plotting.dropna().plot(ax = ax[1,i], column='WR'+str(i), cmap=cmap,
                                  #vmax=vmax_cf, vmin=vmin_cf,
                                  scheme='quantiles', legend=True,);
        #add title to the map
        ax[1,i].set_title('delta-CF WR'+str(i), fontdict= 
                    {'fontsize':15})
        #remove axes
        ax[1,i].set_axis_off()
        #only plot relevant part of map
        ax[1,i].set_xlim(left=-20, right=40)
        ax[1,i].set_ylim(bottom=30, top=80)
        
        
    else:
  
        #standard anomalie height plot
        # vmax_std_ano = mean_wr_std_ano.max()
        # vmin_std_ano = mean_wr_std_ano.min()
        title= 'std ano WR' + str(i) + ' ' +  str(np.round(frequency * 100, decimals=1)) + "%"
        ax[0, i].coastlines()
        ax[0, i].set_global()
        mean_wr_std_ano.plot.contourf(ax=ax[0, i], vmin=vmin_std_ano, vmax=vmax_std_ano, cmap=cmap,
                                  transform=ccrs.PlateCarree(), add_colorbar=True, cbar_kwargs={"orientation": "horizontal"}, cbar_ax=cbar_ax)
        ax[0, i].set_title(title, fontsize=16) 
        
        
        
        #Plot CF
        ax[1, i] = plt.subplot(2, c, c + 1 + i)  # override the GeoAxes object
        cf_plotting.dropna().plot(ax = ax[1,i], column='WR'+str(i), cmap=cmap,
                                  #vmax=vmax_cf, vmin=vmin_cf,
                                  scheme='quantiles', legend=True, cax=cax);
        #add title to the map
        ax[1,i].set_title('delta-CF WR'+str(i), fontdict= 
                    {'fontsize':15})
        #remove axes
        ax[1,i].set_axis_off()
        #move legend to an empty space
        ax[1,i].get_legend().set_bbox_to_anchor((.12,1))
        ax[1,i].set_xlim(left=-20, right=40)
        ax[1,i].set_ylim(bottom=30, top=80)
        patch_col = ax[1,i].collections[0]
        cb = f.colorbar(patch_col, ax=ax[1,i], shrink=0.5)
               
        
        



    
    #Plot monthly frequency of weather regime    
    # monthly_frequency = wr.where(wr==i).dropna(dim='time').groupby('time.month').count()
    # ax[2, i] = plt.subplot(2, c, c + 1 + i)  # override the GeoAxes object
    # monthly_frequency = pd.Series(data=monthly_frequency.wr, index=calendar.month_abbr[1:13])
    
    # monthly_frequency.plot.bar(ax=ax[2,i])

#¶plt.subplots_adjust(left=0.05, right=0.92, bottom=0.25)

plt.suptitle("Mean weather regime fields (standardized anomalies) and relative mean capacity factors", fontsize=20)
plt.savefig("../data/fig/cf_and_wr_plot.png")








# f, ax = plt.subplots(
#     ncols=2,
#     sharex=True,
#     sharey=True,
#     nrows=1,)

# bins = Quantiles(cf_plotting['WR1'], 20).bins
# cf_plotting.assign(cl=UserDefined(cf_plotting['WR0'].dropna(), list(bins)).yb).plot(
#     column='WR0', ax=ax[0], cmap=cmap)
# ax[0].set_xlim(left=-20, right=40)
# ax[0].set_ylim(bottom=30, top=80)

# cf_plotting.plot('WR1', scheme='quantiles',  ax=ax[1], cmap=cmap, legend=True, cax=ax[1],
#              legend_kwds=dict(loc='upper right', title="Legend\n", frameon=False)
# )

# ax[1].set_xlim(left=-20, right=40)
# ax[1].set_ylim(bottom=30, top=80)