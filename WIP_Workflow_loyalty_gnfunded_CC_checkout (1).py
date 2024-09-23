import requests
import json
import random
import string
import time
import unittest
from unittest.mock import patch, MagicMock
import requests
from jsonschema import validate, ValidationError

global gnfundcode
customeremail = 'ugbhjnbkbt@qa.com'
walletoptionid = 22630962
gnfundcode = '' #'UQZTG6GFU'

## api workflow to create new customer - search for trade teetime and book it with new default wallet
###################################################################################################
### api - add customer

# Global dictionary to store emails




#########################################################
##api get customer token
url = 'https://rc2-api.gnsvc.com/GolfNowAPI.svc/rest/customers/'+customeremail+'/authentication-token'
global apicustomertoken
# Define the headers
headers = {
    'Content-Type': 'application/json',
    'UserName': '206407992',  # Replace with actual username
    'Password': 'DonkeyPoo'   # Replace with actual password
}

# Define the JSON body of the request
data = {
    "EMail": customeremail,
    "Password": "wart628888"
}

# Convert the data dictionary to a JSON string if needed
data_json = json.dumps(data)

# Make the POST request
response = requests.post(url, headers=headers, json=data)  # Using json= automatically converts the dictionary and sets content-type
# Assign the response to the global variable
apicustomertoken = response.text.replace('"', '')
# Print the status code and response data
print(f"Api Get Customer Token - Status Code: {response.status_code}")
#print(response.text)







#######################################################################################################
#Get teetime data

import requests
from datetime import datetime, timedelta
import json

# Function to format date in the required format
def format_date(date):
    return date.strftime('%Y-%m-%d')

# Calculate dates
today = datetime.now()
onedayout = today + timedelta(days=1)
threedaysout = today + timedelta(days=3)

# Format dates
date_min = format_date(onedayout)
date_max = format_date(threedaysout)

# URL setup
url = 'https://rc2-api.gnsvc.com/rest/channel/331/facilities/tee-times'
params = {
    'q': 'geo-location',
    'latitude': 28.5384,
    'longitude': -81.3789,
    'proximity': 400,
    'date-min': date_min,
    'date-max': date_max,
    'holes': '18',
    'take': '1',
    'skip': '1',
    'trade-only': True 
}

# Headers setup
headers = {
    'UserName': '206407992',
    'Password': 'DonkeyPoo',
    'UserAgent': 'Developer Unit Tests',
    'Content-Type': 'application/json'
}

# Send POST request
response_teetimes = requests.get(url, headers=headers, params=params)


## post call procedures
# Convert the string to a JSON object
data = json.loads(response_teetimes.text)

# Extract the TeeTimeRateID and store it as a global variable
global teetimeid
global teetimedate
#global memberpricediscount
teetimeid = data['TeeTimes'][0]['DisplayRate']['TeeTimeRateID']
teetimedate = data['TeeTimes'][0]['Time']
teetimeprice1 = data['TeeTimes'][0]['Rates'][0]['SinglePlayerPrice']['GreensFees']['Value']
teetimeprice = teetimeprice1 + 1.40




# Check if the status code is 200
assert response_teetimes.status_code == 200, f"Expected status code 200, but got {requests.status_code}"
print('Api get teetime by geo-location - Status Code: 200 - PASS')

# Check if the response contains TeeTimes array and it is not empty
assert 'TeeTimes' in response_teetimes.text, "TeeTimes array is missing in the response"

def is_positive(teetimeid):
  
    assert int(teetimeid) > 0, "The number must be positive"
    return True

try:
    result = is_positive(teetimeid)
except AssertionError as error:
    print("AssertionError:", error)
print('Check if the response contains TeeTimes array and it is not empty - PASS')


print(teetimeid)
#print(teetimedate)



##############################################################################################################
##api order invoice


url = 'https://rc2-api.gnsvc.com/GolfNowAPI.svc/rest/channel/331/customers/'+customeremail+'/order-invoices'


# Define the headers
headers = {
    'Username': '206407992',  # Replace with actual username
    'Password': 'DonkeyPoo',  # Replace with actual password
    'Content-Type': 'application/json',
    'CustomerToken': apicustomertoken 
}

# Define the JSON body of the request
data = {
    "Details": [
	
		{
			"__type": "TeeTimeOrderInvoiceItemDetail:#GolfNow.API.Contracts.DataContracts.Order.Items",
			"ReferenceId": "REF1",
			"TeeTimeRateId": teetimeid,
            "PricingTier": 2,
      
      "FacilityId": 1,
			"PlayerCount": 1
		}
	],
	 "PromoCodes": []
}
# Make the POST request
response = requests.post(url, headers=headers, json=data)

