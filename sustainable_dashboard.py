import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
df = pd.read_csv('SEI_Summary_2.csv', index_col=False)

# Ensure 'Rating Year' is numeric
df['PPP Value'].fillna(0, inplace=True)
df['Rating Year'] = pd.to_numeric(df['Rating Year'], errors='coerce')
df = df.dropna(subset=['Rating Year'])
if not df.empty:
    df['Rating Year'] = df['Rating Year'].astype(int)

# Title and description
st.title('Sustainable Economy Intelligence')
st.write('Explore sustainable investments and revenues across industries and countries.')

### GLOBAL FILTERS ###
st.header('Global Filters (Affect All Graphs)')
col1, col2, col3 = st.columns(3)

# Global Filters
with col1:
    ckpg = st.multiselect('Select Industry (CKPG)', sorted(df['Corporate Knights Peer Group (CKPG)'].unique()))
with col2:
    category = st.multiselect('Select Category', sorted(df['Category'].unique()), default=df['Category'].unique())
with col3:
    years = df['Rating Year'].unique()
    year = st.multiselect('Select Rating Year', sorted(years), default=sorted(years))

# Apply global filter conditions
global_conditions = []
if ckpg:
    global_conditions.append(df['Corporate Knights Peer Group (CKPG)'].isin(ckpg))
if category:
    global_conditions.append(df['Category'].isin(category))
if year:
    global_conditions.append(df['Rating Year'].isin(year))

if global_conditions:
    global_filter_condition = global_conditions[0]
    for condition in global_conditions[1:]:
        global_filter_condition &= condition
else:
    global_filter_condition = pd.Series([True] * len(df))  # No filters applied

global_filtered_df = df[global_filter_condition]

### BAR CHART BASED ON GLOBAL FILTERS ###
if global_filtered_df.empty:
    st.write("No data available for the selected filters.")
else:
    bar_fig = px.bar(global_filtered_df, x='Category', y='PPP Value', color='Corporate Knights Peer Group (CKPG)',
                     title='$ USD PPP by Category and Industry',
                     labels={'PPP Value': 'PPP Value (USD)'})
    st.plotly_chart(bar_fig)

### GRAPH-SPECIFIC FILTERS ###
st.header('Additional Filters (Affect Graphs Below)')

col4, col5 = st.columns(2)
with col4:
    company = st.multiselect('Select Company', sorted(global_filtered_df['Company Name'].unique()))
    location = st.multiselect('Select Location of Headquarters', sorted(global_filtered_df['Location of Headquarters'].unique()))
with col5:
    tier_1 = st.selectbox('Select CK Taxonomy Tier 1', sorted(global_filtered_df['CK Taxonomy Tier 1'].unique()))
    tier_2_options = global_filtered_df[global_filtered_df['CK Taxonomy Tier 1'] == tier_1]['CK Taxonomy Tier 2'].unique()
    tier_2 = st.multiselect('Select CK Taxonomy Tier 2', sorted(tier_2_options))

# Apply graph-specific filters on top of global filters
specific_conditions = []
if company:
    specific_conditions.append(global_filtered_df['Company Name'].isin(company))
if location:
    specific_conditions.append(global_filtered_df['Location of Headquarters'].isin(location))
if tier_1:
    specific_conditions.append(global_filtered_df['CK Taxonomy Tier 1'] == tier_1)
if tier_2:
    specific_conditions.append(global_filtered_df['CK Taxonomy Tier 2'].isin(tier_2))

if specific_conditions:
    specific_filter_condition = specific_conditions[0]
    for condition in specific_conditions[1:]:
        specific_filter_condition &= condition
else:
    specific_filter_condition = pd.Series([True] * len(global_filtered_df))  # No specific filters applied

# Apply the graph-specific filters
specific_filtered_df = global_filtered_df[specific_filter_condition]

### CHARTS BASED ON SPECIFIC FILTERS ###
if specific_filtered_df.empty:
    st.write("No data available for the selected filters.")
else:
    # Trend analysis line chart
    trend_fig = px.line(specific_filtered_df, x='Rating Year', y='PPP Value', color='Company Name',
                        title='$ USD PPP by Year and Company',
                        labels={'PPP Value': 'PPP Value (USD)', 'Rating Year': 'Year'},
                        markers=True)
    trend_fig.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=1))
    st.plotly_chart(trend_fig)

    # Sunburst chart
    sunburst_fig = px.sunburst(specific_filtered_df, path=['CK Taxonomy Tier 1', 'CK Taxonomy Tier 2', 'Company Name'],
                               values='PPP Value', title='$ USD PPP by CK Taxonomy Tier',
                               labels={'PPP Value': 'PPP Value (USD)'})
    sunburst_fig.update_traces(textinfo="label+percent entry", insidetextorientation="radial")
    st.plotly_chart(sunburst_fig)

    # World map scatter plot
    world_map = px.scatter_geo(specific_filtered_df,
                               locations='Location of Headquarters',
                               locationmode='country names',
                               color='Category',
                               hover_name='Company Name',
                               size='PPP Value',
                               projection='equirectangular',
                               title='$ USD PPP by Location and Category')
    world_map.update_geos(
        showcoastlines=True, coastlinecolor="Black",
        showland=True, landcolor="Green",
        showocean=True, oceancolor="LightBlue",
        showlakes=True, lakecolor="Blue"
    )
    st.plotly_chart(world_map)

    # Option to download filtered data
    st.download_button(label='Download Filtered Data as CSV', data=specific_filtered_df.to_csv(index=False), 
                       file_name='filtered_data.csv', mime='text/csv')
