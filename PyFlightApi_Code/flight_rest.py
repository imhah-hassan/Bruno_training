#!C:\Apps\Python311 python
# encoding: utf8
import json
import logging.config
from datetime import datetime, timedelta, date as datetime_date
from dateutil.relativedelta import relativedelta
from random import randrange

from fastapi import FastAPI, Depends, HTTPException, status, Query, Body, Path, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

import config
import flights_db

app = FastAPI(title="FlightsApp Rest Api")

SECRET_KEY = 'XBhbnJM8IaQwaWVVv9RK'
ALGORITHM = "HS256"

security = HTTPBearer()

logging.config.fileConfig('logging.conf')
print("FlightsApp Rest Api")
print("Listening on http://localhost:" + str(config.port))
print("Sample request :  http://localhost:" + str(config.port) + "/Flights/10487")

def get_db():
    db = flights_db.sqlite_db()
    try:
        yield db
    finally:
        db.close_db()

# Authentication dependency
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: flights_db.sqlite_db = Depends(get_db)):
    token = credentials.credentials
    try:
        logging.info(f"Read token: {token}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        public_id: str = payload.get("public_id")
        if public_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token!")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token!")
    
    users = db.get_user_by_id(public_id)
    if not users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
    return users[0]

def require_admin(user: flights_db.User = Depends(get_current_user)):
    if user.profil != 'Admin':
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin profil needed")
    return user


@app.get('/', response_class=HTMLResponse)
def home():
    return f'''<h1>FlightsApp Rest Api</h1>
<p>Listening on http://localhost:{config.port}</p>
<p>Sample request :
http://localhost:{config.port}/Flights/?DepartureCity=Paris&ArrivalCity=London&Date=2021-09-03
</p>
'''

@app.post('/login')
def login_user(username: str = Body(..., embed=True), password: str = Body(..., embed=True), db: flights_db.sqlite_db = Depends(get_db)):
    users = db.get_user(username)
    if not users:
        return JSONResponse (status_code=401, content={"error": f"User not found : {username} "})

    user = users[0]

    if user.password == password:
        token = jwt.encode(
            {'public_id': user.id, 'exp': datetime.utcnow() + timedelta(minutes=30)},
            SECRET_KEY, algorithm=ALGORITHM)
        logging.info("Create token :" + token)
        return {"token": token, "profile":user.profil}
    else:
        return JSONResponse (status_code=401, content={"error": "Bad crédentiels"})

# POST  http://localhost:5000/Cities
#   {
#     "CityInitials":"CMN",
#     "CityName":"Casablanca"
# }
@app.get('/Users')
def GetUsers(user: flights_db.User = Depends(require_admin), db: flights_db.sqlite_db = Depends(get_db)):
    users = db.get_users()
    return [ob.model_dump() for ob in users]


#   GET http://localhost:5000/Cities?CityCode=PAR
@app.get('/Cities')
def GetCities(CityCode: str = Query(None), db: flights_db.sqlite_db = Depends(get_db)):
    city_initials = CityCode if CityCode else ''
    if CityCode is None:
        cities = db.get_cities()
        return [ob.model_dump() for ob in cities]
    else:
        city = db.get_city(city_initials)
        # Returning dicts for FastAPI to serialize to JSON automatically
        return city.model_dump()

# POST  http://localhost:5000/Cities
#   {
#     "CityInitials":"CMN",
#     "CityName":"Casablanca"
# }
@app.post('/Cities', status_code=201)
def CreateCity(city_data: dict = Body(...), user: flights_db.User = Depends(require_admin), db: flights_db.sqlite_db = Depends(get_db)):
    city = db.create_city(city_data.get('CityInitials'), city_data.get('CityName'))
    if city == -1:
        return JSONResponse(status_code=202, content={"Warning": f"City already exists : {city_data.get('CityName')} "})
    return city.model_dump()