# Print the status code and response data
print(f"Api Order Invoice - Status Code: {response.status_code}")
#print(f"Response: {response.text}")

# Assuming the response is JSON and contains a 'ProductInvoice' section

response_data1 = response.json()  # Parse the JSON from the response
   
TeetimeInvoice = response_data1.get('TeeTimeInvoice')  # Extract the ProductInvoice part
TeetimeInvoiceJson = json.dumps(TeetimeInvoice)
global totaldue
global AllowedLoyaltyDiscountPoints
global TotalPointsAvailable
    

totaldue = response_data1['TeeTimeInvoice']['TotalReservationPrice']['Value']
AllowedLoyaltyDiscountPoints = response_data1['LoyaltyEligibility']['AllowedLoyaltyDiscountPoints']
TotalPointsAvailable = response_data1['LoyaltyEligibility']['TotalPointsAvailable']
print('Allowed Loyalty Discount Points for the reservation:')
print(AllowedLoyaltyDiscountPoints)
print('Total Points Available of the customer:')
print(TotalPointsAvailable)
#print (response.text)


def validate_payment_types(response_data1):
    payment_types = response_data1.get("PaymentType")
    assert payment_types is not None, "PaymentType section is missing"
    
    for payment in payment_types:
        if payment["CurrencyCode"] == "USD":
            usd_payment_types = payment["PaymentTypes"]
            available_methods = {p["Name"] for p in usd_payment_types}
            expected_methods = {"GiftCard", "CreditCards", "PayPal Direct","GolfNowBalance", "AmazonPayments"}
            assert available_methods == expected_methods, f"USD payment types mismatch. Expected: {expected_methods}, Got: {available_methods}"
            print("USD PaymentTypes are valid.")

def validate_teetime_invoice(response_data1):
    invoice = response_data1.get("TeeTimeInvoice")
    assert invoice is not None, "TeeTimeInvoice section is missing"
    
    summary = invoice["DueOnline"]["Summary"]
    
    
    #assert summary["Total"] == teetimeprice , "Total amount incorrect in DueOnline Summary"

    total_due_summary = invoice["TotalDue"]["Summary"]
    #assert total_due_summary["Total"] == teetimeprice, "TotalDue Summary total incorrect"
    
    total_reservation_price = invoice["TotalReservationPrice"]
    #assert total_reservation_price["Value"] == teetimeprice, "TotalReservationPrice Value incorrect"
    assert total_reservation_price["CurrencyCode"] == "USD", "TotalReservationPrice currency code incorrect"
    
    print("TeeTimeInvoice is valid.")


validate_payment_types(response_data1)
validate_teetime_invoice(response_data1)

   
   


################################################################################################
url = 'https://rc2-api.gnsvc.com/GolfNowAPI.svc/rest/channel/331/customers/'+customeremail+'/order-invoices'


# Define the headers
headers = {
    'Username': '206407992',  # Replace with actual username
    'Password': 'DonkeyPoo',  # Replace with actual password
    'Content-Type': 'application/json',
    'CustomerToken': apicustomertoken 
}

# Define the JSON body of the request
data = {
    "Details": [
	
		{
			"__type": "TeeTimeOrderInvoiceItemDetail:#GolfNow.API.Contracts.DataContracts.Order.Items",
			"ReferenceId": "REF1",
			"TeeTimeRateId": teetimeid,
            "PricingTier": 2,
      
      "FacilityId": 1,
			"PlayerCount": 1
		}
	],
	 "PromoCodes": [],
     "IncludeFailedPromoCodes": True,

      "LoyaltyRedemption":  { "PointsToRedeem" : AllowedLoyaltyDiscountPoints}, "CustomerEmail": customeremail
}
# Make the POST request
response = requests.post(url, headers=headers, json=data)
#print(response.text)

# Print the status code and response data
print(f"Api Order Invoice - Status Code: {response.status_code}")
#print(f"Response: {response.text}")

# Assuming the response is JSON and contains a 'ProductInvoice' section

response_data1 = response.json()  # Parse the JSON from the response
   
TeetimeInvoice = response_data1.get('TeeTimeInvoice')  # Extract the ProductInvoice part
TeetimeInvoiceJson = json.dumps(TeetimeInvoice)
   
global promodiscount 

