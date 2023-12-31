![screencapture-vigilant-spoon-wrrgjgx94xr4hg9xv-8501-app-github-dev-2023-12-04-17_40_09](https://github.com/amarshs/coding-challenge-3/assets/152249539/eeeab9f0-cf35-4baa-b100-95407a10fc0a)

This Dashbaord is part of Blend360 Coding Challenge 3
   
Objective:
Coding Challenge Problem Statement: Scraping and Dashboard Building using Streamlit 
Build a data pipeline that involves web scraping, data storage, transformation, and the creating and deploying of a Streamlit dashboard. 

Challenge Steps: 

Step 1: Web Scraping (25 points) 
Your first task is to scrape data from the website https://books.toscrape.com/.Extract the following information for each book: title, rating, price, and availability (In stock/Out of stock). 

Step 2: Data Storage (20 points) 
Store the scraped data into a database or data warehouse. You can choose between PostgreSQL or Snowflake(recommended). 

Step 3: Data Transformation (5 points) 
Apply any necessary transformations to the data if required. Ensure that the data is in a suitable format for analysis. 

Step 4: Streamlit Dashboard Development (25 points) 
Retrieve the data from the chosen database/data warehouse. Build a Streamlit dashboard that displays various comparisons and visualizations including Sorting and filtering options. 

Step 5: Deployment (25 points) 
Deploy the Streamlit application. Choose a suitable platform for deployment. Ensure that the deployed application is accessible through a web browser. 
 
Note: Submit all the code files & other relevant files into your respective folders, and submit your deployment link in a text file. 

Regarding the files:
- part1.ipynb: file has code of web scraping, pushing into snowflake, transformations in snowflake, pulling from snowflake
- coding_challenge_3.py: has pulling from snowflake and streamlit. It can be run on its own.
- book.csv has the data directly after web scraping without any transformations
- book_data_transformed is data pulled from snowflake after transformations
- deployment.txt is the public accessable link for the dashboard