#  PATCH http://localhost:5000/Cities/CMN
#   {"CityInitials": "CASA", "CityName": "Casablanca"}
@app.patch('/Cities/{CityInitials}')
def UpdateCity(CityInitials: str, city_data: dict = Body(...), user: flights_db.User = Depends(require_admin), db: flights_db.sqlite_db = Depends(get_db)):
    upd_city = db.get_city(CityInitials)
    if upd_city is None:
        return {"false": f"City not found  {CityInitials} "}
    
    new_city_initials = city_data.get('CityInitials')
    new_city_name = city_data.get('CityName')
    upd_city = db.update_city(CityInitials, new_city_initials, new_city_name)
    return upd_city.model_dump()

# DELETE  http://localhost:5000/Cities/Casablanca
@app.delete('/Cities/{CityInitials}')
def DeleteCity(CityInitials: str, user: flights_db.User = Depends(require_admin), db: flights_db.sqlite_db = Depends(get_db)):
    rows = db.delete_city(CityInitials)
    if rows == 1:
        return {"true": f"City deleted {CityInitials} "}
    elif rows == 0:
        return {"false": f"City not found  {CityInitials} "}
    elif rows == -1:
         return {"false": f"Flight exists from or to this city  {CityInitials} "}
    return {"false": "Error deleting city"}

# GET http://localhost:5000/RandomFlights?Count=10
@app.get('/RandomFlights')
def GetRandomFlights(Count: int = Query(10), Date: str = Query(None), db: flights_db.sqlite_db = Depends(get_db)):
    random_fligths = []
    cities = db.get_cities()
    date_str = Date if Date else ""
    for i in range(Count):
        current_date_str = date_str
        if current_date_str == '':
            futur = randrange(20) + 30
            dt = datetime_date.today() + relativedelta(days=futur)
            current_date_str = dt.strftime('%Y-%m-%d')
        DepartureCity = cities[randrange(10)].CityName
        ArrivalCity = DepartureCity
        while ArrivalCity == DepartureCity:
            ArrivalCity = cities[randrange(10)].CityName

        flights = db.get_flights(DepartureCity, ArrivalCity, current_date_str)
        if flights and isinstance(flights, list) and len(flights) > 0:
            index = randrange(len(flights))
            random_fligths.append(flights[index])

    return [ob.model_dump() for ob in random_fligths]

#   GET http://localhost:5000/Flights?DepartureCity=Paris&ArrivalCity=Denver&Date=2021-12-08
@app.get('/Flights')
def GetFlights(DepartureCity: str = Query(""), ArrivalCity: str = Query(""), Date: str = Query(""), db: flights_db.sqlite_db = Depends(get_db)):
    try:
        if Date:
            dt = datetime.strptime(Date, '%Y-%m-%d')
        d = datetime.strptime(Date, "%Y-%m-%d").date()
        if d < datetime_date.today():
            # Date dans le passé
            flights = -4
        else:
            flights = db.get_flights(DepartureCity, ArrivalCity, Date)
    except:
        # Date mauvais format
        flights = -3

    if flights == -1:
        return {"error": f"Invalid DepartureCity : {DepartureCity} "}
    elif flights == -2:
        return {"error": f"Invalid ArrivalCity : {ArrivalCity} "}
    elif flights == -3:
        return {"error": f"Invalid date format. Accepted format is  YYYY-MM-DD : {Date} "}
    elif flights == -4:
        return {"error": f"Booking date cannot be in the past : {Date} "}
    else:
        return [ob.model_dump() for ob in flights]

#   GET http://localhost:5000/Flights/16939
@app.get('/Flights/{flight_number}')
def GetFlightByNumber(flight_number: str, db: flights_db.sqlite_db = Depends(get_db)):
    if not flight_number.isnumeric():
        flight = -2
    else:
        flight = db.get_flight(flight_number)

    if flight == -1:
        return {"error": f"Unkown Flight  : {flight_number} "}
    elif flight == -2:
        return {"error": f"Flight number must be numeric  : {flight_number} "}
    else:
        return flight.model_dump()