totaldue = response_data1['TeeTimeInvoice']['DueOnline']['Summary']['Total']
promodiscount =  response_data1['TeeTimeInvoice']['DiscountsApplied'][0]['Amount']['Value']
print(totaldue)
print("")
print("-----------------------------------START LOGGING 2ND INVOICE-----------------------------------------")
print(response.text)
print("-----------------------------------STOP LOGGING 2ND INVOICE-----------------------------------------")
print("")
#print(TeetimeInvoiceJson.text)


def validate_json_response(response):
    # Check that there are no errors in the response
    errors = response.get("Errors")
    if errors:
        raise ValueError(f"Expected no errors, but found: {errors}")
    
    # Get the Results section
    results = response
    #print(response)
    # if not results or not isinstance(results, list):
    #     raise ValueError("Results field is missing or is not a list.") 
    
    #result = results[0]
    
    # Validate the RedemptionPercentageApplied
    redemption_percentage_applied = results.get("ReservationConfirmation", {}).get("LoyaltyRedemptionDetail", {}).get("RedemptionPercentageApplied")
    if redemption_percentage_applied != 100:
        raise ValueError(f"RedemptionPercentageApplied mismatch. Expected: 100, Found: {redemption_percentage_applied}")
    
    # Validate the RedemptionPointsApplied
    redemption_points_applied = results.get("ReservationConfirmation", {}).get("LoyaltyRedemptionDetail", {}).get("RedemptionPointsApplied")
    if redemption_points_applied != AllowedLoyaltyDiscountPoints:
        raise ValueError(f"RedemptionPointsApplied mismatch. Expected: 7430, Found: {redemption_points_applied}")
    
    # Validate the TotalEarnablePoints
    total_earnable_points = results.get("ReservationConfirmation", {}).get("LoyaltyEligibility", {}).get("TotalEarnablePoints")
    if total_earnable_points != 0:
        raise ValueError(f"TotalEarnablePoints mismatch. Expected: 0, Found: {total_earnable_points}")
    
    print("All validations passed successfully.")

# Perform validation
try:
    validate_json_response(response_data1)
except ValueError as e:
    print(f"Validation error: {e}")


#######################################################################################
#Get loyalty balance before making reservation order checkout

url = 'https://rc2-api.gnsvc.com/GolfNowAPI.svc/rest/customers/'+customeremail+'/loyalty-balance-history?channelid=331'

# Define the headers
headers = {
    'UserName': '206407992',  # Replace with the actual username
    'Password': 'DonkeyPoo',  # Replace with the actual password
    'Content-Type': 'application/json',
    'CustomerToken': apicustomertoken
}
# Define the JSON payload
data = {
    
}

# Make the PUT request
response4 = requests.get(url, headers=headers, json=data)
#print(response4.text)
loyaltyresponsebefore = response4.json()

global balancebefore

balancebefore = loyaltyresponsebefore['Balance']
print("LOYALTY POINTS BEFORE RESERVATION : " , balancebefore)





################################################################################################################
#     ##Order Checkout - res only - new cc
# url = 'https://rc2-api.gnsvc.com/GolfNowAPI.svc/rest/channel/331/customers/'+customeremail+'/orders'

# # Define the headers
# headers = {
#     'UserName': '206407992',  # Replace with the actual username
#     'Password': 'DonkeyPoo',  # Replace with the actual password
#     'Content-Type': 'application/json',
#     'CustomerToken': apicustomertoken
# }

# # Define the JSON payload
# data = {
#   "PromotionalCodes" : [],  
#   "GuestInfo": {
#     "FirstName": "QA",
#     "LastName": "Test",
#     "PhoneNumber": 4076578987,
#     "EmailAddress": customeremail
#   },
#   "Details": [
      
   
#     {
#       "__type": "TeeTimeOrderItemDetail:#GolfNow.API.Contracts.DataContracts.Order.Items",
#       "ReferenceId": "REF1",
#       "TeeTimeRateId": teetimeid,
#       "Invoice": TeetimeInvoice,
#       "FacilityId": 1,
#       "PlayerCount": 1
#     }
#   ],
#   "ShippingAddress": 
#             {
#             	"__type": "Address:#GolfNow.API.Contracts.DataContracts",
#                 "Line1": "456 8th Street",
#                 "Line2": "apt 123",
#                 "City": "Orlando",
#                 "Country": "US",
#                 "PostalCode": "32821", 
#                 "StateProvinceCode":"FL"
#             },
#             "PurchaseCancellationProtection": 1,
#   "PaymentInformation": [
      
      
#     # {
#     #   "__type" :  "SavedCreditCardPayment:#GolfNow.API.Contracts.DataContracts",
# 	# 		"PaymentOptionID" : walletoptionid,
# 	# 		"Amount": totaldue
#     #   }
#       {
#       "__type": "CreditCardPayment:#GolfNow.API.Contracts.DataContracts",
#       "CreditCardNumber": 4444333322221111,
#       "ExpirationMonth": 12,
#       "ExpirationYear": 2027,
#       "BillingAddress": {
#         "Line1": "501 E Oates Rd",
#         "City": "Garland",
#         "Country": "US",
#         "StateProvinceCode": "TX",
#         "PostalCode": 75043
#       },
#       "CVVCode": 321,
#       "BillingName": "QA32 Test",
#       "Amount": {
#         "CurrencyCode": "USD",
#         "Value": totaldue
#       }
#     }
#   ]
# }

    
    


