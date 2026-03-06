#!C:\Apps\Python311 python
# encoding: utf8
import sys
import traceback
import sqlite3 as sl
from pydantic import BaseModel
from typing import Optional
from datetime import date
from datetime import datetime
import calendar
import logging
import config

from datetime import datetime, timedelta
from os.path import abspath

logger = logging.getLogger(__name__)

class User(BaseModel):
   username: Optional[str] = None
   password: Optional[str] = None
   id: Optional[str] = None
   name: Optional[str] = None
   profil: Optional[str] = None

class Flight(BaseModel):
    Airline: Optional[str] = None
    ArrivalCity: Optional[str] = None
    ArrivalTime: Optional[str] = None
    DepartureCity: Optional[str] = None
    DepartureTime: Optional[str] = None
    FlightNumber: Optional[int] = None
    Price: Optional[float] = None
    PriceFirst: Optional[float] = None
    PriceBusiness: Optional[float] = None
    SeatsAvailable: Optional[int] = None
    DayOfWeek: Optional[str] = None

class FlightOrder(BaseModel):
   Class: Optional[str] = None
   CustomerName: Optional[str] = None
   DepartureDate: Optional[str] = None
   FlightNumber: Optional[int] = None
   NumberOfTickets: Optional[int] = None
   OrderNumber: Optional[int] = None
   TotalPrice: Optional[float] = None

class Order(BaseModel):
   OrderNumber: Optional[int] = None
   TotalPrice: Optional[float] = None

class City(BaseModel):
   CityInitials: Optional[str] = None
   CityName: Optional[str] = None