#  PATCH http://localhost:5000/Flights/16939
#   {"Price": 185.0, "PriceFirst": 200.0, "PriceBusiness": 190.0}
@app.patch('/Flights/{flight_number}')
def UpdateFlightPrice(flight_number: str, price_data: dict = Body(...), user: flights_db.User = Depends(get_current_user), db: flights_db.sqlite_db = Depends(get_db)):
    upd_fligth = db.get_flight(flight_number)
    if upd_fligth == -1:
        return {"error": "Unkown flight"}

    upd_fligth = db.update_flight_price(flight_number, price_data)
    return upd_fligth.model_dump()

# POST  http://localhost:5000/Flights
#   {"Airline":"AF", "ArrivalCity":"Casablanca", "ArrivalTime":"10:30 AM", "DepartureCity":"Paris", "DepartureTime":"08:00 AM", "FlightNumber":99558, "Price":185.2, "DayOfWeek":"Monday"}
@app.post('/Flights', status_code=201)
def CreateFlight(flight_data: dict = Body(...), user: flights_db.User = Depends(require_admin), db: flights_db.sqlite_db = Depends(get_db)):
    flt_number = db.create_flight(flight_data)
    if flt_number > 0:
        flt = db.get_flight(flt_number)
        return flt.model_dump()
    else:
        return {"error": "Error creating flight"}


# DELETE  http://localhost:5000/Flights/12654
@app.delete('/Flights/{FlightNumber}')
def DeleteFlight(FlightNumber: str, user: flights_db.User = Depends(require_admin), db: flights_db.sqlite_db = Depends(get_db)):
    rows = db.delete_flight(FlightNumber)
    if rows == 1:
        return {"true": f"Flight deleted {FlightNumber} "}
    elif rows == 0:
        return {"false": f"FlightNumber not found  {FlightNumber} "}
    elif rows == -2:
        return {"false": f"FlightNumber has existing orders "}
    return {"false": "Error deleting flight"}

# GET  http://localhost:5000/FlightOrders?CustomerName=IMHAH
@app.get('/FlightOrders')
def GetOrders(CustomerName: str = Query(None), db: flights_db.sqlite_db = Depends(get_db)):
    orders = db.get_orders('', CustomerName)
    return [ob.model_dump() for ob in orders]

# GET  http://localhost:5000/FlightOrders/81
@app.get('/FlightOrders/{OrderNumber}')
def GetOrder(OrderNumber: str, db: flights_db.sqlite_db = Depends(get_db)):
    if not OrderNumber.isnumeric():
        return {"error": f"invalid order number {OrderNumber}"}
    else:
        orders = db.get_orders(OrderNumber, '')
        if len(orders) > 0:
            return orders[0].model_dump()
        else:
            return {"error": f"Order not found {OrderNumber}"}

# DELETE  http://localhost:5000/FlightOrders/81
@app.delete('/FlightOrders/{OrderNumber}')
def DeleteOrder(OrderNumber: str, db: flights_db.sqlite_db = Depends(get_db)):
    rows = db.delete_flight_order(OrderNumber)
    if rows == 1:
        return {"true": f"Order deleted {OrderNumber} "}
    else:
        return {"false": f"Order not found  {OrderNumber} "}

# DELETE  http://localhost:5000/FlightOrders
@app.delete('/FlightOrders')
def DeleteAllOrders(db: flights_db.sqlite_db = Depends(get_db)):
    orders = db.delete_all_orders()
    return [ob.model_dump() for ob in orders]