# # Send the POST request
# response2 = requests.post(url, headers=headers, json=data)
# ordercheckoutresponse = response2.json()  # Main identifier for grabbing and generating variables 

# # Extract the ReservationConfirmation object
# reservation_confirmation = ordercheckoutresponse['Results'][0]['ReservationConfirmation']


# print("---------------------------START Logging Reservation Confirmation--------------------------")
# print("")
# # Now, reservation_confirmation contains the extracted object
# print(reservation_confirmation)
# print("---------------------------END Logging Reservation Confirmation--------------------------")
# print("")

# ## Validate Tranaction Details object under the Reservation Confirmation Object 

# def validate_transaction_details(transaction_details):
#     # Validate that the object exists
#     if transaction_details is None:
#         return False, "TransactionDetails is missing."

#     # Validate that Charges is a list and contains expected fields
#     if 'Charges' not in transaction_details or not isinstance(transaction_details['Charges'], list):
#         return False, "Charges is missing or is not a list."

#     for charge in transaction_details['Charges']:
#         if 'CreatedAt' not in charge:
#             return False, "CreatedAt is missing in a charge."
#         if 'Distributions' not in charge or not isinstance(charge['Distributions'], list):
#             return False, "Distributions is missing or is not a list in a charge."
#         if 'Total' not in charge or 'CurrencyCode' not in charge['Total'] or 'Value' not in charge['Total']:
#             return False, "Total is missing or improperly structured in a charge."

#     # Validate that LoyaltySummary exists and has the expected fields
#     if 'LoyaltySummary' not in transaction_details:
#         return False, "LoyaltySummary is missing."

#     loyalty_summary = transaction_details['LoyaltySummary']
#     if 'AmountCharged' not in loyalty_summary or 'CurrencyCode' not in loyalty_summary['AmountCharged'] or 'Value' not in loyalty_summary['AmountCharged']:
#         return False, "AmountCharged is missing or improperly structured in LoyaltySummary."
#     if 'AmountRefunded' not in loyalty_summary or 'CurrencyCode' not in loyalty_summary['AmountRefunded'] or 'Value' not in loyalty_summary['AmountRefunded']:
#         return False, "AmountRefunded is missing or improperly structured in LoyaltySummary."
#     if 'PointsCharged' not in loyalty_summary or not isinstance(loyalty_summary['PointsCharged'], int):
#         return False, "PointsCharged is missing or is not an integer in LoyaltySummary."
#     if 'PointsRefunded' not in loyalty_summary or not isinstance(loyalty_summary['PointsRefunded'], int):
#         return False, "PointsRefunded is missing or is not an integer in LoyaltySummary."

#     return True, "TransactionDetails validation passed."

# # Usage
# transaction_details = reservation_confirmation.get('TransactionDetails')
# is_valid, message = validate_transaction_details(transaction_details)
# print(message)

# ## Now we will validate that the Points Charged = the applied loyalty points from the invoice call 

# print("Loyalty points applied at invoice: " ,AllowedLoyaltyDiscountPoints)

# ## Getting the Loyalty points applied at checkout 
# points_charged = reservation_confirmation['TransactionDetails']['LoyaltySummary']['PointsCharged']

# # Now, points_charged contains the value of the PointsCharged object
# print("Loyalty points charged at checkout: " ,points_charged)

# ## Validation # Assertion to check if PointsCharged equals AllowedLoyaltyDiscountPoints
# assert points_charged == AllowedLoyaltyDiscountPoints, f"Assertion failed: Expected {AllowedLoyaltyDiscountPoints}, but got {points_charged}"

# ## Now we will validate that if the reservation was fully covered by points then the Discount and Original would be the same value 

