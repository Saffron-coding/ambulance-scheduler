from math import *

def haversine(lat1, lon1, lat2, lon2):
    R = 3959.87433  # this is in miles.  For Earth radius in kilometers use 6372.8 km

#convert degrees to radius
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

#Haversine formula

    a = sin(dLat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dLon / 2) ** 2
    c = 2 * asin(sqrt(a))

    return R * c

#find ETA in minutes

def haversine_eta(lat1, lng1, lat2, lng2, avg_speed_kmh=40):
    #Return straight-line distance (miles) and estimated minutes
    distance_miles = haversine(lat1, lng1, lat2, lng2)
    eta_minutes = (distance_miles / avg_speed_kmh) * 60
    return round(distance_miles, 2), round(eta_minutes, 1)