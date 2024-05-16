import pandas as pd
import json
import requests
import os

JWT_TOKEN = ""

# DEV
# BASE_API_URL = "https://promotion-service.awsdevapps.penske.com"
# TOKEN_ENDPOINT = "https://sso.devapps.penske.com/auth/realms/ocpsso/protocol/openid-connect/token"
# CLIENT_SECRET = "KIKjvAH6lAaRrEoXiYMr9YThkcb37J1n"

# QA
BASE_API_URL = "https://promotion-service.awsqaapps.penske.com"

# PRE-PROD
# BASE_API_URL = "https://promotion-service.awspreapps.penske.com"

TOKEN_ENDPOINT = "https://sso.qaapps.penske.com/auth/realms/ocpsso/protocol/openid-connect/token"
CLIENT_SECRET = "GyDjMhCpaux7sVf0KZ4L0NwDHUwd95FK"

def get_jwt_token():
    global JWT_TOKEN
    if JWT_TOKEN == "":
        payload = {
            "grant_type": "client_credentials",
            "client_id": "rentallocrtsvc",
            "client_secret": CLIENT_SECRET
        }

        response = requests.post(TOKEN_ENDPOINT, data=payload)
        JWT_TOKEN = response.json()["access_token"]
        print(f"JWT Token: {JWT_TOKEN}")


get_jwt_token()
CREATE_PROMO_URL = f"{BASE_API_URL}/v1/promotion"

BUSINESS_CLASS = ["S/A SLEEPER","MEDIUM VAN","T/A SLEEPER","REEFER TRAILER","HIGH ROOF CARGO VAN","FLATBED TRAILER","TADC/ TADT","SADC/SADT","FLATBED","CONTAINER","REEFER","LITE DUTY","TRAILER"]
VEHICLE_CLASS = ["15' Van","12 Parcel Van","16' Reefer Van","20' Reefer Van","10' Flatbed Truck","16' Flatbed Truck","T/A Tractor","28' Van Trailer","40' Van Trailer","45' Van Trailer","48' Van Trailer","32' Reefer Trailer","53' Reefer Trailer","53' Flatbed Trailer","Pickup Truck","26' Electric Van","48' Storage Container","Electric T/A Sleeper","14' Parcel Van","16' One Way Van","22' Van","22' Reefer Van","24' Reefer Van","14' Flatbed Truck","20' Flatbed Truck","Yard Tractor","S/A Tractor Sleeper","S/A Tractor Premium Sleeper","S/A Tractor Super Premium Sleeper","42' Reefer Trailer","45' Flatbed Trailer","TADC CNG","Electric High Roof Cargo Reefer Van","Panel Truck","12' One Way Van","15' Parcel Van","14' Cube Van","15 Cube Van","10' Van","16' Van","48 Reefer +LG","14' Reefer Van","18' Flatbed Truck","22' Flatbed Truck","T/A Tractor Cab Over","T/A Tractor Premium Sleeper","32' Van Trailer","53' Van Trailer","28' Reefer Trailer","45' Reefer Trailer","42' Flatbed Trailer","48' Flatbed Trailer","48 dry van +LG","53 dry van +LG","SADC CNG","One Way High Roof Cargo Van","Electric High Roof Cargo Van","High Roof Cargo Van With Shelving","18' Van","20' Van","24' Van","25' Van","26' Van","22' One Way Van","26' One Way Van","26' Reefer Van","26' Flatbed Truck","High Roof Cargo Van","26 One Way Van with Liftgate","18' Reefer Van","24' T/A Reefer Van","12' Flatbed Truck","24' Flatbed Truck","S/A Tractor","S/A Tractor Cab Over Sleeper","16' Electric Van","T/A Tractor Sleeper","T/A Tractor Super Premium Sleeper","42' Van Trailer","40' Reefer Trailer","48' Reefer Trailer","40' Flatbed Trailer","53 Reefer +LG","24' T/A Van","53' Storage Container","18' Step Van","20' Step Van","Electric T/A DayCab","16' Cube with Shelf"]