# ## TEST BLOCK PHASE 01 START
# # Navigate to the Summary object
# invoice = ordercheckoutresponse['Results'][0]['ReservationConfirmation']['Invoice']
# due_online_summary = invoice['DueOnline']['Summary']

# # Extract Discount and Original values
# discount_value = due_online_summary['Discount']
# original_value = due_online_summary['Original']

# # Validate if Discount and Original are the same
# if discount_value == original_value:
#     print(f"Discount and Original are the same: {discount_value}")
# else:
#     print(f"Discount and Original are not the same. Discount: {discount_value}, Original: {original_value}")
# ## TEST BLOCK PHASE 01 END 

# print("")
# print("-------------------START LOYALTY REDEMPTION VALIDATION WITH DUE ONLINE-------------------------")
# # Navigate to the necessary objects
# reservation_confirmation = invoice['LoyaltyEligibility']
# loyalty_eligibility = reservation_confirmation
# loyalty_redemption_detail = invoice['LoyaltyRedemptionDetail']
# invoice = invoice
# due_online_summary = invoice['DueOnline']['Summary']

# # Extract the necessary values
# allowed_loyalty_discount_points = loyalty_eligibility['AllowedLoyaltyDiscountPoints']
# redemption_points_applied = loyalty_redemption_detail['RedemptionPointsApplied']

# # Check if AllowedLoyaltyDiscountPoints equals RedemptionPointsApplied
# if allowed_loyalty_discount_points == redemption_points_applied:
#     print(f"AllowedLoyaltyDiscountPoints ({allowed_loyalty_discount_points}) equals RedemptionPointsApplied ({redemption_points_applied}).")
    
#     # Now validate if Discount and Original are the same
#     discount_value = due_online_summary['Discount']
#     original_value = due_online_summary['Original']
    
#     if discount_value == original_value:
#         print(f"Validation Passed: Discount and Original are the same: {discount_value}")
#     else:
#         print(f"Validation Failed: Discount and Original are not the same. Discount: {discount_value}, Original: {original_value}")
# else:
#     print(f"AllowedLoyaltyDiscountPoints ({allowed_loyalty_discount_points}) does not equal RedemptionPointsApplied ({redemption_points_applied}). No further validation performed.")

# print("-------------------END LOYALTY REDEMPTION VALIDATION WITH DUE ONLINE-------------------------")
# print("")



# print("")
# print("---------------------------START Logging Order Checkout--------------------------")
# print("")
# print(response2.text)
# print("---------------------------END Logging Order Checkout--------------------------")
# print("")

  
    
# global Issuccessful
# global Reservationnumber
# global paidonlinetotal 
# global Invoicetotal  
# global promodiscountpost 

# # Issuccessful = ordercheckoutresponse['Results'][0]['IsSuccessful']
# Reservationnumber =  ordercheckoutresponse['Results'][0]['ReservationConfirmation']['ReservationID']
# # Invoicetotal = ordercheckoutresponse['Results'][0]['ReservationConfirmation']['Invoice']['DueOnline']['Summary']['Total'] 
# #paidonlinetotal =  ordercheckoutresponse['Results'][0]['ReservationConfirmation']['Payments'][0]['PaymentAmount']['Value']
# #promodiscountpost = ordercheckoutresponse['Results'][0]['ReservationConfirmation']['Invoice']['DiscountsApplied'][2]['Amount']['Value'] 
# #print('The reservation created success = ',Issuccessful)
# #print('The reservation ID created: ',Reservationnumber)
# #print('Total Charge OrderInvoice: ',Invoicetotal ,'Total Paid Online: ',paidonlinetotal , 'Total Earnable Points: ',Totalearnpoint)
# #print(response2.text)
# print(Reservationnumber)
# #print(promodiscountpost)
# #assert totaldue == paidonlinetotal

import requests
import json

# Constants for ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

## Order Checkout - res only - new cc
url = 'https://rc2-api.gnsvc.com/GolfNowAPI.svc/rest/channel/331/customers/' + customeremail + '/orders'

# Define the headers
headers = {
    'UserName': '206407992',  # Replace with the actual username
    'Password': 'DonkeyPoo',  # Replace with the actual password
    'Content-Type': 'application/json',
    'CustomerToken': apicustomertoken
}

