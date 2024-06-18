import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sbn
import numpy as np
from bs4 import BeautifulSoup
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
@st.cache_resource
def load_data(csv_path):
    data = pd.read_csv(csv_path)
    return data
data= load_data('data.csv')
df = pd.DataFrame(data)
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)
df['Date'] = df['Order Date'].dt.strftime('%Y-%m-%d')

df.set_index(keys='Date', inplace = True)
df.index = pd.to_datetime(df.index)

df['Year'] = df.index.year

df['Ship Date'] =df['Ship Date']+ pd.DateOffset(years=2)
df['Days to Ship'] = (df['Ship Date'] - df['Order Date']).dt.days

df['Order Date'] = df['Order Date'].dt.strftime('%Y-%m-%d')
df['Ship Date'] = df['Ship Date'].dt.strftime('%Y-%m-%d')
df.fillna(np.nan, inplace=True)




st.sidebar.subheader('Made by: \n Laszlo Majoros & Adam Nagy', divider= 'red')
st.sidebar.header("FILTERING OPTIONS:", divider="red")

all_years = sorted(df['Year'].unique())
sel_year = st.sidebar.multiselect('Select Year(s):', options=all_years, default=all_years)

st.sidebar.subheader('', divider="red")

all_ship = sorted(df['Ship Mode'].unique())
sel_ship = st.sidebar.multiselect('Select Shipping method(s):', options=all_ship, default=all_ship)

st.sidebar.subheader('', divider="red")

all_cat = sorted(df['Category'].unique())
sel_cat = []
st.sidebar.write('Select Category(s):')
for category in all_cat:
    if st.sidebar.checkbox(category, value=True):
        sel_cat.append(category)
        
st.sidebar.subheader('', divider="red")

all_sub = sorted(df['Sub-Category'].unique())
sel_sub = []
st.sidebar.write('Select Sub-Category(s):')
for category in all_sub:
    if st.sidebar.checkbox(category, value=True):
        sel_sub.append(category)
        
st.sidebar.subheader('', divider="red")

filtered_df = df[(df['Year'].isin(sel_year)) & (df['Category'].isin(sel_cat)) & (df['Ship Mode'].isin(sel_ship)) & (df['Sub-Category'].isin(sel_sub))]
tot_sales = round((filtered_df['Sales'].sum())/1000000,1) 
tot_profit = round(filtered_df['Profit'].sum()/1000,1)
tot_orders = len(filtered_df['Order ID'].unique())

st.markdown("<h1 style='text-align: center; color: #FF3333; font-size: 100px;'>SUPERSTORES</h1>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #FF6666; font-size: 35px;'>Orders overall review</h1>", unsafe_allow_html=True)
st.header('Analysis of the orders of Superstore', divider='red')

col1,col2,col3 = st.columns([2, 0.15, 0.6])

# Different shades of red for the bars
red_shades = [
    "#FF9999",  
    "#FF6666",
    "#FF3333",
    "#FF0000", 
    "#CC0000",
    "#990000",
    '#8B0000',
    "#660000",
    "#330000",
    "#330015"
]

with col1: 
    # Average shipping days
    min_ship_days = filtered_df['Days to Ship'].min()
    max_ship_days = filtered_df['Days to Ship'].max()
    avg_ship_days = filtered_df['Days to Ship'].mean()

    avg_ship_indicator = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = avg_ship_days,
        #title = {'text': "Average days to ship"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        number={'valueformat': '.2f', 'suffix': " days"},
        gauge = {
            'axis': {'range': [min_ship_days, max_ship_days]},
            'bar': {'color': 'darkred'}
        }
    ))

    avg_ship_indicator.update_layout(
        width=700,
        height=300,
        margin=dict(t=20, b=20, l=20, r=20)
        )
    st.subheader('Average shipping date:', divider="red")
    st.plotly_chart(avg_ship_indicator, use_container_width=True)