#THIS IS FOR DEV
# ASSET_CLASS = ["4003", "4004", "4005", "4001", "2027", "2022", "2018", "2020", "2024", "2025", "2026", "6020", "6025", "6026", "2124", "2019", "2021", "5010", "5004", "5003", "5005", "7132", "7153", "7142", "7149", "7128", "7145", "7140", "7148", "7154", "2109", "2110", "2108", "7253", "7245", "7242", "7248", "7240", "5002", "5006", "5000", "5007", "4000", "4006", "4002", "3010", "3016", "3014", "3020", "3018", "3022", "3026", "3012", "3024", "8048", "8053", "2516", "2520", "2522", "2524", "2515", "2514", "2526", "2518", "2624", "2015", "1210", "1008", "1214", "6015", "1108", "6010", "1215", "1314", "1315", "2010", "2016", "6008", "2017", "1317", "7028", "7040", "7045", "7048", "7032", "7053", "7049", "7054", "7042"]

#THIS IS FOR QA
ASSET_CLASS = ["2015","1210","2516","2520","3010","3016","5002","7028","7040","7045","7048","7132","7153","7253","1008","2027","8048","5010","1214","6015","2022","2522","2524","3014","3020","4000","4003","4004","4005","7142","7245","5006","2515","1108","6010","1215","1314","1315","2010","2016","7149","2514","3018","3022","5000","5004","7032","7053","7128","7145","7242","7248","7049","7054","4006","6008","2109","2110","2018","2020","2024","2025","2026","6020","6025","2526","3026","2108","6026","2518","2624","3012","3024","4002","4001","2017","5003","5005","7042","7140","7148","7240","7154","2124","8053","2019","2021","5007","1317"]

headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json",
        "validate-date" : "false"
}

output_folder = "/Users/praveen/Documents/SampleApps/python/promo-generator/output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def get_existing_promotion_codes():
    SEARCH_PROMO_URL = f"{BASE_API_URL}/v1/promotion?pageNumber=1&pageSize=5000&sortField=createdAt&sortOrder=DESC"
    exising_promotions_resp = requests.get(SEARCH_PROMO_URL, headers=headers)
    existing_promotions = exising_promotions_resp.json().get("promotions")
    existing_codes = [promo["code"] for promo in existing_promotions]
    return existing_codes

existing_codes = get_existing_promotion_codes()

