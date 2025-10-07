import requests

url = "https://restful-booker.herokuapp.com/booking"

headers = {

}

def postBooking (firtname, lastname, totalprice):

    body = {
        "firstname": firtname,
        "lastname": lastname,
        "totalprice": totalprice,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2018-01-01",
            "checkout": "2019-01-01"
        },
        "additionalneeds": "Breakfast"
    }

    return requests.post(headers=headers, json=body, url=url).json()



assert postBooking("naufal", "sunandar", True).get("bookingid") != N

print()