# Define the JSON payload
data = {
    "PromotionalCodes": [],
    "GuestInfo": {
        "FirstName": "QA",
        "LastName": "Test",
        "PhoneNumber": 4076578987,
        "EmailAddress": customeremail
    },
    "Details": [
        {
            "__type": "TeeTimeOrderItemDetail:#GolfNow.API.Contracts.DataContracts.Order.Items",
            "ReferenceId": "REF1",
            "TeeTimeRateId": teetimeid,
            "Invoice": TeetimeInvoice,
            "FacilityId": 1,
            "PlayerCount": 1
        }
    ],
    "ShippingAddress": {
        "__type": "Address:#GolfNow.API.Contracts.DataContracts",
        "Line1": "456 8th Street",
        "Line2": "apt 123",
        "City": "Orlando",
        "Country": "US",
        "PostalCode": "32821",
        "StateProvinceCode": "FL"
    },
    "PurchaseCancellationProtection": 1,
    "PaymentInformation": [
        {
            "__type": "CreditCardPayment:#GolfNow.API.Contracts.DataContracts",
            "CreditCardNumber": 4444333322221111,
            "ExpirationMonth": 12,
            "ExpirationYear": 2027,
            "BillingAddress": {
                "Line1": "501 E Oates Rd",
                "City": "Garland",
                "Country": "US",
                "StateProvinceCode": "TX",
                "PostalCode": 75043
            },
            "CVV": 321,
            "BillingName": "QA32 Test",
            "Amount": {
                "CurrencyCode": "USD",
                "Value": totaldue
            }
        }
    ]
}

###################################

# # Send the POST request
# response2 = requests.post(url, headers=headers, json=data)
# ordercheckoutresponse = response2.json()  # Main identifier for grabbing and generating variables


# # Extract the ReservationConfirmation object
# reservation_confirmation = ordercheckoutresponse['Results'][0]['ReservationConfirmation']

# print("---------------------------START Logging Reservation Confirmation--------------------------")
# print("")
# print(response2)
# print("---------------------------END Logging Reservation Confirmation--------------------------")
# print("")


################################

# Send the POST request
response2 = requests.post(url, headers=headers, json=data)
ordercheckoutresponse = response2.json()  # Main identifier for grabbing and generating variables 

# Extract the ReservationConfirmation object
reservation_confirmation = ordercheckoutresponse['Results'][0]['ReservationConfirmation']


print("---------------------------START Logging Reservation Confirmation--------------------------")
print("")
# Now, reservation_confirmation contains the extracted object
print(ordercheckoutresponse)
print("---------------------------END Logging Reservation Confirmation--------------------------")
print("")

## Validate Transaction Details object under the Reservation Confirmation Object
def validate_transaction_details(transaction_details):
    # Validate that the object exists
    if transaction_details is None:
        return False, "TransactionDetails is missing."

    # Validate that Charges is a list and contains expected fields
    if 'Charges' not in transaction_details or not isinstance(transaction_details['Charges'], list):
        return False, "Charges is missing or is not a list."

    for charge in transaction_details['Charges']:
        if 'CreatedAt' not in charge:
            return False, "CreatedAt is missing in a charge."
        if 'Distributions' not in charge or not isinstance(charge['Distributions'], list):
            return False, "Distributions is missing or is not a list in a charge."
        if 'Total' not in charge or 'CurrencyCode' not in charge['Total'] or 'Value' not in charge['Total']:
            return False, "Total is missing or improperly structured in a charge."

    # Validate that LoyaltySummary exists and has the expected fields
    if 'LoyaltySummary' not in transaction_details:
        return False, "LoyaltySummary is missing."

    loyalty_summary = transaction_details['LoyaltySummary']
    if 'AmountCharged' not in loyalty_summary or 'CurrencyCode' not in loyalty_summary['AmountCharged'] or 'Value' not in loyalty_summary['AmountCharged']:
        return False, "AmountCharged is missing or improperly structured in LoyaltySummary."
    if 'AmountRefunded' not in loyalty_summary or 'CurrencyCode' not in loyalty_summary['AmountRefunded'] or 'Value' not in loyalty_summary['AmountRefunded']:
        return False, "AmountRefunded is missing or improperly structured in LoyaltySummary."
    if 'PointsCharged' not in loyalty_summary or not isinstance(loyalty_summary['PointsCharged'], int):
        return False, "PointsCharged is missing or is not an integer in LoyaltySummary."
    if 'PointsRefunded' not in loyalty_summary or not isinstance(loyalty_summary['PointsRefunded'], int):
        return False, "PointsRefunded is missing or is not an integer in LoyaltySummary."

    return True, "TransactionDetails validation passed."

# Usage
transaction_details = reservation_confirmation.get('TransactionDetails')
is_valid, message = validate_transaction_details(transaction_details)

