import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import snowflake
import snowflake.connector as snow
from snowflake.connector.pandas_tools import write_pandas
import streamlit as st
import matplotlib.pyplot as plt


#  Data Scraping

base_url = "https://books.toscrape.com/catalogue/page-{}.html"
page_number = 1
count = 1

# Open a CSV file for writing
with open('book_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    # Create a CSV writer
    csv_writer = csv.writer(csvfile)

    # Write header row
    csv_writer.writerow(["Title", "Rating", "Price", "Availability"])

    while True:
        url = base_url.format(page_number)

        # Send an HTTP request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all the book containers on the page
            book_containers = soup.find_all('article', class_='product_pod')

            # If no books are found, break the loop
            if not book_containers:
                break

            # Loop through each book container and extract information
            for book in book_containers:
                # Extract title
                title = book.h3.a['title']

                # Extract rating
                rating = book.p['class'][1]


                # Extract price
                price = book.select('div p.price_color')[0].text

                # Extract availability
                availability = book.select('div p.instock.availability')[0].text.strip()

                # Write the extracted information to the CSV file
                csv_writer.writerow([title, rating, price, availability])

                # Print the extracted information
                # print(f"Book No: {count}")
                # print(f"Title: {title}")
                # print(f"Rating: {rating}")
                # print(f"Price: {price}")
                # print(f"Availability: {availability}")
                # print("-" * 40)

                # Increment the book count
                count += 1

            # Move to the next page
            page_number += 1

        else:
            # print(f"Failed to retrieve the page. Status code: {response.status_code}")
            break

# Connect to snowflake
## Phase I: Truncate/Delete the current data in the table
# The connector...
conn = snow.connect(user="AMARSH",
   password= "SQtcfg655DgL9A",
   account="ytvggyp-ay55760",
)
# (FYI, if you don't want to hard code your password into a script, there are
# some other options for security.)

conn.cursor().execute("CREATE WAREHOUSE IF NOT EXISTS snowflake")
conn.cursor().execute("USE WAREHOUSE snowflake")
conn.cursor().execute("CREATE DATABASE IF NOT EXISTS blend")
conn.cursor().execute("USE DATABASE blend")
conn.cursor().execute("CREATE SCHEMA IF NOT EXISTS coding_challenge")
conn.cursor().execute("USE SCHEMA coding_challenge")

original = r"book_data.csv" # <- Replace with your path.
delimiter = "," # Replace if you're using a different delimiter.

# Get it as a pandas dataframe.
total = pd.read_csv(original, sep = delimiter)
total.rename(columns={"Title": "TITLE",
                      "Rating": "RATING",
                      "Price": "PRICE",
                      "Availability": "AVAILABILITY"},
                       inplace=True)
conn.cursor().execute("CREATE OR REPLACE TABLE books (Title STRING, Rating STRING, Price STRING, Availability STRING)")

write_pandas(conn, total, 'BOOKS')
sql_code = """
UPDATE BOOKS
SET 
  PRICE = CAST(SUBSTRING(PRICE, 2) AS FLOAT),
  AVAILABILITY = CASE WHEN AVAILABILITY = 'In stock' THEN 1 ELSE 0 END,
  RATING = CASE
              WHEN RATING = 'One' THEN 1
              WHEN RATING = 'Two' THEN 2
              WHEN RATING = 'Three' THEN 3
              WHEN RATING = 'Four' THEN 4
              WHEN RATING = 'Five' THEN 5
              ELSE NULL
           END;
"""
# Execute the SQL code
conn.cursor().execute(sql_code)

## Phase III: Turn off the warehouse.
# Create a cursor object.
cur = conn.cursor()
cur.execute("ALTER WAREHOUSE snowflake SUSPEND")

# Close your cursor and your connection.
cur.close()
conn.close()

# Pull from snowflake

snowflake_params = {
    'user':"AMARSH",
   'password':"SQtcfg655DgL9A",
   'account':"ytvggyp-ay55760",
    'warehouse': 'snowflake',
    'database': 'blend',
    'schema': 'coding_challenge',
}

conn = snowflake.connector.connect(**snowflake_params)
cur = conn.cursor()
cur.execute('SELECT * FROM BOOKS')
result = cur.fetchall()
column_names = [desc[0] for desc in cur.description]
df = pd.DataFrame(result, columns=column_names)
# print(df)
conn.close()
df.to_csv("book_data_transformed.csv")

# Streamlit Deployment

# Load the data
df = pd.read_csv('book_data_transformed.csv')

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
    st.subheader("Total Available Books")
    st.markdown("<div style='text-align: center; border: 1px solid #d3d3d3; padding: 10px;'>"
                f"<p style='font-size: 24px;'>{total_available_books}/{total_books}</p></div>", unsafe_allow_html=True)

# Display the average cost of a book
with col3:
    st.subheader("Average Cost of a Book")
    st.markdown("<div style='text-align: center; border: 1px solid #d3d3d3; padding: 10px;'>"
                f"<p style='font-size: 24px;'>${df['PRICE'].mean():.2f}</p></div>", unsafe_allow_html=True)

# Display the average rating of a book
with col4:
    st.subheader("Average Rating of a Book")
    st.markdown("<div style='text-align: center; border: 1px solid #d3d3d3; padding: 10px;'>"
                f"<p style='font-size: 24px;'>{df['RATING'].mean():.2f}</p></div>", unsafe_allow_html=True)

# Create a layout with 2 columns for the tables
col5, col6 = st.columns(2)

# Display the 5-star rated books with minimum cost in a table
with col5:
    st.subheader("5-Star Rated Books with Minimum Cost:")
    top_rated_books = df[df['RATING'] == 5].sort_values(by='PRICE').head(5)
    st.table(top_rated_books[['TITLE', 'RATING', 'PRICE', 'AVAILABILITY']])

# Display the "Book Data" table with reduced height
with col6:
    st.subheader("Book Data:")
    st.dataframe(df, height=205, width= 1000)

# Create a layout with 3 columns for histogram, pie chart, and line plot
col7, col8, col9 = st.columns([1, 1, 1])
# Display histogram for the number of books in each price range
with col7:
    st.subheader("Histogram for Book Prices")
    fig, ax = plt.subplots(figsize=(6, 4))  # Adjust the figsize as needed
    counts, bins, _ = ax.hist(df['PRICE'], bins=range(int(df['PRICE'].min()), int(df['PRICE'].max()) + 2), edgecolor='black')

    ax.set_xlabel('Price Range (Bins of $1)', fontsize=10)
    ax.set_ylabel('Number of Books', fontsize=10)
    ax.set_title('Distribution of Book Prices', fontsize=12)

    # Annotate each bar with the number of books
    for count, bin_edge in zip(counts, bins[:-1]):
        if count > 0:
            ax.text(bin_edge + 0.5, count, str(int(count)), ha='center', va='bottom', fontsize=8)

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

# Display price vs average ratings plot
# Display line plot for average price vs ratings
with col9:
    st.subheader("Line Plot for Average Price vs Ratings")
    
    # Calculate average price for each rating
    avg_price_by_rating = df.groupby('RATING')['PRICE'].mean()

    # Create a line plot
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(avg_price_by_rating.index, avg_price_by_rating.values, marker='o', linestyle='-')
    
    # Customize the plot
    ax.set_xlabel('Ratings', fontsize=12)
    ax.set_ylabel('Average Price', fontsize=12)
    ax.set_title('Average Price vs Ratings', fontsize=14)
    
    # Set x-axis ticks to only show values 1 through 5
    ax.set_xticks([1, 2, 3, 4, 5])
    
    # Use st.pyplot() to display the plot with adjusted width and height
    st.pyplot(fig, use_container_width=True)


