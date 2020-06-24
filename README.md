# stock-tracker - Project Proposal

**Goals**  
The website will be designed to assist with understanding the historic stock changes. It will allow for users to select in real time current stock ticket codes and review their historic performance. It will also allow for a user to save multiple stocks to their portfolio and select notification frequency to allow for daily, weekly, or monthly update on the performance of their portfolio. 


**Target Users**  
It is anticipated that the application will be used for anyone who has an interest in stock performance and the ability to track their actual owned stock or simulate the performance of a hypothetical portfolio. This will allow new users who are interested into getting onto the stock market to track the performance of how a hypothetical portfolio would perform prior to needing to purchase any shares.  

**Data**  
The data to be used for this site is to be pulled from Finhub.io API which will provide real time data for stock. In the beginning the application will be rather vanilla with a focus on stocks, their current price, and historical data. The API does allow for expansion into Foreign Exchange, crypto currency. It also has the functionality to provide "fundamental data" (financial statements, ownership, dividends, analysists estimates) which may be able to extend the review process when selection stocks. 

**Database**  
I have outlined below some of the information which will be collected and displayed to the users upon their request notification period
1. USER TABLE 
    - id - primary key
    - Username - sensitive to be secured
    - Email - sensitive to be secured
    - Password - sensitive to be secured
    - Country
    - State
  
2. STOCKS TABLE
   - Stock Symbol - primary key
   - Stock Name
  
 3. USER_STOCK_TABLE
    - id - primary key
    - stock symbol - foreign key
    - user_id - foreign key
    - notification period - daily, weekly, monthly
    - start date
    - stock price start date
    - current date (first day this will be the same as start date, otherwise it will update to be the date the notification is issued)
    - stock price current date (first day this will be the same as start date)
    - Number of stocks to track - sensitive to be secured

**Outline**  
The user will be able to select stocks along with an amount to create a personalized portfolio.   

The user will also select a notification period which will set how often they are notified about their portfolio via email. The notification will show their performance from year to date (from start date), monthly to date, weekly to date and daily to date (if daily is selected you will be provided will all options, if weekly is selected you will be provided all above options (e.g. will exclude daily data) etc. The notifications will include % change along with total $ change for each requested period.  

The user will be able to login to their profile and review their portfolio and add / remove stocks as they see necessary. This will also give the user access to candle stick data for the historic performance of the stocks they are reviewing.  

**Stretch Goals**
1. Add fundamental data to the user’s portfolio available online so they can review further company information
2. Add notifications when stocks you are following post price sensitive information
3. Add Foreign Exchange and / or crypto currency functionality 
4. List news articles which mention the stock you are following