with col3:
    st.subheader(f'Total Sales:  ${tot_sales}M', divider="red")
    st.subheader(f'Total Profit: ${tot_profit}K', divider='red')
    st.subheader(f'Total Orders:  {tot_orders}',divider='red')

st.header("Plot analysis:", divider='red')
col5,col6 = st.columns(2)


with col5:
    # Top 10 products by sales
    prod_sales = filtered_df.groupby('Product Name').sum('Sales').round(2)
    prod_sales_sorted = prod_sales.sort_values(by='Sales', ascending=False)
    top10_prods_sales = prod_sales_sorted.head(10)
    top10_prods_sales = top10_prods_sales.reset_index()
    max_sales = top10_prods_sales['Sales'].max()
    
    fig, ax = plt.subplots(figsize=(10, 20))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    t10_sales_horbar = sbn.barplot(x="Sales", y="Product Name", data=top10_prods_sales, palette=red_shades, errorbar=None)
    for index, value in enumerate(top10_prods_sales['Sales']): 
        plt.text(value, index, f'  ${round(int(value)/1000, 2)}k', va='center', color='white', ha='left', fontsize=35)

    plt.xlim(0, max_sales)
    plt.ylabel("", fontsize=15)
    plt.xlabel("", fontsize=15)
    plt.xticks(color= 'white', fontsize=25)
    plt.yticks(color='white', fontsize=30)
    sbn.despine(left=True, bottom=True)
    
    plt.gcf().patch.set_alpha(0.0)
    st.subheader('Top 10 products by Sales', divider='red')
    st.pyplot(fig)
    
with col6:
    # Top 10 products by profit
    prod_profit = filtered_df.groupby('Product Name').sum('Profit').round(2)
    prod_profit_sorted = prod_profit.sort_values(by='Profit', ascending=False)
    top10_prods_profit = prod_profit_sorted.head(10)
    top10_prods_profit = top10_prods_profit.reset_index()
    max_profit = top10_prods_profit['Profit'].max()
    
    plt.style.use('dark_background')
    sbn.set_color_codes("muted")
    
    fig, ax = plt.subplots(figsize=(10, 20))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    t10_profit_horbar = sbn.barplot(x="Profit", y="Product Name", data=top10_prods_profit, palette=red_shades, errorbar=None)
    for index, value in enumerate(top10_prods_profit['Profit']):
        plt.text(value, index, f'  ${round(int(value)/1000, 2)}k', va='center', ha='left', color='white', fontsize=35)

    plt.xlim(0, max_profit)
    plt.ylabel('',fontsize=15)
    plt.xlabel('',fontsize=15)
    plt.xticks(color='white', fontsize=25)
    plt.yticks(color='white', fontsize=30)
    sbn.despine(left=True, bottom=True)
    
    plt.gcf().patch.set_alpha(0.0)
    st.subheader('Top 10 products by Profit', divider='red')
    st.pyplot(fig)

# Sales trends
yearly_sales_by_category = filtered_df.groupby(['Year', 'Category'])['Sales'].sum().reset_index().round(2)
pivot_table = yearly_sales_by_category.pivot(index='Year', columns='Category', values='Sales')
pivot_table = pivot_table / 1000
colors = ["#330015","#CC0000", "#FF9999"] 
ax = pivot_table.plot(kind='bar', stacked=True, color=colors, figsize=(10, 6))

plt.xlabel('Year')
plt.ylabel('Sales')
legend = plt.legend(title='Category')
legend.get_frame().set_facecolor('none')
legend.get_frame().set_edgecolor('none')
plt.xticks(rotation=0)
for container in ax.containers:
    ax.bar_label(container, fmt='$%.2fk', label_type='center')

st.subheader("Yearly Sales by Category", divider='red')
fig = plt.gcf()
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)
st.pyplot(fig)
         
st.header('Filtered DataFrame:', divider="red")
st.dataframe(filtered_df, hide_index=True)
