# %%
import nsepy as nse
import datetime
import urllib3 
import random 
import numpy as np 
from fbprophet import Prophet 
import pandas as pd
from nsetools import Nse
nsel = Nse()
stock_list = nsel.get_stock_codes() 
stock_list= {v: k for k, v in stock_list.items()} 
Today = datetime.datetime.now() 
number_of_company = int(input('En|tert the number of company:\t')) 

# %%
 # taking the number of companies to predict
company_list =[]
for _ in range(number_of_company):
 name = input('Enter the Company to Predict\t:\t')
 company_list.append(name)
 numbered = list(company_list)
 stock_data = list(company_list)
for i in range(number_of_company):
 stock_data[i] = nse.get_history(symbol=company_list[i], start=datetime.datetime(2019,11,1), end=datetime.datetime(2021,3,27))

# %%