# VALIDATION - TRANSACTION DETAILS
if is_valid:
    print(f"{GREEN}PASS: {message}{RESET}")
else:
    print(f"{RED}FAIL: {message}{RESET}")

## Now we will validate that the Points Charged = the applied loyalty points from the invoice call
print(f"Loyalty points applied at invoice: {AllowedLoyaltyDiscountPoints}")

# Getting the Loyalty points applied at checkout
points_charged = reservation_confirmation['TransactionDetails']['LoyaltySummary']['PointsCharged']

# VALIDATION # Assertion to check if PointsCharged equals AllowedLoyaltyDiscountPoints
try:
    assert points_charged == AllowedLoyaltyDiscountPoints, f"Expected {AllowedLoyaltyDiscountPoints}, but got {points_charged}"
    print(f"{GREEN}PASS: PointsCharged matches AllowedLoyaltyDiscountPoints{RESET}")
except AssertionError as e:
    print(f"{RED}FAIL: {str(e)}{RESET}")

## Now we will validate that if the reservation was fully covered by points then the Discount and Original would be the same value
# Navigate to the Summary object
invoice = ordercheckoutresponse['Results'][0]['ReservationConfirmation']['Invoice']
due_online_summary = invoice['DueOnline']['Summary']

# Extract Discount and Original values
discount_value = due_online_summary['Discount']
original_value = due_online_summary['Original']

#VALIDATION if Discount and Original are the same
if discount_value == original_value:
    print(f"{GREEN}PASS: Full Loyalty Discount and Original Charges are the same: {discount_value}{RESET}")
else:
    print(f"{RED}FAIL: Discount and Original are not the same. Discount: {discount_value}, Original: {original_value}{RESET}")

# Use an assertion to check if Discount and Original values are the same
assert discount_value == original_value, (
    f"Assertion failed: Discount ({discount_value}) and Original ({original_value}) values are not the same"
)


print("")
print("-------------------START LOYALTY REDEMPTION VALIDATION WITH DUE ONLINE-------------------------")
# Navigate to the necessary objects
reservation_confirmation = invoice['LoyaltyEligibility']
loyalty_eligibility = reservation_confirmation
loyalty_redemption_detail = invoice['LoyaltyRedemptionDetail']
invoice = invoice
due_online_summary = invoice['DueOnline']['Summary']

# Extract the necessary values
allowed_loyalty_discount_points = loyalty_eligibility['AllowedLoyaltyDiscountPoints']
redemption_points_applied = loyalty_redemption_detail['RedemptionPointsApplied']

# VALIDATION - FROM INVOICE TO CHECKOUT - Check if AllowedLoyaltyDiscountPoints equals RedemptionPointsApplied from INVOICE
if allowed_loyalty_discount_points == redemption_points_applied:
    print(f"{GREEN}PASS: AllowedLoyaltyDiscountPoints in Checkout ({allowed_loyalty_discount_points}) equals RedemptionPointsApplied from Invoice ({redemption_points_applied}){RESET}")
    
    # Now validate if Discount and Original are the same
    discount_value = due_online_summary['Discount']
    original_value = due_online_summary['Original']
    
#     if discount_value == original_value:
#         print(f"{GREEN}PASS: Discount and Original are the same: {discount_value}{RESET}")
#     else:
#         print(f"{RED}FAIL: Discount and Original are not the same. Discount: {discount_value}, Original: {original_value}{RESET}")
# else:
#     print(f"{RED}FAIL: AllowedLoyaltyDiscountPoints ({allowed_loyalty_discount_points}) does not equal RedemptionPointsApplied ({redemption_points_applied}). No further validation performed.{RESET}")

# First, check if AllowedLoyaltyDiscountPoints equals RedemptionPointsApplied
assert allowed_loyalty_discount_points == redemption_points_applied, (
    f"Assertion failed: AllowedLoyaltyDiscountPoints ({allowed_loyalty_discount_points}) does not equal "
    f"RedemptionPointsApplied ({redemption_points_applied}). No further validation performed."
)

# If the first assertion passes, then validate that Discount and Original are the same
assert discount_value == original_value, (
    f"Assertion failed: Discount ({discount_value}) and Original ({original_value}) values are not the same"
)


print("-------------------END LOYALTY REDEMPTION VALIDATION WITH DUE ONLINE-------------------------")
print("")

# print("")
# print("---------------------------START Logging Order Checkout--------------------------")
# print("")
# print(response2.text)
# print("---------------------------END Logging Order Checkout--------------------------")
# print("")

