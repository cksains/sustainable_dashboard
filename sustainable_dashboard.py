#!/usr/bin/env python
# coding: utf-8
import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
df = pd.read_csv('SEI_Summary_2.csv', index_col=False)

# Ensure 'Rating Year' is numeric
df['Rating Year'] = pd.to_numeric(df['Rating Year'], errors='coerce')
df = df.dropna(subset=['Rating Year'])
if not df.empty:
    df['Rating Year'] = df['Rating Year'].astype(int)

# Title and description
st.title('Sustainable Investments Dashboard')
st.write('Explore sustainable investments and revenues across industries.')

# Filter options
ckpg = st.multiselect('Select Industry (CKPG)', df['Corporate Knights Peer Group (CKPG)'].unique())
if ckpg:
    # Filter companies based on selected peer groups
    filtered_companies = df[df['Corporate Knights Peer Group (CKPG)'].isin(ckpg)]['Company Name'].unique()
else:
    filtered_companies = df['Company Name'].unique()

company = st.multiselect('Select Company', filtered_companies)
category = st.multiselect('Select Category', df['Category'].unique(), default=df['Category'].unique())

# Rating Year Dropdown
if not df.empty:
    years = df['Rating Year'].unique()
    year = st.selectbox('Select Rating Year', sorted(years))

    # Build the filter condition
    conditions = []
    if company:
        conditions.append(df['Company Name'].isin(company))
    if ckpg:
        conditions.append(df['Corporate Knights Peer Group (CKPG)'].isin(ckpg))
    if category:
        conditions.append(df['Category'].isin(category))

    # Apply filters with AND logic
    if conditions:
        filter_condition = conditions[0]
        for condition in conditions[1:]:
            filter_condition &= condition
    else:
        filter_condition = pd.Series([True] * len(df))  # No filters applied

    # Apply the filter condition
    filtered_df = df[filter_condition & (df['Rating Year'] == year)]

    # Check if any data is available after filtering
    if filtered_df.empty:
        st.write("No data available for the selected filters.")
    else:
        # Bar chart for PPP Value across categories
        fig = px.bar(filtered_df, x='Category', y='PPP Value', color='Corporate Knights Peer Group (CKPG)', 
                     title='PPP Value by Category and Industry', labels={'PPP Value': 'PPP Value (USD)'})
        st.plotly_chart(fig)

        # Show the filtered data at the bottom
        st.write('Filtered Data:', filtered_df)

        # Option to export filtered data
        st.download_button(label='Download Filtered Data as CSV', data=filtered_df.to_csv(index=False), 
                           file_name='filtered_data.csv', mime='text/csv')
else:
    st.warning("No valid data available for 'Rating Year'. Please check your data.")
