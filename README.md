# stock-tracker - Project Proposal

**Goals**  
The website will be designed to assist with understanding the historic stock changes. It will allow for users to select in real time current stock ticket codes and review their historic performance. It will also allow for a user to save multiple stocks to their portfolio and select notification frequency to allow for daily, weekly, or monthly update on the performance of their portfolio.

**Target Users**  
It is anticipated that the application will be used for anyone who has an interest in stock performance and the ability to track their actual owned stock or simulate the performance of a hypothetical portfolio. This will allow new users who are interested into getting onto the stock market to track the performance of how a hypothetical portfolio would perform prior to needing to purchase any shares.

**Data**  
The data to be used for this site is to be pulled from Finhub.io API (documentation: https://finnhub.io/docs/api, & Official Python Library https://github.com/Finnhub-Stock-API) which will provide real time data for stock. In the beginning the application will be rather vanilla with a focus on stocks, their current price, and historical data. The API does allow for expansion into Foreign Exchange, crypto currency. It also has the functionality to provide "fundamental data" (financial statements, ownership, dividends, analysis's estimates) which may be able to extend the review process when selection stocks.

**Database**  
I have outlined below some of the information which will be collected and displayed to the users upon their request notification period

1. USER TABLE

    - id - primary key
    - Username
    - Email
    - Password - sensitive to be secured
    - Country
    - State

2. STOCKS TABLE

    - Stock Symbol - primary key
    - Stock Name
    - country
    - currency
    - exchange
    - ipo
    - marketCapitalization
    - name
    - phone
    - shareOutstanding
    - weburl
    - logo
    - finnhubIndustry
    - yearlyHigh
    - yearlyHighDate
    - yearlyLow
    - yearlyLowDate
    - beta
    - buy
    - hold
    - period
    - sell
    - strongBuy
    - strongSell
    - lastUpdated
    - targetHigh
    - targetLow
    - targetMean
    - targetMedian
    - price

3. USER_STOCK TABLE

    - stock symbol - foreign key - primary key
    - user_id - foreign key - primary key
    - start_date
    - start_stock_price
    - current_date (first day this will be the same as start date, otherwise it will update to be the date the notification is issued)
    - curr_stock_price (first day this will be the same as start date)
    - stock_num - sensitive to be secured

4. NEWS TABLE
    - id - primary key
    - category
    - datetime
    - headline
    - image
    - related
    - source
    - summary
    - url

**Outline**  
The user will be able to select stocks along with an amount to create a personalized portfolio.

The user will need to register so that they can login to their profile, review their portfolio and add / remove stocks as they see necessary.

The user will be able to see a summary of their portfolio including the date the start to track a stock, the number of stocks tracked, the starting stock price, the starting stock value (number of stocks times starting stock price), current date, current stock price, current stock value (number of stocks times current stock price), the change in % over this time, the change in dollars over this time.

Users will have the functionality to be able to sort based on alphabetical order of the stock symbol, or the change in % or the change in dollars.

The summary will also include a total portfolio position summarizing the total starting stock value, total current stock value, total change in %, total change in dollars over time.

The user will also be able to send a email snapshot of their portfolio so they can save this position in time.

The user will be able to see general busienss news on the home page

The user (login not required) will also be able to search for companies based on their stock symbol and obtain detailed company financial, stock recommendation and company news.

**Stretch Goals**

1. Add notifications when stocks you are following post price sensitive information
2. Add Foreign Exchange and / or crypto currency functionality

**Requirements**
please note if you download this code base you will need to:

1. pip install the requirements.txt file
2. Create a psql database called stock_tracker OR create another database and save it your your environment variable
3. create a secrets file including:

    - API_KEY - This can be obtained from https://finnhub.io/dashboard
    - APP_KEY - This can be any string
    - MAIL_USER - gamil email address\*
    - MAIL_PASSWORD - gmail password\*
      please note if you wish to use a separate mail client you will need to change app.py lines 25-32

**Live Heroku Server**
Should you wish to see a live example please visit https://cw-stock-tracker.herokuapp.com/