class   sqlite_db ():
    def __init__(self):
        logging.info (abspath(config.flight_db))
        self.con = sl.connect(abspath(config.flight_db))
        logging.info (self.con)
    def close_db(self):
        self.con.close()
    def log_sql_error (self, err):
        logging.error('SQLite error: %s' % (' '.join(err.args)))
        logging.error("Exception class is: ", err.__class__)
        logging.error('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        logging.error(traceback.format_exception(exc_type, exc_value, exc_tb))

    #
    # Utils
    #
    # Get day name from date
    def get_week_day(self, date_str):
        date_parts = date_str.split('-')
        dt = date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
        return (calendar.day_name[dt.weekday()])

    # Convert Flight Class number to name 1 - Business, 2-First, 3-Economy
    def flight_class_name (self, flght_class):
        flght_class_name = 'N/A'
        if flght_class == 1:
            flght_class_name = 'Business'
        elif flght_class == 2:
            flght_class_name = 'First'
        elif flght_class == 3:
            flght_class_name = 'Economy'
        return (flght_class_name)
    # Check if date is in the past
    def date_in_the_past(self, flight_date):
        flight_date = datetime.strptime(flight_date, "%Y-%m-%d")
        return(flight_date > datetime.now())
    # Convert Flight Class name  to Number  1 - Business, 2-First, 3-Economy
    def flight_class_id(self, flght_class_name):
        flight_class = 0
        if flght_class_name == 'Business':
            flight_class = 1
        elif flght_class_name == 'First':
            flight_class = 2
        elif flght_class_name == 'Economy':
            flight_class = 3
        return (flight_class)
    # Convert date + time (AM/PM) to datetime 24h
    def get_flight_datetime (self, departure_date, departure_time):
        time_parts = departure_time.split(' ')[0].split(':')
        date_parts = departure_date.split('-')
        hour = time_parts[0]
        if (departure_time.split(' ')[1] == 'PM'):
            hour = str(int(hour) + 12)
        return (date_parts[0] + '-' + str(int(date_parts[1])) + '-' +  str(int(date_parts[2])) + ' ' +  str(hour) +':' +  time_parts[1])

    #
    # Users
    #
    def get_user (self, user_name):
        users = []
        sql = "SELECT ID, username, Name, Password, Profil FROM Users WHERE username = '"+ user_name + "';"
        logging.info ('get_user %s', user_name)
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            res = cur.execute(sql)
            for r in res:
                user = User ()
                user.id = r[0]
                user.username = r[1]
                user.name = r[2]
                user.password = r[3]
                user.profil = r[4]
                users.append(user)
        return (users)

    #
    # Users
    #
    def get_users (self):
        users = []
        sql = "SELECT ID, username, Name, Password, Profil FROM Users ;"
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            res = cur.execute(sql)
            for r in res:
                user = User ()
                user.id = r[0]
                user.username = r[1]
                user.name = r[2]
                user.password = '********'
                user.profil = r[4]
                users.append(user)
        return (users)

    def get_user_by_id (self, id):
        users = []
        sql = "SELECT ID, username, Name, Password, Profil FROM Users WHERE ID = '"+ id + "';"
        logging.info ('get_user_by_id %s', id)
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            res = cur.execute(sql)
            for r in res:
                user = User ()
                user.id = r[0]
                user.username = r[1]
                user.name = r[2]
                user.password = r[3]
                user.profil = r[4]
                users.append(user)
        return (users)

    #
    # Cities
    #
    def get_city (self, city_initials):
        cities = []
        sql = 'SELECT c.CityInitials, c.CityName FROM Cities c WHERE c.CityInitials = \'' + city_initials + '\';'
        logging.info ('city_exists %s : ', city_initials)
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            res = cur.execute(sql)
            for r in res:
                city = City ()
                city.CityInitials = r[0]
                city.CityName = r[1]
                cities.append(city)
        if len(cities)>0:
            return (cities[0])
        else:
            return None
    def get_cities (self):
        cities = []
        sql = 'SELECT c.CityInitials, c.CityName FROM Cities c;'
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            res = cur.execute(sql)
            for r in res:
                city = City ()
                city.CityInitials = r[0]
                city.CityName = r[1]
                cities.append(city)
        return (cities)
    def get_city_by_name (self, city_name):
        cities = []
        sql = 'SELECT c.CityInitials, c.CityName FROM Cities c WHERE c.CityName like \'%' + city_name + '%\';'
        logging.info ('city_exists %s : ', city_name)
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            res = cur.execute(sql)
            for r in res:
                city = City ()
                city.CityInitials = r[0]
                city.CityName = r[1]
                cities.append(city)
        return (cities)
    def city_exists (self, city_name):
        cities = self.get_city_by_name (city_name)
        return (len(cities)>0)
    def create_city (self, city_initials, city_name):
        city = self.get_city(city_initials)
        if city is not None:
            return (-1)
        sql = 'INSERT INTO Cities (CityInitials, CityName) values (?, ?)'
        data = (city_initials, city_name)
        city = City()
        with self.con:
            try:
                self.con.execute(sql, data)
                city.CityInitials = city_initials
                city.CityName = city_name
            except sl.con.Error as err:
                self.log_sql_error (err)
        return (city)
    def update_city (self, city_initials, new_city_initials, new_city_name):
        city =  self.get_city(city_initials)
        if city is None:
            return 0
        sql = 'UPDATE Cities SET CityInitials = \''+ new_city_initials + '\''
        sql += ', CityName = \'' + new_city_name + "'"
        sql += ' WHERE CityInitials=\'' + str(city_initials) + '\''
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            cur.execute(sql)
        return (self.get_city(new_city_initials))
    def delete_city (self, city_initials):
        city = self.get_city (city_initials)
        if city is None:
            return 0
        if self.flights_exist (city_initials):
            return -1

        sql = 'DELETE FROM  Cities  WHERE CityInitials=\'' + city_initials +'\''
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            cur.execute(sql)
            row_deleted = cur.rowcount
        return (row_deleted)
    #
    # Flights
    #
    def create_flight (self, flight_data):
        sql = 'INSERT INTO Flights (Airline, Arrival, ArrivalInitials, ArrivalTime, Departure, DepartureInitials, DepartureTime, TicketPrice, TicketPriceFirst, TicketPriceBusiness, SeatsAvailable, DayOfWeek) '
        sql += ' values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        data = (flight_data['Airline'], flight_data['ArrivalCity'], flight_data['ArrivalInitials'],
                                        flight_data['ArrivalTime'],
                                        flight_data['DepartureCity'], flight_data['DepartureInitials'],
                                        flight_data['DepartureTime'],
                                        flight_data['Price'], flight_data['PriceFirst'], flight_data['PriceBusiness'],
                                        flight_data['SeatsAvailable'], flight_data['DayOfWeek'])
        with self.con:
            try:
                self.con.execute(sql, data)
                cursor = self.con.cursor()
                cursor.execute('select last_insert_rowid();')
                last_id = cursor.fetchone()[0]
                return last_id
            except sl.con.Error as err:
                self.log_sql_error (err)
        return 0
    def get_flights (self, departure_city, arrival_city, flight_date):
        logging.info ('get_flights departure_city : %s - arrival_city : %s - flight_date : %s ', departure_city, arrival_city, flight_date)
        flights = []
        day_name = ''
        if (not self.city_exists(departure_city)):
            return -1

        if (not self.city_exists(arrival_city)):
            return -2

        if (flight_date.find('-') > 0):
            try:
                day_name = self.get_week_day (flight_date)
            except:
                return -3
        sql = 'SELECT 	f.Airline , f.Arrival , f.ArrivalTime, f.Departure,f.DepartureTime , f.FlightNumber , f.TicketPrice, f.TicketPriceFirst, f.TicketPriceBusiness, f.SeatsAvailable, f.DayOfWeek FROM 	Flights f  '
        criterias = ''
        if (len(departure_city) > 0):
            criterias += ' f.Departure = \'' + departure_city + '\' '

        if (len(arrival_city) > 0):
            if (len(criterias) > 0):
                criterias += ' AND '
            criterias += ' f.Arrival = \'' + arrival_city + '\' '

        if (len(day_name) > 0):
            if (len(criterias) > 0):
                criterias += ' AND '
            criterias += ' f.DayOfWeek = \'' + day_name + '\' '

        if (len(criterias) > 0):
            sql = sql + ' WHERE ' + criterias

        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            res = cur.execute(sql)
            for r in res:
                flight = Flight()
                flight.Airline = r[0]
                flight.ArrivalCity = r[1]
                flight.ArrivalTime = r[2]
                flight.DepartureCity = r[3]
                flight.DepartureTime = r[4]
                flight.FlightNumber = r[5]
                flight.Price = round (r[6], 2)
                flight.PriceFirst = round (r[7],2)
                flight.PriceBusiness = round (r[8],2)
                flight.SeatsAvailable = round (r[9],0)
                flight.DayOfWeek = r[10]
                flights.append( flight )
        return (flights)
    def get_flight (self, flight_number):
        logging.info ('get_flight flight_number : %s  ', flight_number)
        sql = 'SELECT f.Airline , f.Arrival , f.ArrivalTime, f.Departure,f.DepartureTime , f.FlightNumber , f.TicketPrice, f.TicketPriceFirst, f.TicketPriceBusiness, f.SeatsAvailable, f.DayOfWeek FROM Flights f  '
        sql += ' WHERE f.FlightNumber  = ' + str(flight_number) + ';'
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            cur.execute(sql)
            row = cur.fetchone()
            if (not row is None):
                flight = Flight()
                flight.Airline = row[0]
                flight.ArrivalCity = row[1]
                flight.ArrivalTime = row[2]
                flight.DepartureCity = row[3]
                flight.DepartureTime = row[4]
                flight.FlightNumber = row[5]
                flight.Price = round(row[6], 2)
                flight.PriceFirst = round(row[7], 2)
                flight.PriceBusiness = round(row[8], 2)
                flight.SeatsAvailable = round(row[9], 0)
                flight.DayOfWeek = row[10]
            else:
                flight=-1
        return (flight)
    def delete_flight (self, flight_number):
        fights = self.get_flight (flight_number)
        if fights == -1:
            return 0
        orders = self.get_flight_orders(flight_number)
        if len(orders) > 0:
            return -2

        sql = 'DELETE FROM  Flights  WHERE FlightNumber=' + flight_number +';'
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            cur.execute(sql)
            row_deleted = cur.rowcount
        return (row_deleted)
    def get_seats_available (self, flight_number):
        sql = 'Select SeatsAvailable from Flights Where FlightNumber = ' + str(flight_number) + ';'
        logging.info(sql)
        cursor = self.con.cursor()
        cursor.execute(sql)
        seats = cursor.fetchone()[0]
        return (seats)
    def update_seats_available (self, flight_number, seats):
        if (seats > 0):
            seats = '+' + str (seats)
        elif (seats < 0):
            seats =  str (seats)
        elif (seats == 0):
            seats=''
        sql = 'UPDATE Flights SET SeatsAvailable =  SeatsAvailable ' + seats + ' WHERE FlightNumber =' + str(flight_number) + ';'
        logging.info(sql)
        self.con.execute(sql)
    def update_all_seats_available (self):
        sql = 'UPDATE Flights SET SeatsAvailable = 250 ;'
        logging.info(sql)
        self.con.execute(sql)
    def update_flight_price (self, flight_number, price_data):
        flt = self.get_flight(flight_number)
        if (flt.Price != price_data['Price']):
            sql = 'UPDATE Flights '
            sql += 'SET TicketPrice =  ' + str(price_data['Price'])
            sql += ', TicketPriceFirst =  ' + str(price_data['PriceFirst'])
            sql += ', TicketPriceBusiness =  ' + str(price_data['PriceBusiness'])
            sql += ' WHERE FlightNumber =' + str(flight_number) + ';'
            logging.info(sql)
            with self.con:
                try:
                    self.con.execute(sql)
                except sl.con.Error as err:
                    self.log_sql_error (err)

            sql = 'INSERT INTO Audit (tableName, tableColumn, kayName, kayValue, oldValue, newValue, updateDate) values(?, ?, ?, ?, ?, ?, ?)'
            data = ('Flights', 'TicketPrice', 'FlightNumber', str(flight_number), flt.Price, price_data['Price'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            logging.info(sql)
            logging.info(data)
            with self.con:
                try:
                    self.con.execute(sql, data)
                except sl.con.Error as err:
                    self.log_sql_error (err)


            sql = 'INSERT INTO Audit (tableName, tableColumn, kayName, kayValue, oldValue, newValue, updateDate) values(?, ?, ?, ?, ?, ?, ?)'
            data = ('Flights', 'TicketPriceBusiness', 'FlightNumber', str(flight_number), flt.PriceBusiness, price_data['PriceBusiness'], datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
            logging.info(sql)
            logging.info(data)
            with self.con:
                try:
                    self.con.execute(sql, data)
                except sl.con.Error as err:
                    self.log_sql_error (err)

            sql = 'INSERT INTO Audit (tableName, tableColumn, kayName, kayValue, oldValue, newValue, updateDate) values(?, ?, ?, ?, ?, ?, ?)'
            data = ('Flights', 'TicketPriceFirst', 'FlightNumber', str(flight_number), flt.PriceFirst, price_data['PriceFirst'], datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
            with self.con:
                try:
                    self.con.execute(sql, data)
                except sl.con.Error as err:
                    self.log_sql_error (err)

            flt.Price = price_data['Price']
            flt.PriceFirst = price_data['PriceFirst']
            flt.PriceBusiness = price_data['PriceBusiness']
        return (flt)
    def flights_exist (self, city_initials):
        sql = "Select FlightNumber from Flights f Where DepartureInitials = '"+city_initials+"' or ArrivalInitials = '"+city_initials+"';"
        logging.info ('flights_exist %s : ', city_initials)
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            res = cur.execute(sql)
            for r in res:
                return (True)
        return (False)

    #
    # Orders
    #
    def get_orders (self, order_number, customer_name):
        orders = []
        if order_number is None or len(order_number)==0:
            order_number=0
        try:
            order_number = int(order_number)
        except:
            return (orders)
        if customer_name is None:
            customer_name=''
        sql = 'SELECT 	o.OrderNumber , o.CustomerName , o.DepartureDate, o.FlightNumber , o.TicketsOrdered , o.Class, o.TotalPrice FROM	Orders o'
        criteria = ''
        if (order_number!=0):
            criteria = ' o.OrderNumber =  '  + str(order_number)
        if (customer_name != ''):
            if (len(criteria) > 0):
                criteria += ' AND o.CustomerName =  \'' + customer_name + '\''
            else:
                criteria += ' o.CustomerName =  \'' + customer_name + '\''

        if (len(criteria)>0):
            criteria = ' WHERE ' + criteria
        sql = sql + criteria + ';'
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            res = cur.execute(sql)
            for r in res:
                flight_class = self.flight_class_name (r[5])
                order = FlightOrder()
                order.Class = flight_class
                order.CustomerName = r[1]
                order.DepartureDate = r[2]
                order.FlightNumber = r[3]
                order.NumberOfTickets = r[4]
                order.TotalPrice = 0 if r[6] is None else round(r[6],2)
                order.OrderNumber = r[0]
                orders.append (order)
        return (orders)
    def get_flight_orders (self, flight_number):
        orders = []
        sql = 'SELECT o.OrderNumber, o.FlightNumber FROM Orders o WHERE o.FlightNumber='+flight_number+';'
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            res = cur.execute(sql)
            for r in res:
                order = FlightOrder()
                order.FlightNumber = r[0]
                order.OrderNumber = r[1]
                orders.append (order)
        return (orders)

    def create_flight_order (self, customer_name, departure_date, flight_number, tickets_ordered, flight_class):
        flight = self.get_flight(flight_number)
        if (tickets_ordered>10):
            return (-5)
        if (flight==-1):
            return (-4)
        total_price = round (flight.Price * float(tickets_ordered), 2)
        total_price = format(total_price, '.2f')
        if (flight.FlightNumber is None):
            return(-2)
        seats_availabe = flight.SeatsAvailable
        if (seats_availabe <= 0):
            return(-3)
        if (int(tickets_ordered) > seats_availabe):
            return (-1)
        last_id = 0
        day_name = self.get_week_day(departure_date)
        if day_name!=flight.DayOfWeek:
            # Vol non disponible ce jour
            return (-6)

        #  departure_date = get_flight_datetime('2021-02-05', flight.DepartureTime)
        departure_date = self.get_flight_datetime(departure_date, flight.DepartureTime)

        sql = 'INSERT INTO Orders (CustomerName, DepartureDate, FlightNumber, TicketsOrdered, Class, TotalPrice, AgentsName, SendSignatureWithOrder) values(?, ?, ?, ?, ?, ?, ?, ?)'
        data = (customer_name, departure_date, flight_number, tickets_ordered, self.flight_class_id(flight_class), total_price, 'Test', 'N')
        with self.con:
            self.con.execute(sql, data)
            cursor = self.con.cursor()
            cursor.execute('select last_insert_rowid();')
            last_id = cursor.fetchone()[0]
            self.update_seats_available(flight_number, -1*int(tickets_ordered))
        new_order = Order()
        new_order.OrderNumber = last_id
        new_order.TotalPrice = total_price
        return (new_order)
    def update_flight_order (self, order_number, flight_number, departure_date, flight_class, customer_name, number_of_tickets):
        totaPrice = 0
        orders =  self.get_orders (str(order_number), '')
        flight = self.get_flight(flight_number)
        if type(flight) == 'int':
            if flight<0:
                return (-10)
        if (len(orders)==0):
            return 0
        tickets_ordered_old = orders[0].NumberOfTickets
        class_id = self.flight_class_id(flight_class)
        if (class_id==0):
            return (-1)
        day_name = self.get_week_day(departure_date)
        if day_name!=flight.DayOfWeek:
            # Vol non disponible ce jour
            return (-5)
        if (number_of_tickets>10):
                return (-4)
        if flight_class == 'Economy':
            totaPrice = number_of_tickets*flight.Price
        if flight_class == 'First':
            totaPrice = number_of_tickets*flight.PriceFirst
        if flight_class == 'Business':
            totaPrice = number_of_tickets*flight.PriceBusiness

        totaPrice = round (totaPrice, 2)
        totaPrice = format(totaPrice, '.2f')


        departure_date = self.get_flight_datetime(departure_date, flight.DepartureTime)
        sql = 'UPDATE Orders SET Class = '+ str(class_id)
        sql += ', CustomerName = \''+customer_name + "'"
        sql += ', FlightNumber = ' + str(flight_number)
        sql += ', DepartureDate = \'' + str(departure_date) + "'"
        sql += ', TicketsOrdered = '+str(number_of_tickets)
        sql += ', TotalPrice = ' + str(totaPrice)
        sql += ' WHERE OrderNumber=' + str(order_number)
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            cur.execute(sql)
            self.update_seats_available(flight_number, tickets_ordered_old)
            self.update_seats_available(flight_number, -1 * int(number_of_tickets))
        return (self.get_orders(order_number, '')[0])

    def delete_flight_order (self, order_number):
        orders = self.get_orders (order_number, '')
        if (len(orders) == 0):
            return 0
        tickets_ordered = orders[0].NumberOfTickets
        flight_number= orders[0].FlightNumber
        sql = 'DELETE FROM  Orders WHERE OrderNumber=' + str(order_number)
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            cur.execute(sql)
            row_deleted = cur.rowcount
            self.update_seats_available(flight_number, tickets_ordered)
        return (row_deleted)
    def delete_all_orders (self):
        logging.info ("Delete all")
        orders = self.get_orders('','')
        with self.con:
            cur = self.con.cursor()
            try:
                cur.execute("DELETE FROM  Orders WHERE OrderNumber > 80;")
                cur.execute("UPDATE sqlite_sequence  SET seq = 80 WHERE name='Orders';")
                cur.execute("UPDATE sqlite_sequence  SET seq = 21000 WHERE name='Flights';")
                cur.execute("Update Flights Set SeatsAvailable = 250;")
                self.clean_audit()
                orders = self.get_orders('', '')
            except:
                logging.error("Delete all")
        return (orders)
    def clean_audit(self):
        logging.info("Clean up audit")
        with self.con:
            cur = self.con.cursor()
            try:
                cur.execute("DELETE FROM  Audit  ;")
                cur.execute("UPDATE sqlite_sequence  SET seq = 1 WHERE name='Audit';")
            except:
                logging.error("Clean up audit")
        return (0)


if __name__ == '__main__':
    sl = sqlite_db()
    '''
    print (sl.get_flight_datetime('2021-12-21', '8:00 AM'))
    print (sl.get_flight_datetime('2021-12-21', '8:00 PM'))
    print (sl.con)
    print (sl.city_exists ('Paris'))
    print (sl.city_exists ('Denver'))
    print (sl.get_flights ('Paris', 'London', '2021-12-25'))
    print (sl.get_flights ('Paris', 'Denver', '2021-12-25'))
'''

    print(sl.delete_city('Casablanca'))

    print(sl.delete_city('Anfa'))

    print (sl.update_flight_price ('10454', 163.4))
    # sl.delete_city('Casablanca')
    print(sl.create_city('CMN', 'Casablanca'))
    print (sl.update_city('Casablanca', 'CASA', 'Anfa'))
    print(sl.get_city('Casablanca'))
    print(sl.get_city(''))
    print(sl.delete_city('Anfa'))
    print(sl.delete_city('Casablanca'))
    # sl.create_flight(5896478523, 'AF', 'Casablanca' , '10:30 AM', 'Paris', '08:00 AM', 185.2, 'Monday')
    # print (sl.get_flight (5896478523))

    '''
    print (sl.create_flight_order ('IMHAH',  '2021-12-25', 10454, 2, 'Economy'))
    print (sl.get_orders('', 'IMHAH'))
    print (sl.get_orders('81', ''))
    print (sl.update_flight_order('81', 'First', 'IMHAH', 5))
    print(sl.get_orders('81', ''))
    '''
    #print(sl.delete_flight_order('81'))
    #print(sl.delete_all_orders())
    sl.close_db()