df_sheets = pd.read_excel('existing_promo_codes-New.xlsx', sheet_name=None)
for sheet_name, df in df_sheets.items():
    marketingType = "Partner" if sheet_name == "Partner Codes" else "Nationwide"
    for index, row in df.iterrows():
        # create a new promotion only if the promotion code is from this list
        # if(row["PROMOTION_CODE"] not in ["SPRING24","FLOWERS24","SUNNY24","HAPPY24","SUMMER24","FALL24","THANKFUL24","HOLIDAY24", "STUDENT", "MILITARY"]):
        #     continue
    
        # Skip if the promotions is already created
        pCode = str(row['PROMOTION_CODE']).replace(" ", "")
        promoCode = f"{pCode}-RT" if row['RENTAL_TYPE'] == "L" else f"{pCode}-OW"
        if promoCode in existing_codes:
            print(f"Promotion code {promoCode} already exists. Skipping...")
            continue

        vehicle_discount =  {
                        "chargeableUnitsFunction":  "Vehicle",
                        "calculationType": "Simple",   # add all vehicle codes except for 9000 and 9200 (Tow vehicles) for vehicle. For tow, send only 9000 and 9200. 
                        "chargeFor": [x for x in ASSET_CLASS] + ["9000", "9200"] if row['APPLY_TRUCK'] == "Y" and row['APPLY_TOW'] == "Y" 
                                else ["9000", "9200"] if row['APPLY_TOW'] == "Y" else ASSET_CLASS, 
                        "chargeableUnits": [  # For mileage, this would be miles. For supply, this would be Quantity. OW=Trip. RT=Day
                            "Day" if row['RENTAL_TYPE'] == "L" else "Trip"
                        ],
                        "simpleTiers": [
                            {
                                "valueType": "rate", 
                                "value": row['DISCOUNT'], 
                                "rangeFrom": 0,
                                "rangeTo": 999999
                            }
                        ],
                        "discountId": "D1"
                    }
        
        mileage_discount =  {
                        "chargeableUnitsFunction":  "Mileage",
                        "calculationType": "Simple",  # How do we find this value?
                        "chargeFor": ["Mileage"],
                        "chargeableUnits": [  
                            "Miles"
                        ],
                        "simpleTiers": [
                            {
                                "valueType": "rate", 
                                "value": row['DISCOUNT'], 
                                "rangeFrom": 0,
                                "rangeTo": 999999
                            }
                        ],
                        "discountId": "D2"
                    }

        supply_discount = []
        supply_type_values = ["PADS", "HTOW", "HTDY", "BOXW", "BOXS", "BOXM", "BOXL", "LOCK", "TAPE", "ROPE"]
        
        supply_index = 3
        for supply_type in supply_type_values:
            if supply_type == "HTOW" and row['RENTAL_TYPE'] not in ["O", "B"]:
                continue
            if supply_type == "HTDY" and row['RENTAL_TYPE'] not in ["L", "B"]:
                continue
            discount = {
                "minDiscountAllowed": 4.9E-324,
                "calculationType": "NforM",
                "chargeableUnits": [
                    "Quantity"
                ],
                "chargeableUnitsFunction": "Supply",
                "chargeFor": [
                    supply_type
                ],
                "maxDiscountAllowed": 99999.0,
                "nForMTier": {
                    "nItems": {
                        "nType": supply_type,
                        "nRange": [
                            {
                                "unit": "Quantity",
                                "value": 1.0
                            }                        ],
                        "ratePerUnit": row['DISCOUNT'],
                        "computationType": "rate"
                    },
                    "mItems": {
                        "mType": ASSET_CLASS,
                        "mRange": [
                            {
                                "unit": "Quantity",
                                "value": 1.0
                            }
                        ]
                    },
                    "mConditionalItems": ASSET_CLASS
                },
                "simpleTiers": [],
                "minInvoiceAmount": 0.0,
                "stackable": False,
                "discountId": "D" + str(supply_index)
            }
            supply_index += 1
            supply_discount.append(discount)

        # supply_discount_Str = json.dumps(supply_discount, indent=4)
        # print(supply_discount_Str)
        
        json_data = {
        "promoCodeVersion": "1",
        "isActive": "true",
        "isEnabled": "true",
        "name": row['DISPLAY_NAME'],
        "code": promoCode,
        "description": row['DISPLAY_NAME'] + " (existing promotion)",
        "autoApply": False,
        "marketingType": marketingType, 
        "geographicalHierarchy": "LOCN", # How do we find this value?
        "locationType": [ # How do we find this value?
            "Penske",
            "Home Depot",
            "Agent"
        ],
        "sameAsPickupLocationFlag": "true" if row['RENTAL_TYPE'] == "L" else "false",
        "startDateTime": f"{row['START_DATE'].strftime('%m/%d/%Y')} 00:00:01",
        "endDateTime": f"{row['END_DATE'].strftime('%m/%d/%Y')} 23:59:59",
        "calculations": [
            {
                "code": promoCode,
                "description": row['DISPLAY_NAME'],
                "combinable": False, 
                "discounts": [ # Create multiple discounts based on the number of flags (APPLY_TRUCK, APPLY_MILEAGE etc.) selected.

                ]
            }
        ],
        "additionalProperties": { 
            "vehicleCategory": BUSINESS_CLASS,
            "vehicleClass": "Business Class" # This would be Business class for now. 
        },
        "scope": {
            "assertion1": {
                "expression": "customer.customerType",
                "operator": "in",
                    "values": ["Personal"] if row['BUSINESS_TYPE'] == "H" else ["Business"] if row['BUSINESS_TYPE'] == "C" else ["Personal", "Business"]
            },
            "binaryOperator": "and",
            "assertion2": {
                "assertion1": {
                    "assertion1": {
                        "assertion1": {
                            "assertion1": {
                                "assertion1": {
                                    "assertion1": {
                                        "assertion1": {
                                            "assertion1": {
                                                "assertion1": {
                                                    "expression": "channel",
                                                    "operator": "in",
                                                    "values": ["ConsumerWeb", "ConsumerMobile", "CRES", "RentalNet"] 
                                                        if row['BUSINESS_TYPE'] == "H"
                                                        else ["CommercialWeb", "Penske1", "FleetInsight", "RentalNet" ]
                                                },
                                                "binaryOperator": "and",
                                                "assertion2": {
                                                    "expression": "tripType",
                                                    "operator": "eq",
                                                    "values": [
                                                        "RoundTrip" if row['RENTAL_TYPE'] == "L" else "OneWay"
                                                    ]
                                                }
                                            },
                                            "binaryOperator": "and",
                                            "assertion2": {
                                                "expression": "pickUpLocation.region",
                                                "operator": "eq",
                                                "values": [
                                                    "all"
                                                ]
                                            }
                                        },
                                        "binaryOperator": "and",
                                        "assertion2": {
                                            "expression": "dropOffLocation.region",
                                            "operator": "eq",
                                            "values": [
                                                "all"
                                            ]
                                        }  
                                    },
                                    "binaryOperator": "and",
                                    "assertion2": {
                                        "expression": "lineItemDetails.assetDetails.assetClass",
                                        "operator": "in",
                                        "values": ASSET_CLASS
                                    }
                                },
                                "binaryOperator": "and",
                                "assertion2": {
                                    "expression": "booking.bookingDate",
                                    "operator": "gte",
                                    "values": [
                                        f"{row['START_DATE'].strftime('%m/%d/%Y')}" 
                                    ]
                                }
                            },
                            "binaryOperator": "and",
                            "assertion2": {
                                "expression": "booking.bookingDate",
                                "operator": "lte",
                                "values": [
                                f"{row['END_DATE'].strftime('%m/%d/%Y')}" 
                                ]
                            }
                        },
                        "binaryOperator": "and",
                        "assertion2": {
                            "expression": "booking.dayOfWeek",
                            "operator": "in",
                            "values": [
                                "Monday",
                                "Tuesday",
                                "Wednesday",
                                "Thursday",
                                "Friday",
                                "Saturday",
                                "Sunday"
                            ]
                        }
                    },
                    "binaryOperator": "and",
                    "assertion2": {
                        "expression": "dropOff.dayOfWeek",
                        "operator": "in",
                        "values": [
                            "Monday",
                            "Tuesday",
                            "Wednesday",
                            "Thursday",
                            "Friday",
                            "Saturday",
                            "Sunday"
                        ]
                    }
                },
                "binaryOperator": "and",
                "assertion2": {
                    "expression": "pickUp.dayOfWeek",
                    "operator": "in",
                    "values": [
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                        "Sunday"
                    ]
                }
            }
        },
        "combinable": False,
        "status": "Active"
    }
        
        if row['APPLY_TRUCK'] == "Y" or row['APPLY_TOW'] == "Y":
            json_data['calculations'][0]['discounts'].append(vehicle_discount)
        if row['APPLY_MILEAGE'] == "Y" and row['RENTAL_TYPE'] == "L": # Mileage discount is only applicable for Round Trips
            json_data['calculations'][0]['discounts'].append(mileage_discount)
        if row['APPLY_ACCESSORIES'] == "Y":
            json_data['calculations'][0]['discounts'] += supply_discount

        json_string = json.dumps(json_data, indent=4)
        # print(json_string)

        file_name = os.path.join(output_folder, f"{promoCode}.json")
        with open(file_name, "w") as file:
            file.write(json_string)

        try:
            response = ""
            response = requests.post(CREATE_PROMO_URL, headers=headers, json=json_data).json()
            print(f"Promo Code: {promoCode} -> {response}")
        except Exception as e:
            print(f"An error occurred while creating promo {promoCode}: {str(e)}")

        print("========================================================================")
