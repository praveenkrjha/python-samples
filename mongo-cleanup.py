from pymongo import MongoClient
import requests

jwt_token = ""
# DEV
# BASE_API_URL = "https://promotion-service.awsdevapps.penske.com"
# TOKEN_ENDPOINT = "https://sso.devapps.penske.com/auth/realms/ocpsso/protocol/openid-connect/token"
# CLIENT_SECRET = "KIKjvAH6lAaRrEoXiYMr9YThkcb37J1n"

# QA
BASE_API_URL = "https://promotion-service.awsqaapps.penske.com"
TOKEN_ENDPOINT = "https://sso.qaapps.penske.com/auth/realms/ocpsso/protocol/openid-connect/token"
CLIENT_SECRET = "GyDjMhCpaux7sVf0KZ4L0NwDHUwd95FK"

def query_records_db(item_to_find):
    mongo_client = MongoClient("mongodb+srv://glread:vUJHxNqfaWye1LEq@cluster-stg-pl-0.9ya4g.mongodb.net/")
    db = mongo_client["rentalnetstgdb"]
    collection = db["Promotions"]
    # uncomment below line to delete all documents from the provided collection
    # collection.delete_many({})
    existing_documents = []
    documents = collection.find({"description": {"$regex": item_to_find}})
    for document in documents:
        existing_documents.append({"id": document["_id"], "code": document["code"]})
        print(f"{document['_id']}, {document['code']}")
    # for value_to_delete in values_to_delete:
    #     collection.delete_many({"description": value_to_delete})
    return existing_documents

def query_records_api(item_to_find):
    get_jwt_token()
    headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
    }
    if len(item_to_find) != 0:
        SEARCH_PROMO_URL = f"{BASE_API_URL}/v1/promotion?searchPromotion={item_to_find}&pageNumber=1&pageSize=5000&sortField=createdAt&sortOrder=DESC"
    else:
        SEARCH_PROMO_URL = f"{BASE_API_URL}/v1/promotion?pageNumber=1&pageSize=5000&sortField=createdAt&sortOrder=DESC"
    print(SEARCH_PROMO_URL)
    exising_promotions_resp = requests.get(SEARCH_PROMO_URL, headers=headers)
    existing_promotions = exising_promotions_resp.json().get("promotions")
    existing_documents = []
    for promotion in existing_promotions:
        existing_documents.append({"id": promotion["id"], "code": promotion["code"]})
    return existing_documents

def get_jwt_token():
    global jwt_token
    if jwt_token == "":
        payload = {
            "grant_type": "client_credentials",
            "client_id": "rentallocrtsvc",
            "client_secret": CLIENT_SECRET
        }

        response = requests.post(TOKEN_ENDPOINT, data=payload)
        jwt_token = response.json()["access_token"]
        print(f"JWT Token: {jwt_token}")

def delete_item(itemId):
    global jwt_token
    get_jwt_token()
    headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
    }
    delete_resp = ""
    DELETE_URL = f"{BASE_API_URL}/v1/promotion/internal/delete/{itemId}"
    delete_resp = requests.delete(DELETE_URL, headers=headers).json()
    print(f"Delete response {delete_resp}")


item_to_find = "existing"

# Call the function to delete records
#existing_documents = query_records_db(item_to_find)
existing_documents = query_records_api(item_to_find)
deleteCounter = 0
for document in existing_documents:
    try:
        deleteCounter += 1
        print(f"Deleting document {document['id']}, {document['code']}")
        delete_item(document["id"])
    except Exception as e:
        print(f"Error deleting document: {e}")

print(f"Done!! Deleted {deleteCounter} items.")
