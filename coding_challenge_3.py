# Import necessary libraries
import csv
import pandas as pd
import snowflake
import snowflake.connector as snow
from snowflake.connector.pandas_tools import write_pandas
import streamlit as st
import matplotlib.pyplot as plt

# Connect to Snowflake and fetch data

snowflake_params = {
    'user': "AMARSH",
    'password': "SQtcfg655DgL9A",
    'account': "ytvggyp-ay55760",
    'warehouse': 'snowflake',
    'database': 'blend',
    'schema': 'coding_challenge',
}

conn = snowflake.connector.connect(**snowflake_params)
cur = conn.cursor()
cur.execute('SELECT * FROM TRANSFORMED_BOOKS')
result = cur.fetchall()
column_names = [desc[0] for desc in cur.description]
df = pd.DataFrame(result, columns=column_names)
conn.close()

# Streamlit Deployment

# Set page title and color
st.set_page_config(page_title="Online Bookstore Dashboard", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

# Header with different color and box
st.markdown("<div style='background-color: #f0f0f0; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>"
            "<h1 style='text-align: center; color: #ff6347;'>Online Bookstore Dashboard</h1></div>", unsafe_allow_html=True)

# Create a layout with 4 columns
col2, col3, col4 = st.columns([1, 1, 1])

# Display the total available books as a fraction of total books
with col2:
    total_books = df.shape[0]
    total_available_books = df['AVAILABILITY'].sum()
    st.markdown("<div style='text-align: center; border: 1px solid #d3d3d3; padding: 10px;'>"
                "<h3>Total Available Books</h3>"
                f"<p style='font-size: 24px;'><span></span> {total_available_books}/{total_books}📚</p></div>", unsafe_allow_html=True)

# Display the average cost of a book
with col3:
    st.markdown("<div style='text-align: center; border: 1px solid #d3d3d3; padding: 10px;'>"
                "<h3>Average Cost of a Book</h3>"
                f"<p style='font-size: 24px;'>£{df['PRICE'].mean():.2f} <span>&#x1F4B0;</span></p></div>", unsafe_allow_html=True)

# Display the average rating of a book
with col4:
    st.markdown("<div style='text-align: center; border: 1px solid #d3d3d3; padding: 10px;'>"
                "<h3>Average Rating of a Book</h3>"
                f"<p style='font-size: 24px;'>{df['RATING'].mean():.2f}/{5} <span>&#x2B50;</span></p></div>", unsafe_allow_html=True)

# Create a layout with 2 columns for the tables
col5, col6 = st.columns(2)

# Display the 5-star rated books with minimum cost in a table
with col5:
    st.subheader("5-Star Rated Books with Minimum Cost:")
    top_rated_books = df[df['RATING'] == 5].sort_values(by='PRICE').head(7)
    
    # Format the 'PRICE' column to have only two decimal places
    top_rated_books['PRICE'] = top_rated_books['PRICE'].apply(lambda x: f"£{x:.2f}")
    
    st.table(top_rated_books[['TITLE', 'RATING', 'PRICE', 'AVAILABILITY']])

# Display the "Book Data" table with reduced height and rating filter options
with col6:
    st.subheader("Book Data:")
    
    # Filter the DataFrame based on selected ratings
    selected_ratings = st.multiselect("Select Ratings:", [1, 2, 3, 4, 5], default=[1, 2, 3, 4, 5])
    filtered_df = df[df['RATING'].isin(selected_ratings)]
    
    # Format the 'PRICE' column with a pound sign before displaying
    filtered_df['PRICE'] = filtered_df['PRICE'].apply(lambda x: f"£{x:.2f}")

    # Display the filtered DataFrame
    st.dataframe(filtered_df, height=205, width=1000)

# Create a layout with 3 columns for histogram, pie chart, and line plot
col7, col8, col9 = st.columns([1, 1, 1])

# Display histogram for the number of books in each price range
with col7:
    st.subheader("Histogram for Book Prices")
    fig, ax = plt.subplots(figsize=(6, 4))  # Adjust the figsize as needed
    counts, bins, _ = ax.hist(df['PRICE'], bins=range(int(df['PRICE'].min()), int(df['PRICE'].max()) + 2), edgecolor='black')

    ax.set_xlabel('Price Range (Bins of £1)', fontsize=10)
    ax.set_ylabel('Number of Books', fontsize=10)
    ax.set_title('Distribution of Book Prices', fontsize=12)

    # Annotate each bar with the number of books
    for count, bin_edge in zip(counts, bins[:-1]):
        if count > 0:
            ax.text(bin_edge + 0.5, count, str(int(count)), ha='center', va='bottom', fontsize=6)

    # Use st.pyplot() to display the plot with adjusted width and height
    st.pyplot(fig, use_container_width=True)  # Adjust the width and height as needed

# Display pie chart for the distribution of ratings
with col8:
    st.subheader("Pie Chart for Ratings Distribution")
    fig, ax = plt.subplots(figsize=(6, 4.3))
    rating_counts = df['RATING'].value_counts()
    ax.pie(rating_counts, labels=rating_counts.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig, use_container_width=True)

# Display line plot for average price vs ratings
with col9:
    st.subheader("Line Plot for Average Price vs Ratings")
    
    # Calculate average price for each rating
    avg_price_by_rating = df.groupby('RATING')['PRICE'].mean()

    # Create a line plot
    fig, ax = plt.subplots(figsize=(6, 4.3))
    ax.plot(avg_price_by_rating.index, avg_price_by_rating.values, marker='o', linestyle='-')
    
    # Annotate each point with its average price
    for x, y in zip(avg_price_by_rating.index, avg_price_by_rating.values):
        ax.text(x, y, f'£{y:.2f}', ha='left', va='bottom', fontsize=8)

    # Customize the plot
    ax.set_xlabel('Ratings', fontsize=12)
    ax.set_ylabel('Average Price (£)', fontsize=12)
    ax.set_title('Average Price vs Ratings', fontsize=14)
    
    # Set x-axis ticks to only show values 1 through 5
    ax.set_xticks([1, 2, 3, 4, 5])

    # Format y-axis labels with two decimal places
    ax.yaxis.set_major_formatter('£{x:.2f}')
    
    # Use st.pyplot() to display the plot with adjusted width and height
    st.pyplot(fig, use_container_width=True)