# POST  http://localhost:5000/FlightOrders
#   {   "DepartureDate":"2021-12-08",
#     "FlightNumber":16939,
#     "CustomerName": "IMHAH",
#     "NumberOfTickets":2,
#     "Class":"Economy"
# }
@app.post('/FlightOrders')
def CreateOrder(order_data: dict = Body(...), db: flights_db.sqlite_db = Depends(get_db)):
    DepartureDate = order_data.get('DepartureDate')
    if DepartureDate is None or DepartureDate == "":
        return JSONResponse(status_code=500, content={"error": f"Flight date cannot be empty or null"})
    if not db.date_in_the_past(DepartureDate):
        return JSONResponse(status_code=500, content={"error": f"Flight date cannot be in the past : {DepartureDate} "})
    
    CustomerName = order_data.get('CustomerName')
    FlightNumber = order_data.get('FlightNumber')
    NumberOfTickets = order_data.get('NumberOfTickets')
    FlightClass = order_data.get('Class')
    
    new_order = db.create_flight_order(CustomerName, DepartureDate, FlightNumber, NumberOfTickets, FlightClass)
    if new_order == -1:
        flight = db.get_flight(FlightNumber)
        return JSONResponse(status_code=500, content={"error": f"Ordered tickets too high. Seats available : {flight.SeatsAvailable} "})
    elif new_order == -2:
        return JSONResponse(status_code=500, content={"error": f"Unkown Flight  : {FlightNumber} "})
    elif new_order == -4:
         return JSONResponse(status_code=500, content={"error": f"Flight not exists "})
    elif new_order == -3:
         return JSONResponse(status_code=500, content={"error": f"No more seats available in flight  : {FlightNumber} "})
    elif new_order == -5:
         return JSONResponse(status_code=500, content={"error": "Number Of Tickets cannot be more than 10 "})
    elif new_order == -6:
         return JSONResponse(status_code=500, content={"error": f"Flight not available for departure date "})
    else:
        return new_order.model_dump()


#   PATCH http://localhost:5000/FlightOrders/81
# {   "DepartureDate":"2021-12-08",
#     "FlightNumber":16939,
#     "CustomerName": "IMHAH",
#     "NumberOfTickets":2,
#     "Class":"Economy"
# }
@app.patch('/FlightOrders/{OrderNumber}')
def UpdateOrder(OrderNumber: str, order_data: dict = Body(...), db: flights_db.sqlite_db = Depends(get_db)):
    if 'DepartureDate' not in order_data:
        return {"error": "Missing value DepartureDate"}
    if 'CustomerName' not in order_data:
        return {"error": "Missing value CustomerName"}
    if 'FlightNumber' not in order_data:
        return {"error": "Missing value FlightNumber"}
    if 'NumberOfTickets' not in order_data:
        return {"error": "Missing value NumberOfTickets"}
    if 'Class' not in order_data:
        return {"error": "Missing value Class"}

    DepartureDate = order_data['DepartureDate']
    if not db.date_in_the_past(DepartureDate):
        return JSONResponse(status_code=500, content={"error": f"Flight date cannot be in the past : {DepartureDate} "})
        
    CustomerName = order_data['CustomerName']
    FlightNumber = order_data['FlightNumber']
    NumberOfTickets = order_data['NumberOfTickets']
    FlightClass = order_data['Class']
    
    upd_order = db.update_flight_order(OrderNumber, FlightNumber, DepartureDate, FlightClass, CustomerName, NumberOfTickets)
    if upd_order == 0:
        return JSONResponse(status_code=500, content={"error": f"Order not found : {OrderNumber} "})
    elif upd_order == -1:
        return JSONResponse(status_code=500, content={"error": f"Ordered tickets too high : {FlightNumber} "})
    elif upd_order == -2:
        return JSONResponse(status_code=500, content={"error": f"Unkown Flight  : {FlightNumber} "})
    elif upd_order == -3:
        return JSONResponse(status_code=500, content={"error": f"No more seats available in flight  : {FlightNumber} "})
    elif upd_order == -4:
        return JSONResponse(status_code=500, content={"error": f"Ordered tickets cannot be more than 10 {FlightNumber} "})
    elif upd_order == -5:
        return JSONResponse(status_code=500, content={"error": f"Flight not available for departure date {FlightNumber}"})
    elif upd_order == -10:
        return JSONResponse(status_code=500, content={"error": f"Flight not found {FlightNumber}"})
    else:
        return upd_order.model_dump()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(config.port))