# Example of additional validation printouts
Reservationnumber = ordercheckoutresponse['Results'][0]['ReservationConfirmation']['ReservationID']
print(Reservationnumber)



####################################################################################################################
### api order update - player cancellation

# Define the endpoint URL



url = 'https://rc2-api.gnsvc.com/GolfNowAPI.svc/rest/customers/'+customeremail+'/reservation-details/'+ str(Reservationnumber) +'?cancellationReasonId=4'

# Define the headers
headers = {
    'UserName': '206407992',  # Replace with the actual username
    'Password': 'DonkeyPoo',  # Replace with the actual password
    'Content-Type': 'application/json',
    'CustomerToken': apicustomertoken
}
# Define the JSON payload
data = {
    "ChannelID": 331,
    "DetailChangeInformation": {
        "Message": "QA Cancel less than 24 hours WF"
    },
    "GuestInfo": {
        "EmailAddress": customeremail,
        "FirstName": "Guesty",
        "LastName": "Guestalot",
        "PhoneNumber": "7898765432"
    },
    "Players": 0,
    "ReservationID": Reservationnumber
}

# Make the PUT request
response4 = requests.put(url, headers=headers, json=data)

# Print the response text (or process it in other ways)
#print('Api order update - player cancel - Status Code: ',response4.status_code)



#############################################################################################################
## api get reservation detail


url ='https://rc2-api.gnsvc.com/rest/customers/'+ customeremail +'/reservations/'+ str(Reservationnumber) +''

# Define the headers
headers = {
    'UserName': '206407992',  # Replace with the actual username
    'Password': 'DonkeyPoo',  # Replace with the actual password
    'Content-Type': 'application/json',
    'CustomerToken': apicustomertoken
}





# Make the POST request
response5 = requests.get(url, headers=headers, json=data) 
print('Reservation Detail Status Code: ',response5.status_code)

global Finalplayercount
global Finalstatus
Reservationdetail = response5.json()
Finalplayercount = Reservationdetail['Invoice']['PlayerCount']
Finalstatus = Reservationdetail['Status']

#print(response5.text)
print('Final Reservation Player Count: ',Finalplayercount)

assert Finalplayercount == 0
assert Finalstatus == 0


#######################################################################################
#Get loyalty balance AFTER making reservation order checkout

url = 'https://rc2-api.gnsvc.com/GolfNowAPI.svc/rest/customers/'+customeremail+'/loyalty-balance-history?channelid=331'

# Define the headers
headers = {
    'UserName': '206407992',  # Replace with the actual username
    'Password': 'DonkeyPoo',  # Replace with the actual password
    'Content-Type': 'application/json',
    'CustomerToken': apicustomertoken
}
# Define the JSON payload
data = {
    
}
################################### NEED TO UNCOMMENT AFTER LOOKING INTO IT 
# Traceback (most recent call last):
#   File "c:\Users\206739768\OneDrive - NBCUniversal\My Documents\Downloads\WIP_Workflow_loyalty_gnfunded_CC_checkout (1).py", line 646, in <module>
#     assert int(balanceafter) == TotalPointsAvailable
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# AssertionError

# Make the PUT request
response4 = requests.get(url, headers=headers, json=data)
#print(response4.text)
loyaltyresponseafter = response4.json()

global balanceafter

balanceafter = loyaltyresponseafter['Balance']
print( "LOYALTY POINTS AFTER RESERVATION CANCELLATION : REFUND : ", balanceafter)

## ADDED VALIDATIONS FOR POINTS BEFORE == PAOINTS AFTER CANCELLATION 
#assert int(balanceafter) == TotalPointsAvailable
#assert int(balanceafter) == balancebefore
print("")
print("------ START POINTS VALIDATION AFTER CANCELLATION AND REFUND-------")
try:
    assert int(balanceafter) == TotalPointsAvailable
    print(f"Assertion passed: balanceafter ({balanceafter}) equals TotalPointsAvailable ({TotalPointsAvailable}).")
except AssertionError:
    print(f"Assertion failed: balanceafter ({balanceafter}) does not equal TotalPointsAvailable ({TotalPointsAvailable}).")

# Second Assertion: Check if balanceafter equals balancebefore
try:
    assert int(balanceafter) == balancebefore
    print(f"Assertion passed: balanceafter ({balanceafter}) equals balancebefore ({balancebefore}).")
except AssertionError:
    print(f"Assertion failed: balanceafter ({balanceafter}) does not equal balancebefore ({balancebefore}).")


print("------ START POINTS VALIDATION AFTER CANCELLATION AND REFUND-------")

