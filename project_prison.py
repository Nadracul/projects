import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import seaborn as sbn
import matplotlib.pyplot as plt

# URL of the Wikipedia page
url = 'https://en.wikipedia.org/wiki/List_of_helicopter_prison_escapes'

# Send a request to fetch the HTML content
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the table containing the list of helicopter prison escapes
table = soup.find('table', {'class': 'wikitable'})

# Extract the headers
headers = []
for th in table.find_all('th'):
    headers.append(th.text.strip())

# Extract the rows
rows = []
for tr in table.find_all('tr')[1:]:
    cells = tr.find_all(['td', 'th'])
    row = [cell.text.strip() for cell in cells]
    rows.append(row)

# Create a DataFrame
df = pd.DataFrame(rows, columns=headers)

# Function to fetch the year from a date string
def fetch_year(date_str):
    # Use regex to find the first four-digit number which represents the year
    match = re.search(r'\b\d{4}\b', date_str)
    if match:
        return match.group(0)
    return None  # Return the original string if no year is found

# Iterate over the rows to extract and replace the date with the year
years = []
for row in rows:
    if len(row) > 0:
        year = fetch_year(row[0])
        years.append(year)
        
df['Year'] = years

# Configure Streamlit to use wide layout mode
st.set_page_config(layout="wide")

# Display filtered data
st.header('Prison escape attempts')
st.sidebar.subheader("Options")

# Sidebar for selecting country or year
option = st.sidebar.radio('Filter by', ('Country', 'Year'))

min_year = int(df['Year'].min())
max_year = int(df['Year'].max())
all_years = list(range(min_year, max_year + 1))

# Count the number of prison break attempts for each year
attempts_per_year = []
for year in all_years:
    count = df['Year'].tolist().count(str(year))
    attempts_per_year.append(count)

# Create a DataFrame with the complete range of years and the counts
attempts_df = pd.DataFrame({
    'Year': all_years,
    'Attempts': attempts_per_year
})

col1, col2 = st.columns(2)

with col1:
    plt.figure(figsize=(15,8))
    plt.subplot(1, 2, 1)
    bars = plt.barh(attempts_df['Year'], attempts_df['Attempts'], color='red')

    # Add title and labels
    plt.title('Number of Prison Break Attempts Per Year')
    plt.ylabel('Year')
    plt.xlabel('Number of Attempts')

    # Add count values as annotations
    for bar in bars:
        plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, str(int(bar.get_width())), va='center', ha='left')
    plt.yticks(attempts_df['Year'])
    plt.tight_layout()
    st.pyplot(plt.gcf())
    
with col2:
       
    # Count occurrences of each country
    country_counts = df['Country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Count']
    # Plot the data as a bar plot
    plt.figure(figsize=(15, 8))
    plt.subplot(1, 2, 1)
    bars = plt.barh(country_counts['Country'], country_counts['Count'], color='green')

    # Add title and labels
    plt.title('Number of Prison Break Attempts in countries')
    plt.ylabel('Country')
    plt.xlabel('Number of Attempts')

    # Add count values as annotations
    for bar in bars:
        plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, str(int(bar.get_width())), va='center', ha='left')
    plt.tight_layout()
    st.pyplot(plt.gcf())     



col3, col4 = st.columns(2)
# If filtering by country
if option == 'Country':
    selected_option = st.sidebar.selectbox('Select Country', df['Country'].unique())
    filtered_df = df[df['Country'] == selected_option]
    st.dataframe(filtered_df)
    # Count occurrences of each year for the selected country
    attempts_per_year = filtered_df['Year'].value_counts().reset_index()
    attempts_per_year.columns = ['Year', 'Attempts']

    with col3:
        # Plot the data
        plt.figure(figsize=(10, 6))
        sbn.barplot(x='Year', y='Attempts', data=attempts_per_year, palette='viridis')
        plt.title(f'Number of Prison Break Attempts Per Year in {selected_option}')
        plt.xlabel('Year')
        plt.ylabel('Number of Attempts')
        st.pyplot(plt.gcf())

# If filtering by year
elif option == 'Year':
    selected_option = st.sidebar.selectbox('Select Year', df['Year'].unique())
    filtered_df = df[df['Year'] == selected_option]
    st.dataframe(filtered_df)
        # Count occurrences of each country for the selected year
    country_counts = filtered_df['Country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Count']

    with col3:
        # Plot the data
        plt.figure(figsize=(10, 6))
        sbn.barplot(x='Country', y='Count', data=country_counts, palette='muted')
        plt.title(f'Number of Prison Break Attempts by Country in {selected_option}')
        plt.xlabel('Country')
        plt.ylabel('Number of Attempts')
        plt.xticks(rotation=45)
        st.pyplot(plt.gcf())

with col4:
    # Add pie chart for success rate
    if len(filtered_df) > 0:
        succeeded_counts = filtered_df['Succeeded'].value_counts()
        labels = succeeded_counts.index
        sizes = succeeded_counts.values

        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Success Rate of Prison Break Attempts')
        st.pyplot(plt.gcf())
    else:
        st.write("No data available for selected filter.")