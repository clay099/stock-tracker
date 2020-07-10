from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import EmailType, PasswordType
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
import finnhub
from secrets import API_KEY
from sqlalchemy.exc import IntegrityError

from decimal import Decimal

# Configure API key
configuration = finnhub.Configuration(
    api_key={
        'token': API_KEY
    }
)

finnhub_client = finnhub.DefaultApi(finnhub.ApiClient(configuration))


db = SQLAlchemy()

bcrypt = Bcrypt()


class User(db.Model, UserMixin):
    """User model"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True,
                         info={'label': 'Username'})
    email = db.Column(EmailType, nullable=False, unique=True,
                      info={'label': 'Email'})
    password = db.Column(db.String, nullable=False,
                         info={'label': 'Password'})
    country = db.Column(db.String, nullable=False,
                        info={'label': 'Country'})
    state = db.Column(db.String,
                      info={'label': 'State'})

    stocks = db.relationship(
        'Stock', secondary="user_stocks",  backref='users')

    @classmethod
    def signup(cls, username, email, password, country, state):
        """
        signup with hashed password

        Returns:
            flask_sqlalchemy Object: new user object to be added to database
        """
        hashed_password = bcrypt.generate_password_hash(
            password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            country=country,
            state=state
        )
        db.session.add(user)
        return user

    @classmethod
    def check_password(cls, username, password):
        """check hashed password"""

        user = User.query.filter_by(
            username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    @classmethod
    def update_password(cls, user, password, confirm_password):
        if password == confirm_password:
            hashed_password = bcrypt.generate_password_hash(
                password).decode('UTF-8')
            user.password = hashed_password
            return user
        return False

    def __repr__(self):
        u = self
        return f'< User: id={u.id}, username={u.username}, email={u.email}, password=HIDDEN, country={u.country}, state={u.state} >'


class Stock(db.Model):
    """Stock model"""

    __tablename__ = "stocks"

    # basic details
    stock_symbol = db.Column(db.String, primary_key=True,
                             info={'label': 'Stock Symbol'})
    stock_name = db.Column(db.String, nullable=False,
                           info={'label': 'Stock Name'})
    country = db.Column(db.String)
    currency = db.Column(db.String)
    exchange = db.Column(db.String)
    ipo = db.Column(db.String)
    marketCapitalization = db.Column(db.String)
    name = db.Column(db.String)
    phone = db.Column(db.String)
    shareOutstanding = db.Column(db.String)
    weburl = db.Column(db.String)
    logo = db.Column(db.String)
    finnhubIndustry = db.Column(db.String)
    # advanced details
    yearlyHigh = db.Column(db.String)
    yearlyHighDate = db.Column(db.String)
    yearlyLow = db.Column(db.String)
    yearlyLowDate = db.Column(db.String)
    beta = db.Column(db.String)
    buy = db.Column(db.String)
    hold = db.Column(db.String)
    period = db.Column(db.String)
    sell = db.Column(db.String)
    strongBuy = db.Column(db.String)
    strongSell = db.Column(db.String)
    lastUpdated = db.Column(db.String)
    targetHigh = db.Column(db.String)
    targetLow = db.Column(db.String)
    targetMean = db.Column(db.String)
    targetMedian = db.Column(db.String)
    # peers
    peers = db.relationship(
        'Peer',  backref='stocks')

    @classmethod
    def add_stock_details(cls, stock_symbol):
        
        # get stock object
        s = Stock.query.get(stock_symbol)
        # get stock details
        returned_data = finnhub_client.company_profile2(
                symbol=stock_symbol)
        try:
            # fillstock details
            s.country = returned_data.country,
            s.currency = returned_data.currency,
            s.exchange = returned_data.exchange,
            s.ipo = returned_data.ipo,
            s.marketCapitalization = returned_data.market_capitalization,
            s.name = returned_data.name,
            s.phone = returned_data.phone,
            s.shareOutstanding = returned_data.share_outstanding,
            s.stock_symbol = returned_data.ticker,
            s.weburl = returned_data.weburl,
            s.logo = returned_data.logo,
            s.finnhubIndustry = returned_data.finnhub_industry
            
            # return stock object
            return s
        # stock not found
        except IntegrityError:
            return False

    def serialize_basic_stock_details(self):
        """Returns a dict representation of stock which we can turn into JSON"""
        return {
            'country': self.country,
            'currency': self.currency,
            'exchange': self.exchange,
            'ipo': self.ipo,
            'marketCapitalization': self.marketCapitalization,
            'name': self.name,
            'phone': self.phone,
            'shareOutstanding': self.shareOutstanding,
            'stock_symbol': self.stock_symbol,
            'weburl': self.weburl,
            'logo': self.logo,
            'finnhubIndustry': self.finnhubIndustry
        }
    
   
    @classmethod
    def add_basic_financial(cls, stock_symbol):
        # get stock object
        s = Stock.query.get(stock_symbol)
        # get basic financials
        stock_financials = finnhub_client.company_basic_financials(symbol=stock_symbol, metric='price')
        

        print("*********************************")
        print("stock_financials")
    
        try:
            # fillstock details
            s.yearlyHigh = stock_financials.metric['52WeekHigh']
            s.yearlyHighDate = stock_financials.metric['52WeekHighDate']
            s.yearlyLow = stock_financials.metric['52WeekLow']
            s.yearlyLowDate = stock_financials.metric['52WeekLowDate']
            s.beta = stock_financials.metric['beta']
            
            db.session.add(s)
            db.session.commit()

            return True
        # stock not found
        except IntegrityError:
            return False
    
    @classmethod
    def add_rec_trend(cls, stock_symbol):
        # get stock object
        s = Stock.query.get(stock_symbol)
        # get stock details
        returned_data = finnhub_client.recommendation_trends(
                symbol=stock_symbol)
        try:
            # s.buy = returned_data.[0].buy
            s.buy = returned_data[0].buy
            s.hold = returned_data[0].hold
            s.period = returned_data[0].period
            s.sell = returned_data[0].sell
            s.strongBuy = returned_data[0].strong_buy
            s.strongSell = returned_data[0].strong_sell

            db.session.add(s)
            db.session.commit()

            return True
        # stock not found
        except IntegrityError:
            return False

    @classmethod
    def add_target(cls, stock_symbol):
        # get stock object
        s = Stock.query.get(stock_symbol)
        # get stock details
        returned_data = finnhub_client.price_target(
                symbol=stock_symbol)
        try:
            s.lastUpdated = returned_data.last_updated
            s.targetHigh = returned_data.target_high
            s.targetLow = returned_data.target_low
            s.targetMean = returned_data.target_mean
            s.targetMedian = returned_data.target_median

            db.session.add(s)
            db.session.commit()

            return True
        # stock not found
        except IntegrityError:
            return False
    
    @classmethod
    def add_peers(cls, stock_symbol):
        # remove saved peers
        Peer.query.delete()
        # get stock object
        s = Stock.query.get(stock_symbol)
        # get stock details
        returned_data = finnhub_client.company_peers(
                symbol=stock_symbol)
        try:
            for peer in returned_data:
                if peer != stock_symbol:
                    p = Peer(lead_stock_symbol=stock_symbol, peer_stock_symbol=peer)

                    db.session.add(p)
                    db.session.commit()

            return True
        # stock not found
        except IntegrityError:
            return False
    

    def serialize_advanced_stock_details(self):
        """Returns a dict representation of stock which we can turn into JSON"""
        return {
            "yearlyHigh": self.yearlyHigh,
            "yearlyHighDate": self.yearlyHighDate,
            "yearlyLow": self.yearlyLow,
            "yearlyLowDate": self.yearlyLowDate,
            "beta": self.beta,
            "buy": self.buy,
            "hold": self.hold,
            "period": self.period,
            "sell": self.sell,
            "strongBuy": self.strongBuy,
            "strongSell": self.strongSell,
            "lastUpdated": self.lastUpdated,
            "targetHigh": self.targetHigh,
            "targetLow": self.targetLow,
            "targetMean": self.targetMean,
            "targetMedian": self.targetMedian
        }

    def __repr__(self):
        s = self
        return f'< Stock: stock_symbol={s.stock_symbol}, stock_name={s.stock_name}, country={s.country}, currency={s.currency}, exchange={s.exchange}, ipo={s.ipo}, marketCapitalization={s.marketCapitalization}, name={s.name}, phone={s.phone}, shareOutstanding={s.shareOutstanding}, stock_symbol={s.stock_symbol}, weburl={s.weburl}, logo={s.logo}, finnhubIndustry={s.finnhubIndustry} >'


class User_Stock(db.Model):
    """user_stock model"""

    __tablename__ = "user_stocks"

    stock_symbol = db.Column(db.String, db.ForeignKey(
        'stocks.stock_symbol'), primary_key=True,
        info={'label': 'Stock Symbol'})
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), primary_key=True,
        info={'label': 'User ID'})
    start_date = db.Column(db.DateTime, nullable=False,
                           info={'label': 'Start Date'})
    start_stock_price = db.Column(db.Numeric, nullable=False,
                                  info={'label': 'Starting Stock Price'})
    current_date = db.Column(db.DateTime, nullable=False,
                             info={'label': 'Current Date'})
    curr_stock_price = db.Column(db.Numeric, nullable=False,
                                 info={'label': 'Current Stock Price'})
    stock_num = db.Column(db.Integer, default=1,
                          info={'label': 'Number of Stocks', 'min': 1})
    

    @classmethod
    def add_stock(cls, user_id, stock_symbol, stock_num):
        """
        add stock to user_stock table

        Args:
            user_id (int): id to verify user
            stock_symbol (string): stock symbol
            stock_num (int): number of stocks to track

        Returns:
        if pass all functions:
           flask_sqlalchemy object: object to be committed
        if stock symbol is not found:
            returns none
        """

        stock_symbol = stock_symbol.upper()

        # check our DB for stock symbol
        check_stock = Stock.query.get(stock_symbol)
        # if Stock symbol not in our DB search finnhub
        if not check_stock:
            success = cls.add_stock_symbol(cls, stock_symbol)
            if not success:
                return None

        time = datetime.utcnow()
        quote = finnhub_client.quote(stock_symbol)
        price = quote.c

        # create new User_Stock
        add_user_stock = User_Stock(
            stock_symbol=stock_symbol,
            user_id=user_id,
            start_date=time,
            start_stock_price=price,
            current_date=time,
            curr_stock_price=price,
            stock_num=stock_num
        )
        db.session.add(add_user_stock)
        return add_user_stock
    @classmethod
    def add_stock_symbol(self, stock_symbol):
        """
        searches finnhub for the stock symbol.
        if found adds stock to our DB
        if not found returns none

        Args:
            stock_symbol (string): capitalized stock symbol to search
        """
        try:
            # search for stock on finnhub
            new_stock_profile = finnhub_client.company_profile2(
                symbol=stock_symbol)
            stock_name = new_stock_profile.name

            # add stock to our DB
            new_stock = Stock(stock_name=stock_name,
                              stock_symbol=stock_symbol)

            db.session.add(new_stock)
            db.session.commit()
            return True
        # stock not found
        except IntegrityError:
            return False

    @classmethod
    def get_users_stocks(cls, user_id):
        """
        searches database for user stocks, calculates portfolio initial and current value

        Args:
            user_id (int): user id to search

        Returns:
            Tuple: tuple contains:
                        flask_sqlalchemy Query Object: object representing all user stocks
                        Decimal: total value of stocks (since purchase)
                        Decimal: total current value of stocks
        """
        stocks = User_Stock.query.filter_by(user_id=user_id)
        total_initial_val = 0
        total_curr_val = 0
        for stock in stocks:
            stock = cls.update_stock(cls, stock)
            db.session.commit()

            if stock.stock_num:
                total_initial_val += (stock.start_stock_price *
                                      stock.stock_num)
                total_curr_val += (stock.curr_stock_price * stock.stock_num)
            else:
                total_initial_val += stock.start_stock_price
                total_curr_val += stock.curr_stock_price

        return (stocks, total_initial_val, total_curr_val)

    def update_stock(self, user_stock):

        time = datetime.utcnow()
        quote = finnhub_client.quote(user_stock.stock_symbol)
        price = "{: .2f}".format(quote.c)
        dec_price = Decimal(price)

        user_stock.current_date = time
        user_stock.curr_stock_price = dec_price

        return user_stock

    def __repr__(self):
        u = self
        return f'< User_Stock: stock_symbol={u.stock_symbol}, user_id={u.user_id}, start_date={u.start_date}, start_stock_price={u.start_stock_price}, current_date={u.current_date}, curr_stock_price={u.curr_stock_price}, stock_num={u.stock_num} >'

class News(db.Model):
    """news model"""

    __tablename__ = "news"

    id = db.Column(db.String, primary_key=True)
    category = db.Column(db.String)
    datetime = db.Column(db.String)
    headline = db.Column(db.String)
    image = db.Column(db.String)
    related = db.Column(db.String)
    source = db.Column(db.String)
    summary = db.Column(db.String)
    url = db.Column(db.String)

    @classmethod
    def get_news(self, stock_symbol=None):
        # drop all articles (DB does not need to keep all articles)
        News.query.delete()
        # if a stock symbol was passed through
        if stock_symbol:
            # todays date in format to be passed through
            today = datetime.today().strftime('%Y-%m-%d')
            #date 7 days ago in format to be passed through
            one_week = (datetime.today()-timedelta(days=7)).strftime('%Y-%m-%d')

            # get news articles from API
            news = finnhub_client.company_news(stock_symbol, _from=one_week, to=today)
            # no articles were found return false
            if (news == []):
                return False
            else:
                # for top 6 articles
                for n in news[:6]:
                    # create new article in DB
                    new_article = News(id=n.id, category=n.category, datetime=n.datetime, headline=n.headline, image=n.image, related=n.related, source=n.source, summary=n.summary, url=n.url)
                    db.session.add(new_article)
                    db.session.commit()
            
        else:
            news = finnhub_client.general_news('general')
            # no articles were found return false
            if (news == []):
                return False
            else:
            # for top 6 articles
                for n in news[:6]:
                    # create new article in DB
                    new_article = News(id=n.id, category=n.category, datetime=n.datetime, headline=n.headline, image=n.image, related=n.related, source=n.source, summary=n.summary, url=n.url)
                    db.session.add(new_article)
                    db.session.commit()

        # get all articles 
        articles = News.query.all()
        # return all articles
        return articles
        
    def serialize_news(self):
        """Returns a dict representation of news which we can turn into JSON"""
        return {
            'category': self.category,
            'datetime': self.datetime,
            'headline': self.headline,
            'image': self.image,
            'related': self.related,
            'source': self.source,
            'summary': self.summary,
            'url': self.url,
        }
    

    def __repr__(self):
        n = self
        return f'< News: id={n.id}, category={n.category}, datetime={n.datetime}, headline={n.headline}, image={n.image}, related={n.related}, source={n.source}, summary={n.summary}, url={n.url} >'

class Peer(db.Model):
    """Peers model"""

    __tablename__ = "peers"

    id = db.Column(db.Integer, primary_key=True)
    lead_stock_symbol = db.Column(db.String, db.ForeignKey(
        'stocks.stock_symbol'))
    peer_stock_symbol = db.Column(db.String)

    def __repr__(self):
        p = self
        return f'< Peer: id={p.id}, lead_stock_symbol={p.lead_stock_symbol}, peer_stock_symbol={p.peer_stock_symbol} >'

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)
