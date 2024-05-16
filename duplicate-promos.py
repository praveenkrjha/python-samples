import pandas as pd
import json
import requests
import os

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
    payload = {
        "grant_type": "client_credentials",
        "client_id": "rentallocrtsvc",
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(TOKEN_ENDPOINT, data=payload)
    jwt_token = response.json()["access_token"]
    print(f"JWT Token: {jwt_token}")
    return jwt_token

def get_headers():
    jwt_token = get_jwt_token()
    
    return {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
        "validate-date" : "false"
    }

def get_existing_promotion_codes():
    headers = get_headers()

    SEARCH_PROMO_URL = f"{BASE_API_URL}/v1/promotion?pageNumber=1&pageSize=5000&sortField=createdAt&sortOrder=DESC"
    exising_promotions_resp = requests.get(SEARCH_PROMO_URL, headers=headers)
    existing_promotions = exising_promotions_resp.json().get("promotions")
    existing_codes = [promo["code"] for promo in existing_promotions]
    return existing_codes

existing_codes = get_existing_promotion_codes()

CREATE_PROMO_URL = f"{BASE_API_URL}/v1/promotion"

json_files = [file for file in os.listdir("qa-promos") if file.endswith(".json")]

max_duplicates = 500
for json_file in json_files:
    duplicate_counter = 1
    with open(f"qa-promos/{json_file}") as file:
        headers = get_headers()

        json_data = json.load(file)
        originalPromoCode = json_data["code"]
        originalDescription = json_data["description"]
        while duplicate_counter <= max_duplicates:
            counter = str(duplicate_counter)
            promoCode = originalPromoCode
            if(len(originalPromoCode + counter) > 20):
                promoCode = originalPromoCode[:20 - len(counter)] + counter
            else:
                promoCode = originalPromoCode + counter
        
            if promoCode in existing_codes:
                print(f"Promo Code: {promoCode} already exists")
                duplicate_counter += 1
                continue
            json_data["code"] = promoCode
            json_data["name"] = promoCode
            newDescription =  originalDescription + " (duplicated)"
            json_data["description"] = newDescription
            json_data['calculations'][0]["code"] = promoCode
            json_data['calculations'][0]["description"] = newDescription
            # json_string = json.dumps(json_data, indent=4)
            # print(f"Creating Promo: {json_string}")
            
            response = ""
            response = requests.post(CREATE_PROMO_URL, json=json_data, headers=headers).json()
                
            print(f"Promo Code: {promoCode} -> {response}")
            if "status" in response and response["status"] == 401:
                print("Token expired. Requesting a new token")
                headers = get_headers()
                continue

            duplicate_counter += 1
            print("========================================================================")

