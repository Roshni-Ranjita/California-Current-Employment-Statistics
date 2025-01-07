import streamlit as st
import pandas as pd
import numpy as np
import base64
import plotly.express as px

# Function to set background image using HTML and CSS
def set_background(image_path):
    """
        Sets a custom background image for the Streamlit application.

        This function applies a specified image as the background for a Streamlit app
        using inline CSS. The image is converted to a base64-encoded string to embed
        it directly into the CSS.

        Args:
            image_path (str): The file path of the image to be used as the background.

        Returns:
            None: This function modifies the Streamlit app's layout directly by injecting
                HTML and CSS. No return value.
    """
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/webp;base64,{base64_image}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def eda(df, c1, c2):
    """
        Displays the Exploratory Data Analysis (EDA) page for employment data.

        This function provides insights into the employment data based on selected groupings. 
        It includes an interactive bar chart for top entities, a breakdown of the distribution 
        in a pie chart, and detailed data tables.

        Args:
            df (pd.DataFrame): The input DataFrame containing employment data.
            c1 (str): The primary column name for grouping data (e.g., "Area Name").
            c2 (str): The secondary column name for analyzing distributions (e.g., "Industry Title").

        Returns:
            None: The function directly renders interactive visualizations and tables using Streamlit.

        Features:
            - Bar chart for the top 10 `c1` entities by employment.
            - Dropdown filter for selecting a specific `c1` entity to analyze.
            - Pie chart for `c2` distribution within the selected `c1`.
            - Scrollable data tables for detailed analysis.
    """
    grouped_df= df.groupby(c1)['Current Employment'].sum().reset_index().sort_values('Current Employment', ascending=False)
    # Display rest of the counties with scrolling
    st.subheader(f"{c1} wise employment")
    # Create interactive bar plot using Plotly
    top_10_c1 = grouped_df.head(10)
    fig = px.bar(top_10_c1, x=c1, y='Current Employment', 
                title=f"Top 10 {c1} by Employment",
                labels={c1: c1, 'Current Employment': 'Employment'},
                color='Current Employment', color_continuous_scale='Viridis')
    
    # Show interactive plot
    st.plotly_chart(fig)
    
    st.dataframe(grouped_df.tail(len(grouped_df) - 8), use_container_width=True)
    
    # Streamlit Dropdown for selecting County
    c1_list = df[c1].unique()
    selected_c1 = st.selectbox(f"Select {c1}", c1_list)
    c1_data = df[df[c1] == selected_c1].sort_values(by='Current Employment', ascending=False).reset_index()
    
    
    # If there are more than 7 rows, group the remaining ones as "Others"
    if len(c1_data) > 7:
        top_7 = c1_data.head(7)
        others = c1_data.iloc[7:]
        others_sum = others['Current Employment'].sum()
        others_data = pd.DataFrame({c2: ['Others'], 'Current Employment': [others_sum]})
        c1_data_t7 = pd.concat([top_7, others_data], ignore_index=True)
    else:
        c1_data_t7= c1_data.copy()
    st.subheader(f"{c2} wise breakdown for {selected_c1} {c1} ")
    # Create a Pie chart (Circular Chart) to display the distribution
    fig = px.pie(c1_data_t7, names=c2, values='Current Employment', 
                title=f"{c2} Distribution in {selected_c1}",
                color=c2, color_discrete_sequence=px.colors.qualitative.Set2)
    # Display the Pie chart
    st.plotly_chart(fig)
    
    # Display the table with occupation data
    st.dataframe(c1_data.tail(len(grouped_df) - 8), use_container_width=True)

# Reading DataFrames
desc = pd.read_csv('data/data_description.csv')

# Set Streamlit app config for a wider layout and light theme
st.set_page_config(layout="wide", page_title="California CES Analysis", initial_sidebar_state="expanded")

# Set background image
pic = 'pics/background_image.jpeg'
set_background(pic)

# Page navigation state
st.sidebar.title("Navigation")
options = st.sidebar.radio("Select a Section", ["Introduction", "IDA", "EDA", "Upcoming"])

# Function to load different sections
if options == "Introduction":
    st.markdown(
        "<h1 style='color: gold;'>Introduction</h1>", 
        unsafe_allow_html=True
    )
    # First Text Block: Introduction to Wine
    st.markdown("""
    ### Significance of California
    California is a prime state for employment due to its diverse economy, spanning technology, entertainment, agriculture, tourism, 
    and manufacturing, offering opportunities across industries. As home to Silicon Valley and leading universities like Stanford and 
    UC Berkeley, it fosters innovation, entrepreneurship, and a highly skilled workforce. With the largest economy in the U.S., strong 
    labor protections, and a vibrant cultural environment, California attracts both employers and employees. Studying its employment trends 
    is vital for understanding economic health, workforce dynamics, and the factors driving job creation in one of the most influential economies 
    in the world.
    """)

    # Embed the YouTube video
    st.markdown("#### Contribution of California in US GDP")
    st.image("pics/gdp.jpg", caption="State wise contribution in GDP in USA ", use_container_width=True)
    st.markdown("California hold about 15 percent of US GDP in the year 2019")



elif options == "IDA":
    st.markdown(
        "<h1 style='color: gold;'>Initial Data Analysis (IDA)</h1>", 
        unsafe_allow_html=True
    )
    st.markdown("""
    ### About the Data

    #### Source ([Link](https://data.ca.gov/dataset/current-employment-statistics-ces-2/resource/98b69522-557e-464a-a2be-4226df433da1))
    **Data.ca.gov** is California's open data portal, centralizing public data from state agencies to enhance transparency, collaboration, 
    and innovation. Managed by GovOps, it supports data-driven projects like sustainability initiatives and resource management tools.

    #### Tables
    **California CES**: Contains details of employment statistics of California over the years (2014 to 2024) across various industries.
    """)
    st.table(desc)
    st.markdown("""
    ### Missing Value
    The dataset has no missing or invalid value.
    """)
    st.image("pics/Missing_Value.png", caption="Heatmap of Missing Data", use_container_width=True)

# EDA page
elif options == "EDA":
    st.markdown(
        "<h1 style='color: gold;'>Exploratory Data Analysis (EDA)</h1>", 
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        # Dropdown filter for Year (2014 to 2024)
        year = st.selectbox("Select Year", list(range(2024, 2013, -1)))

    with col2:
        # Dropdown filter for choosing between country-wise occupation or occupation-wise country
        filter_option = st.selectbox("Select Analysis Type", ["County-wise Industry", "Industry-wise County"])
    
    df= pd.read_csv(f'data/{year}.csv')
    # Remove leading and trailing spaces in column names
    df['Industry Title'] = df['Industry Title'].str.strip()
    # Drop columns containing 'Total' or 'Other' (case-insensitive match)
    df = df[~df['Industry Title'].str.contains(r'\b(Total|Other)\b', case=False, na=False)]
    df= df.groupby(['Area Name', 'Industry Title'])['Current Employment'].mean().round().reset_index()
    
    df.columns=['County', 'Industry','Current Employment']
    c1='County'
    c2='Industry'
    if filter_option == "County-wise Industry":
        st.write(f"Showing data for {year}: {filter_option}")
        eda(df, 'County', 'Industry')
    else:
        st.write(f"Showing data for {year}: {filter_option}")
        eda(df, 'Industry', 'County')



    
elif options == "Upcoming":
    st.markdown(
        "<h1 style='color: gold;'>Future Scope</h1>", 
        unsafe_allow_html=True
    )
    st.markdown("""
    ### Regression / Time Series Analysis:
    Apply regression or time series analysis to forecast the CES (Current Employment Statistics) values for 2025 and beyond.
    """)
# Footer
st.sidebar.markdown("---")
st.sidebar.write("Created by Roshni Bhowmik") 
