import requests
import json
import random
import string
import time
import unittest
from unittest.mock import patch, MagicMock
import requests
from jsonschema import validate, ValidationError
import json
from typing import Any, Dict
import webbrowser


## api workflow to create new customer - search for trade teetime and book it with new default wallet
###################################################################################################
### api - add customer
facilityid  = 1499
# Global dictionary to store emails
emails = {}

def generate_random_email(key):
    """Generates a random email address and stores it in a global dictionary."""
    if key not in emails:  # Check if the email has already been generated for the given key
        domain = '@qa.com'
        letters = string.ascii_lowercase
        random_name = ''.join(random.choice(letters) for i in range(10))  # Generate a 10-letter random string
        emails[key] = random_name + domain  # Store the generated email in the global dictionary

    return emails[key]

# Usage
email1 = generate_random_email('user1')  # Generates an email for 'user1'
print("New Customer Email: "+email1)  # Prints the generated email

email2 = generate_random_email('user1')  # Does not generate a new email, retrieves the existing one


# Define the URL
url = 'https://rc2-api.gnsvc.com/GolfNowAPI.svc/rest/customers?channelid=331'

# Define the headers
headers = {
    'Content-Type': 'application/json',
    'UserName': '206407992',  # Replace with actual username
    'Password': 'DonkeyPoo'   # Replace with actual password
}

# Define the JSON body of the request
data = {
    "Password": "wart628888",
    "EMailAddress": email1,
    "FirstName": "Automation",
    "LastName": "Ordercheckout",
    "Address": {
        "City": "Orlando",
        "Country": "US",
        "Line1": "321 Main Street",
        "Line2": "204",
        "PostalCode": "48161",
        "StateProvinceCode": "MI"
    },
    "DateOfBirth": "09/01/1980",
    "PhoneNumber": "8796545312",
    "Gender": 0,
    "Handicap1": 11.5
}

# Convert the data dictionary to a JSON string
data_json = json.dumps(data)

# Make the PUT request
response = requests.put(url, headers=headers, data=data_json)

# Print the status code and response data
print(f"Api add customer - Status Code: {response.status_code}")



#########################################################
##api get customer token
url = 'https://rc2-api.gnsvc.com/GolfNowAPI.svc/rest/customers/' + email1 +'/authentication-token'
global apicustomertoken
# Define the headers
headers = {
    'Content-Type': 'application/json',
    'UserName': '206407992',  # Replace with actual username
    'Password': 'DonkeyPoo'   # Replace with actual password
}

# Define the JSON body of the request
data = {
    "EMail": email1,
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
onedayout = today + timedelta(days=0)
threedaysout = today + timedelta(days=3)

# Format dates
date_min = format_date(onedayout)
date_max = format_date(threedaysout)

# URL setup
url = 'https://rc2-api.gnsvc.com/rest/channel/331/facilities/' + str(facilityid) + '/tee-times?'
params = {
    
    'date-min': date_min,
    'date-max': date_max,
    'holes': '18',
    'take': '1000',
    'skip': '0',
    'trade-only': True,
    'players': 4
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
#print(response_teetimes.text)

## post call procedures
# Convert the string to a JSON object

data = json.loads(response_teetimes.text)

# Extract the TeeTimeRateID and store it as a global variable
global teetimeid
global teetimedate
#global memberpricediscount
teetimeid = data['TeeTimes'][0]['DisplayRate']['TeeTimeRateID']
teetimedate = data['TeeTimes'][0]['Time']
#memberpricediscount = data['TeeTimes'][0]['DisplayRate']['MemberPricing']['Discount']['Amount']['Value']

print('TeetimeId:',teetimeid)




# Check if the status code is 200
# assert response_teetimes.status_code == 200, f"Expected status code 200, but got {requests.status_code}"
# print('Api get teetime by geo-location - Status Code: 200 - PASS')

# # Check if the response contains TeeTimes array and it is not empty
# assert 'TeeTimes' in response_teetimes.text, "TeeTimes array is missing in the response"

# def is_positive(teetimeid):
  
#     assert int(teetimeid) > 0, "The number must be positive"
#     return True

# try:
#     result = is_positive(teetimeid)
# except AssertionError as error:
#     print("AssertionError:", error)
#print('Check if the response contains TeeTimes array and it is not empty - PASS')


#print(teetimeid)
#print(teetimedate)
#######################################################################################################
### api teetime invoice - validate member pricing 
#/GolfNowAPI.svc/rest/channel/331/facilities/0/tee-times/872414752/invoice?verify=False&extend=True&player-count=1&PricingTier=2

url = 'https://rc2-api.gnsvc.com//GolfNowAPI.svc/rest/channel/331/facilities/0/tee-times/'+str(teetimeid)+'/invoice?'
params = {
    'verify': False,
    'extend': True,
    'pricing-tier': 2,
    'show-virtual-trade-offer': True
}

# Headers setup
headers = {
    'UserName': '206407992',
    'Password': 'DonkeyPoo',
    'UserAgent': 'Developer Unit Tests',
    'Content-Type': 'application/json'
}

# Send POST request
Response2 = requests.get(url, headers=headers, params=params)
#print('teetime invoice')
#print('#1')
#print(Response2.text)
## post call procedures
# Convert the string to a JSON object
response_dict = json.loads(Response2.text)



# Validation functions
def validate_member_pricing(response_dict):
    try:
        # Validate 'MemberPricing' field
        assert 'MemberPricing' in response_dict, "'MemberPricing' is missing from the response"

        member_pricing = response_dict['MemberPricing']
        
        # Validate 'RateAdjustment'
        assert 'RateAdjustment' in member_pricing, "'RateAdjustment' is missing in 'MemberPricing'"
        rate_adjustment = member_pricing['RateAdjustment']
        
        assert 'CurrencyCode' in rate_adjustment, "'CurrencyCode' is missing in 'RateAdjustment'"
        assert rate_adjustment['CurrencyCode'] == "USD", "Expected 'CurrencyCode' to be 'USD'"
        
        assert 'Value' in rate_adjustment, "'Value' is missing in 'RateAdjustment'"
        #assert rate_adjustment['Value'] == 20, "Expected 'Value' to be 5"
        
        # Validate 'EligibleProductIds'
        assert 'EligibleProductIds' in member_pricing, "'EligibleProductIds' is missing in 'MemberPricing'"
        eligible_product_ids = member_pricing['EligibleProductIds']
        
        
        print("Teetime invoice validations passed!")
    except AssertionError as e:
        print(f"Validation error: {e}")

# Run validation
validate_member_pricing(response_dict)

def validate_pricing_by_number_of_players(response_dict):
    errors = []

    pricing_by_number_of_players = response_dict.get("PricingByNumberOfPlayers", [])
    
    # Ensure that PricingByNumberOfPlayers exists and has at least one entry
    if not pricing_by_number_of_players:
        errors.append("PricingByNumberOfPlayers is missing or empty")

    for i, player_pricing in enumerate(pricing_by_number_of_players):
        # Validate that NumberOfPlayers is a positive integer
        if not isinstance(player_pricing.get("NumberOfPlayers"), int) or player_pricing.get("NumberOfPlayers") <= 0:
            errors.append(f"NumberOfPlayers is not a valid positive integer at index {i}")
        
        # Validate DueAtCourse and DueOnline amounts and structure
        due_at_course = player_pricing.get("DueAtCourse", {})
        due_online = player_pricing.get("DueOnline", {})
        
        # Validate DueAtCourse and DueOnline totals
        for category, due in [("DueAtCourse", due_at_course), ("DueOnline", due_online)]:
            total = due.get("Summary", {}).get("Total", None)
            if total is None or total < 0:
                errors.append(f"{category} Total is missing or invalid at index {i}")

            # Validate that Items exist and are structured correctly
            items = due.get("Items", [])
            if not items:
                errors.append(f"{category} Items are missing at index {i}")
            for item in items:
                if "Original" not in item or "Total" not in item:
                    errors.append(f"{category} Items missing Original or Total at index {i}")

        # Validate LoyaltyEligibility
        loyalty_eligibility = player_pricing.get("LoyaltyEligibility", {})
        if not isinstance(loyalty_eligibility.get("TotalEarnablePoints"), (int, float)):
            errors.append(f"Invalid TotalEarnablePoints in LoyaltyEligibility at index {i}")
        
        # Validate MemberPricing structure
        member_pricing = player_pricing.get("MemberPricing", {})
        rate_adjustment = member_pricing.get("RateAdjustment", {})
        if rate_adjustment.get("CurrencyCode") != "USD":
            errors.append(f"RateAdjustment CurrencyCode is not 'USD' at index {i}")
        if rate_adjustment.get("Value") is None or rate_adjustment.get("Value") < 0:
            errors.append(f"Invalid RateAdjustment value at index {i}")
        
        

    # Print validation results
    if errors:
        print(f"Validation failed with {len(errors)} errors:")
        for error in errors:
            print(f"- {error}")
    else:
        print("Validation passed with no errors")

# Run validation
validate_pricing_by_number_of_players(response_dict)



def validate_eligible_product_ids(response_dict, expected_ids):
    errors = []

    # Retrieve the EligibleProductIds list
    eligible_product_ids = response_dict.get("MemberPricing", {}).get("EligibleProductIds", None)

    # Check if EligibleProductIds is present and is a list
    if eligible_product_ids is None:
        errors.append("EligibleProductIds is missing in the response.")
    elif not isinstance(eligible_product_ids, list):
        errors.append(f"EligibleProductIds is not a list: {eligible_product_ids}")
    else:
        # Validate the contents of EligibleProductIds against the expected values
        for expected_id in expected_ids:
            if expected_id not in eligible_product_ids:
                errors.append(f"Expected product ID {expected_id} is missing from EligibleProductIds.")
        
        # Optional: Check for any unexpected product IDs
        for product_id in eligible_product_ids:
            if product_id not in expected_ids:
                errors.append(f"Unexpected product ID {product_id} found in EligibleProductIds.")
    
    # Print validation results
    if errors:
        print(f"Validation failed with {len(errors)} errors:")
        for error in errors:
            print(f"- {error}")
    else:
        print("Validation passed with no errors.")

# Expected EligibleProductIds (based on example)
expected_product_ids = [3, 5, 36, 37, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 56, 57, 59, 61, 62, 63, 64, 69]

# Run validation
validate_eligible_product_ids(response_dict, expected_product_ids)

## add more validations for teetime invoice

###################################################################################################################
#######################################################################################################
#Get facility summary

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
url = 'https://rc2-api.gnsvc.com/rest/channel/331/facility-summaries?'
params = {
    'q': 'facilityids',
    'date-min': date_min,
    'date-max': date_max,
    'holes': '18',
    'take': '1',
    'skip': '5',
    'trade-only': False,
    'ids': '1499' 
}

# Headers setup
headers = {
    'UserName': '206407992',
    'Password': 'DonkeyPoo',
    'UserAgent': 'Developer Unit Tests',
    'Content-Type': 'application/json'
}

# Send POST request
Response2 = requests.get(url, headers=headers, params=params)

#print(Response2.text)
## post call procedures
# Convert the string to a JSON object
data = json.loads(Response2.text)

#global memberpricediscount
#teetimeid = data['TeeTimes'][0]['DisplayRate']['TeeTimeRateID']
#teetimedate = data['TeeTimes'][0]['Time']
#memberpricediscount = data['TeeTimes'][0]['DisplayRate']['MemberPricing']['Discount']['Amount']['Value']

#print(memberpricediscount)





assert "Items" in data, "Items key is missing in the response"
for item in data["Items"]:
        assert "HasMemberPricing" in item, "HasMemberPricing key is missing in the item"
        assert isinstance(item["HasMemberPricing"], bool), "HasMemberPricing should be a boolean"
        assert item["HasMemberPricing"] is True, "HasMemberPricing should be true"

#######################################################################################################
#Get facility 



# URL setup
url = 'https://rc2-api.gnsvc.com/rest/channel/331/facilities/'+ str(facilityid)


# Headers setup
headers = {
    'UserName': '206407992',
    'Password': 'DonkeyPoo',
    'UserAgent': 'Developer Unit Tests',
    'Content-Type': 'application/json'
}

# Send POST request
Response2 = requests.get(url, headers=headers, params=params)

#print(Response2.text)
## post call procedures
# Convert the string to a JSON object
data = json.loads(Response2.text)

#global memberpricediscount
#teetimeid = data['TeeTimes'][0]['DisplayRate']['TeeTimeRateID']
#teetimedate = data['TeeTimes'][0]['Time']
#memberpricediscount = data['TeeTimes'][0]['DisplayRate']['MemberPricing']['Discount']['Amount']['Value']

#print(memberpricediscount)



assert "HasMemberPricing" in data, "HasMemberPricing key is missing in the response"
assert isinstance(data["HasMemberPricing"], bool), "HasMemberPricing should be a boolean"
assert data["HasMemberPricing"] is True, "HasMemberPricing should be true"


######################################################################################################
### tr 
url = 'https://rc2-tr.gnsvc.com/GetToken'

# Define the headers
headers = {
    'Username': '206407992',  # Replace •••••• with your actual username
    'Password': 'DonkeyPoo'   # Replace •••••• with your actual password
}

# Send the POST request
response = requests.post(url, headers=headers)
responsejson = response.json()
global trtoken 
trtoken = responsejson['Token']
#print(trtoken)




##########################################################################################################
## TR product purchase


# Define the API endpoint
url = 'https://rc2-tr.gnsvc.com/Product/Purchase'

# Define the headers
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Username': '206407992',
    'Password': 'DonkeyPoo'
}

# Define the payload data
payload = {
    'Token': trtoken,
    'CustomerEmail': email1,
    'InventoryChannelID': '331',
    'ProductPriceID': '64',
    'Payment.Name': 'David staub',
    'Payment.PhoneNumber': '3052822541',
    'Payment.CC.CreditCardNumber': '4444333322221111',
    'Payment.CC.CVVCode': '111',
    'Payment.CC.ExpirationMonth': '08',
    'Payment.CC.ExpirationYear': '2027',
    'Payment.Address.Line1': '4532 cima alley',
    'Payment.Address.Line2': '',
    'Payment.Address.StateProvinceCode': 'FL',
    'Payment.Address.City': 'Orlando',
    'Payment.Address.Country': 'US',
    'Payment.Address.PostalCode': '32814',
    'Shipping.Address.Line1': '4532 cima alley',
    'Shipping.Address.Line2': '',
    'Shipping.Address.Country': 'US',
    'Shipping.Address.City': 'Orlando',
    'Shipping.Address.StateProvinceCode': 'FL',
    'Shipping.Address.PostalCode': '32814'
}

# Send the POST request
response = requests.post(url, headers=headers, data=payload)



##############################################################################################################
##api order invoice


url = 'https://rc2-api.gnsvc.com/GolfNowAPI.svc/rest/channel/331/customers/'+ email1 +'/order-invoices'


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
#print(response.text)
print(f"Api Order Invoice - Status Code: {response.status_code}")
response_data1 = response.json()  # Parse the JSON from the response
TeetimeInvoice = response_data1.get('TeeTimeInvoice')
totaldue = TeetimeInvoice['DueOnline']['Summary']['Total'] 
response = response.json()
rate_adjustment_value = response['TeeTimeInvoice']['MemberPricing']['RateAdjustment']['Value']
due_online_subtotal = response['TeeTimeInvoice']['DueOnline']['Summary']['SubTotal']

def validate_memberpricing(response):
    try:
        assert rate_adjustment_value > 0.0, f"Expected rate adjustment value to be greater than 0 , but got {rate_adjustment_value}"
        #assert rate_adjustment_value == 5.0, f"Expected rate adjustment value to be 5, but got {rate_adjustment_value}"

        #assert due_online_subtotal == 15, f"Expected due online subtotal to be 20, but got {due_online_subtotal}"
        assert due_online_subtotal > 0.0 , f"Expected due online subtotal to be greater than 0, but got {due_online_subtotal}"
          
        return True
    except AssertionError as e:
        print(f"Validation error: {e}")
        return False

# Print the status code and response data

def validate_response_orderinvoice(response: Dict[str, Any]) -> bool:
    try:
        # Validate ChannelLoyaltyEligibility
        assert 'ChannelLoyaltyEligibility' in response, "Missing key: ChannelLoyaltyEligibility"
        channel_loyalty_eligibility = response['ChannelLoyaltyEligibility']
        assert isinstance(channel_loyalty_eligibility, dict), "ChannelLoyaltyEligibility should be a dictionary"
        assert 'IsLoyaltyEligibleInChannel' in channel_loyalty_eligibility, "Missing key: ChannelLoyaltyEligibility.IsLoyaltyEligibleInChannel"
        assert 'ProgramId' in channel_loyalty_eligibility, "Missing key: ChannelLoyaltyEligibility.ProgramId"
        assert isinstance(channel_loyalty_eligibility['IsLoyaltyEligibleInChannel'], bool), "IsLoyaltyEligibleInChannel should be a boolean"
        assert isinstance(channel_loyalty_eligibility['ProgramId'], int), "ProgramId should be an integer"

        # Validate LoyaltyEligibility
        assert 'LoyaltyEligibility' in response, "Missing key: LoyaltyEligibility"
        loyalty_eligibility = response['LoyaltyEligibility']
        assert isinstance(loyalty_eligibility, dict), "LoyaltyEligibility should be a dictionary"
        required_keys = [
            'AllowedLoyaltyDiscountAmount', 'AllowedLoyaltyDiscountPoints',
            'BaseAllowedLoyaltyDiscountAmount', 'BaseAllowedLoyaltyDiscountPoints',
            'Presets', 'TotalBaseEarnablePoints', 'TotalEarnablePoints',
            'TotalPointsAvailable', 'TotalPointsToRedeem', 'TotalPromotionalEarnablePoints',
            'TransactionFeePreset'
        ]
        for key in required_keys:
            assert key in loyalty_eligibility, f"Missing key: LoyaltyEligibility.{key}"

        # Validate PaymentType
        assert 'PaymentType' in response, "Missing key: PaymentType"
        payment_type = response['PaymentType']
        assert isinstance(payment_type, list), "PaymentType should be a list"
        for payment in payment_type:
            assert isinstance(payment, dict), "Each PaymentType should be a dictionary"
            assert 'ChannelID' in payment, "Missing key: PaymentType.ChannelID"
            assert 'CurrencyCode' in payment, "Missing key: PaymentType.CurrencyCode"
            assert 'PaymentTypes' in payment, "Missing key: PaymentType.PaymentTypes"
            assert 'TextFormat' in payment, "Missing key: PaymentType.TextFormat"
            assert isinstance(payment['ChannelID'], int), "PaymentType.ChannelID should be an integer"
            assert isinstance(payment['CurrencyCode'], str), "PaymentType.CurrencyCode should be a string"
            assert isinstance(payment['PaymentTypes'], list), "PaymentType.PaymentTypes should be a list"
            assert isinstance(payment['TextFormat'], str), "PaymentType.TextFormat should be a string"
            for pt in payment['PaymentTypes']:
                assert isinstance(pt, dict), "Each PaymentType in PaymentTypes should be a dictionary"
                assert 'Name' in pt, "Missing key: PaymentTypes.Name"
                assert 'PaymentTypeDesignationId' in pt, "Missing key: PaymentTypes.PaymentTypeDesignationId"
                assert 'PaymentTypeId' in pt, "Missing key: PaymentTypes.PaymentTypeId"
                assert isinstance(pt['Name'], str), "PaymentTypes.Name should be a string"
                assert isinstance(pt['PaymentTypeDesignationId'], int), "PaymentTypes.PaymentTypeDesignationId should be an integer"
                assert isinstance(pt['PaymentTypeId'], int), "PaymentTypes.PaymentTypeId should be an integer"

        # Validate TeeTimeInvoice
        assert 'TeeTimeInvoice' in response, "Missing key: TeeTimeInvoice"
        tee_time_invoice = response['TeeTimeInvoice']
        assert isinstance(tee_time_invoice, dict), "TeeTimeInvoice should be a dictionary"
        required_keys = [
            '__type', 'FacilityID', 'PlayDateUtc', 'Time', 'CancellationProtectionCreditEligibility',
            'ChannelLoyaltyEligibility', 'CurrencyCode', 'DiscountsApplied', 'DueAtCourse', 'DueOnline',
            'EstimatedChargeDate', 'FacilityFlags', 'GroupSizeLimit', 'HasMembershipDiscount', 'HoleCount',
            'IsHotDeal', 'IsHotDealHidden', 'IsPaidProductSideCart', 'IsPayNow', 'IsPrepaid', 'IsRateRestricted',
            'IsReservationRestricted', 'IsScheduledPaymentEnabled', 'IsSplitReservationEnabled', 'LoyaltyEligibility',
            'LoyaltyRedemptionDetail', 'MemberPricing', 'PlayerCount', 'PlayerRule', 'PolicyItems',
            'PreDiscountPricing', 'Pricing', 'PricingByNumberOfPlayers', 'PricingTier', 'ProductAccessList',
            'ProductEarlyAccessCollection', 'ProductTypeIds', 'ProfileSummary', 'PromoCodeApplied', 'PromoCodeResults',
            'PromoCodeSuccessMessage', 'PurchaseCancellationProtection', 'RateName', 'RateSetTypeId', 'RateTagCodes',
            'ReservationGroup', 'RestrictedRateMessage', 'TeeTimeNotes', 'TeeTimeOffer', 'TeeTimeRateID', 'TermsAndConditions',
            'TotalDue', 'TotalReservationPrice', 'TransactionFeeWaived', 'Transportation', 'UniversalPromotions',
            'VirtualTradeOffer', 'WorryFreeEligibilityStatus', 'OverrideReferenceId'
        ]
        for key in required_keys:
            assert key in tee_time_invoice, f"Missing key: TeeTimeInvoice.{key}"

        return True
    except AssertionError as e:
        print(f"Validation error: {e}")
        return False
    
is_valid2 = validate_response_orderinvoice(response)
validate_memberpricing(response)
print(f"Member Pricing Order Invoice Validation result: Passed = {is_valid2}")



################################################################################################################
    ##Order Checkout - res only - new cc

url = 'https://rc2-api.gnsvc.com/GolfNowAPI.svc/rest/channel/331/customers/'+ email1 +'/orders'

# Define the headers
headers = {
    'UserName': '206407992',  # Replace with the actual username
    'Password': 'DonkeyPoo',  # Replace with the actual password
    'Content-Type': 'application/json',
    'CustomerToken': apicustomertoken
}

# Define the JSON payload
data = {
    
  "GuestInfo": {
    "FirstName": "QA",
    "LastName": "Test",
    "PhoneNumber": 4076578987,
    "EmailAddress": email1
  },
  "Details": [
      
   
    {
      "__type": "TeeTimeOrderItemDetail:#GolfNow.API.Contracts.DataContracts.Order.Items",
      "ReferenceId": "REF1",
      "TeeTimeRateId": teetimeid,
      "Invoice": TeetimeInvoice,
      "FacilityId": 1,
      "PlayerCount": 2
    }
  ],
  "ShippingAddress": 
            {
            	"__type": "Address:#GolfNow.API.Contracts.DataContracts",
                "Line1": "456 8th Street",
                "Line2": "apt 123",
                "City": "Orlando",
                "Country": "US",
                "PostalCode": "32821", 
                "StateProvinceCode":"FL"
            },
            "PurchaseCancellationProtection": 1,

            "Donations":[{
		"CharityID": 2,
		"CharityName":"The First Tee of Central Florida",
		"DonationAmount":2.55,
		"EmployerIdentificationNumber": "27-0149539"
	}],
  "PaymentInformation": [
      
      
    {
      "__type": "CreditCardPayment:#GolfNow.API.Contracts.DataContracts",
      "CreditCardNumber": 4111111111111111,
      "ExpirationMonth": 12,
      "ExpirationYear": 2027,
      "BillingAddress": {
        "Line1": "501 E Oates Rd",
        "City": "Garland",
        "Country": "US",
        "StateProvinceCode": "TX",
        "PostalCode": 75043
      },
      "CVVCode": 321,
      "BillingName": "QA32 Test",
      "Amount": {
        "CurrencyCode": "USD",
        "Value": totaldue
      }
    }
  ]
}

    
    


# Send the POST request
response3 = requests.post(url, headers=headers, json=data)
print(totaldue)
ordercheckoutresponse = response3.json()
#print(totaldue)
# print("------------------------------------------------------------------------------------")
# print(ordercheckoutresponse)
# print("------------------------------------------------------------------------------------")



  
    
global Issuccessful
global Reservationnumber
global paidonlinetotal 
global Invoicetotal  
global Totalearnpoint 

Issuccessful = ordercheckoutresponse['Results'][0]['IsSuccessful']
Reservationnumber =  ordercheckoutresponse['Results'][0]['ReservationConfirmation']['ReservationID']
Invoicetotal = ordercheckoutresponse['Results'][0]['ReservationConfirmation']['Invoice']['DueOnline']['Summary']['Total'] 
paidonlinetotal =  ordercheckoutresponse['Results'][0]['ReservationConfirmation']['Payments'][0]['PaymentAmount']['Value']
Totalearnpoint = ordercheckoutresponse['Results'][0]['ReservationConfirmation']['Invoice']['LoyaltyEligibility']['TotalEarnablePoints'] 
print('The reservation created success = ',Issuccessful)
print('The reservation ID created: ',Reservationnumber)
print('Total Charge OrderInvoice: ',Invoicetotal ,'Total Paid Online: ',paidonlinetotal , 'Total Earnable Points: ',Totalearnpoint)

assert Invoicetotal == paidonlinetotal


#############################################################################################################
## api get reservation detail


url ='https://rc2-api.gnsvc.com/rest/customers/' + email1 +'/reservation-details/'+ str(Reservationnumber) +'?channelid=331'


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
#print(response5.text)
response = response5.json()



def validate_response_resdetail(response: Dict[str, Any]) -> bool:
    try:
        # Validate ChannelID
        assert 'ChannelID' in response, "Missing key: ChannelID"
        assert isinstance(response['ChannelID'], int), "ChannelID should be an integer"
        
        # Validate GuestInfo
        assert 'GuestInfo' in response, "Missing key: GuestInfo"
        guest_info = response['GuestInfo']
        assert isinstance(guest_info, dict), "GuestInfo should be a dictionary"
        assert 'EmailAddress' in guest_info, "Missing key: GuestInfo.EmailAddress"
        assert 'FirstName' in guest_info, "Missing key: GuestInfo.FirstName"
        assert 'LastName' in guest_info, "Missing key: GuestInfo.LastName"
        assert 'PhoneNumber' in guest_info, "Missing key: GuestInfo.PhoneNumber"
        assert isinstance(guest_info['EmailAddress'], str), "GuestInfo.EmailAddress should be a string"
        assert isinstance(guest_info['FirstName'], str), "GuestInfo.FirstName should be a string"
        assert isinstance(guest_info['LastName'], str), "GuestInfo.LastName should be a string"
        assert isinstance(guest_info['PhoneNumber'], str), "GuestInfo.PhoneNumber should be a string"

        # Validate LoyaltyEligibility
        assert 'LoyaltyEligibility' in response, "Missing key: LoyaltyEligibility"
        loyalty_eligibility = response['LoyaltyEligibility']
        assert isinstance(loyalty_eligibility, dict), "LoyaltyEligibility should be a dictionary"
        required_keys = [
            'AllowedLoyaltyDiscountAmount', 'AllowedLoyaltyDiscountPoints',
            'BaseAllowedLoyaltyDiscountAmount', 'BaseAllowedLoyaltyDiscountPoints',
            'Presets', 'TotalBaseEarnablePoints', 'TotalEarnablePoints',
            'TotalPointsAvailable', 'TotalPointsToRedeem', 'TotalPromotionalEarnablePoints',
            'TransactionFeePreset'
        ]
        for key in required_keys:
            assert key in loyalty_eligibility, f"Missing key: LoyaltyEligibility.{key}"

        # Validate MemberPricingDetail
        assert 'MemberPricingDetail' in response, "Missing key: MemberPricingDetail"
        member_pricing_detail = response['MemberPricingDetail']
        assert isinstance(member_pricing_detail, dict), "MemberPricingDetail should be a dictionary"
        assert 'RateAdjustment' in member_pricing_detail, "Missing key: MemberPricingDetail.RateAdjustment"
        rate_adjustment = member_pricing_detail['RateAdjustment']
        assert isinstance(rate_adjustment, dict), "RateAdjustment should be a dictionary"
        assert 'CurrencyCode' in rate_adjustment, "Missing key: RateAdjustment.CurrencyCode"
        assert 'Value' in rate_adjustment, "Missing key: RateAdjustment.Value"
        assert rate_adjustment['CurrencyCode'] == 'USD', "RateAdjustment.CurrencyCode should be 'USD'"
        assert isinstance(rate_adjustment['Value'], (float, int)), "RateAdjustment.Value should be a number"

        # Validate PaidOnlineDistributionDetail
        assert 'PaidOnlineDistributionDetail' in response, "Missing key: PaidOnlineDistributionDetail"
        paid_online_distribution_detail = response['PaidOnlineDistributionDetail']
        assert isinstance(paid_online_distribution_detail, dict), "PaidOnlineDistributionDetail should be a dictionary"
        required_keys = ['CourseGreenFees', 'CourseTaxes', 'CourseTotal', 'GolfNowConvenienceFee', 'GolfNowDeposit', 'GolfNowTaxes', 'GolfNowTotal']
        for key in required_keys:
            assert key in paid_online_distribution_detail, f"Missing key: PaidOnlineDistributionDetail.{key}"

        # Validate Players
        assert 'Players' in response, "Missing key: Players"
        assert isinstance(response['Players'], int), "Players should be an integer"

        # Validate ReservationID
        assert 'ReservationID' in response, "Missing key: ReservationID"
        assert isinstance(response['ReservationID'], int), "ReservationID should be an integer"

        # Validate ReservationMetadata
        assert 'ReservationMetadata' in response, "Missing key: ReservationMetadata"
        reservation_metadata = response['ReservationMetadata']
        assert isinstance(reservation_metadata, list), "ReservationMetadata should be a list"
        for item in reservation_metadata:
            assert isinstance(item, dict), "Each item in ReservationMetadata should be a dictionary"
            assert 'Key' in item, "Missing key: ReservationMetadata.Key"
            assert 'Value' in item, "Missing key: ReservationMetadata.Value"
            assert isinstance(item['Key'], int), "ReservationMetadata.Key should be an integer"
            assert isinstance(item['Value'], str), "ReservationMetadata.Value should be a string"

        # Validate ReservationOrders
        assert 'ReservationOrders' in response, "Missing key: ReservationOrders"
        assert isinstance(response['ReservationOrders'], list), "ReservationOrders should be a list"

        # Validate SmartPlayOrderInfo
        assert 'SmartPlayOrderInfo' in response, "Missing key: SmartPlayOrderInfo"
        assert response['SmartPlayOrderInfo'] is None, "SmartPlayOrderInfo should be None"

        return True
    except AssertionError as e:
        print(f"Validation error: {e}")
        return False

is_valid3 = validate_response_resdetail(response)
print(f"Verify Res Detail Before Cancellation: Validation result: Pass = {is_valid3}")

##############################################################################################################
##api cancellation details



import requests

# Set the endpoint URL


url = 'https://rc2-api.gnsvc.com/GolfNowAPI.svc/rest/customers/'+ email1 +'/cancellation-details/'+ str(Reservationnumber) +'?cancellationReasonId=4'

# Define the headers
headers = {
    'UserName': '206407992',  # Replace with the actual username
    'Password': 'DonkeyPoo',  # Replace with the actual password
    'Content-Type': 'application/json',
    'CustomerToken': apicustomertoken
}
# Define the payload
payload = {
    "ChannelID": 331,
    "Players": 0,
    "ReservationID": Reservationnumber
}

# Make the POST request
response3 = requests.post(url, headers=headers, json=payload)
#print(response3.text)
# Print the response text (or process it in other ways)
print('Cancellation detail call status: ',response3.status_code)
response = response3.json()

def validate_response_canceldetail(response: Dict[str, Any]) -> bool:
    try:
        # Validate Cancellable
        assert 'Cancellable' in response, "Missing key: Cancellable"
        assert isinstance(response['Cancellable'], bool), "Cancellable should be a boolean"

        # Validate CancellationWindowPassed
        assert 'CancellationWindowPassed' in response, "Missing key: CancellationWindowPassed"
        assert isinstance(response['CancellationWindowPassed'], bool), "CancellationWindowPassed should be a boolean"

        # Validate ChannelID
        assert 'ChannelID' in response, "Missing key: ChannelID"
        assert isinstance(response['ChannelID'], int), "ChannelID should be an integer"

        # Validate LoyaltyRefundableDetail
        assert 'LoyaltyRefundableDetail' in response, "Missing key: LoyaltyRefundableDetail"
        loyalty_refundable_detail = response['LoyaltyRefundableDetail']
        assert isinstance(loyalty_refundable_detail, dict), "LoyaltyRefundableDetail should be a dictionary"
        assert 'AmountRefundable' in loyalty_refundable_detail, "Missing key: LoyaltyRefundableDetail.AmountRefundable"
        assert 'PointsRefundable' in loyalty_refundable_detail, "Missing key: LoyaltyRefundableDetail.PointsRefundable"
        assert isinstance(loyalty_refundable_detail['AmountRefundable'], (int, float)), "AmountRefundable should be a number"
        assert isinstance(loyalty_refundable_detail['PointsRefundable'], int), "PointsRefundable should be an integer"

        # Validate Players
        assert 'Players' in response, "Missing key: Players"
        assert isinstance(response['Players'], int), "Players should be an integer"

        # Validate Refundable
        assert 'Refundable' in response, "Missing key: Refundable"
        assert isinstance(response['Refundable'], bool), "Refundable should be a boolean"

        # Validate RefundableDetails
        assert 'RefundableDetails' in response, "Missing key: RefundableDetails"
        refundable_details = response['RefundableDetails']
        assert isinstance(refundable_details, dict), "RefundableDetails should be a dictionary"
        assert 'Distributions' in refundable_details, "Missing key: RefundableDetails.Distributions"
        assert 'TotalRefundable' in refundable_details, "Missing key: RefundableDetails.TotalRefundable"
        assert isinstance(refundable_details['Distributions'], list), "Distributions should be a list"
        assert isinstance(refundable_details['TotalRefundable'], (int, float)), "TotalRefundable should be a number"
        for distribution in refundable_details['Distributions']:
            assert isinstance(distribution, dict), "Each distribution should be a dictionary"
            assert 'AccountBalanceRefund' in distribution, "Missing key: Distribution.AccountBalanceRefund"
            account_balance_refund = distribution['AccountBalanceRefund']
            assert isinstance(account_balance_refund, dict), "AccountBalanceRefund should be a dictionary"
            assert 'Amount' in account_balance_refund, "Missing key: AccountBalanceRefund.Amount"
            assert isinstance(account_balance_refund['Amount'], (int, float)), "AccountBalanceRefund.Amount should be a number"

        # Validate ReservationID
        assert 'ReservationID' in response, "Missing key: ReservationID"
        assert isinstance(response['ReservationID'], int), "ReservationID should be an integer"

        # Validate WorryFreeCovered
        assert 'WorryFreeCovered' in response, "Missing key: WorryFreeCovered"
        assert isinstance(response['WorryFreeCovered'], bool), "WorryFreeCovered should be a boolean"

        return True
    except AssertionError as e:
        print(f"Validation error: {e}")
        return False


# Running the validation function
is_valid4 = validate_response_canceldetail(response)
print(f"Verify Cancellation Detail Validation result: Pass = {is_valid4}")





####################################################################################################################
### api order update - player cancellation

# Define the endpoint URL



url = 'https://rc2-api.gnsvc.com/GolfNowAPI.svc/rest/customers/'+ email1 +'/reservation-details/'+ str(Reservationnumber) +'?cancellationReasonId=4'

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
        "EmailAddress": email1,
        "FirstName": "Guesty",
        "LastName": "Guestalot",
        "PhoneNumber": "7898765432"
    },
    "Players": 0,
    "ReservationID": Reservationnumber
}

# Make the PUT request
response4 = requests.put(url, headers=headers, json=data)
#print(response4.text)
# Print the response text (or process it in other ways)
#print('Api order update - player cancel - Status Code: ',response4.status_code)


#############################################################################################################
## api get reservation detail


url ='https://rc2-api.gnsvc.com/rest/customers/' + email1 +'/reservation-details/'+ str(Reservationnumber) +'?channelid=331'


# Define the headers
headers = {
    'UserName': '206407992',  # Replace with the actual username
    'Password': 'DonkeyPoo',  # Replace with the actual password
    'Content-Type': 'application/json',
    'CustomerToken': apicustomertoken
}





# Make the POST request
response5 = requests.get(url, headers=headers, json=data)


# Make the POST request
response5 = requests.get(url, headers=headers, json=data) 
print('Reservation Detail Status Code: ',response5.status_code)
#print(response5.text)
global Finalplayercount
global Finalstatus
Reservationdetail = response5.json()
response = response5.json()


Finalplayercount = Reservationdetail['Players']




print('Final Reservation Player Count: ',Finalplayercount)

assert Finalplayercount == 0

#assert "MemberPricingDetail" in Reservationdetail["MemberPricingDetail"][0], "MemberPricing key is missing in the response"
member_pricing = Reservationdetail["MemberPricingDetail"]
print('Member Price object in res detail post cancellation:')
print(member_pricing)
    
def validate_response(response: Dict[str, Any]) -> bool:
    try:
        # Check basic keys exist
        assert 'ChannelID' in response, "ChannelID is missing"
        assert 'GuestInfo' in response, "GuestInfo is missing"
        assert 'LoyaltyEligibility' in response, "LoyaltyEligibility is missing"
        assert 'MemberPricingDetail' in response, "MemberPricingDetail is missing"
        assert 'PaidOnlineDistributionDetail' in response, "PaidOnlineDistributionDetail is missing"
        assert 'ReservationID' in response, "ReservationID is missing"
        assert 'ReservationMetadata' in response, "ReservationMetadata is missing"
        assert 'ReservationOrders' in response, "ReservationOrders is missing"

        # Check ChannelID
        assert isinstance(response['ChannelID'], int), "ChannelID must be an integer"

        # Validate GuestInfo
        guest_info = response['GuestInfo']
        assert isinstance(guest_info, dict), "GuestInfo must be a dictionary"
        assert 'EmailAddress' in guest_info, "GuestInfo: EmailAddress is missing"
        assert 'FirstName' in guest_info, "GuestInfo: FirstName is missing"
        assert 'LastName' in guest_info, "GuestInfo: LastName is missing"
        assert 'PhoneNumber' in guest_info, "GuestInfo: PhoneNumber is missing"
        assert isinstance(guest_info['EmailAddress'], str), "GuestInfo: EmailAddress must be a string"
        assert isinstance(guest_info['FirstName'], str), "GuestInfo: FirstName must be a string"
        assert isinstance(guest_info['LastName'], str), "GuestInfo: LastName must be a string"
        assert isinstance(guest_info['PhoneNumber'], str), "GuestInfo: PhoneNumber must be a string"

        # Validate LoyaltyEligibility
        loyalty_eligibility = response['LoyaltyEligibility']
        assert isinstance(loyalty_eligibility, dict), "LoyaltyEligibility must be a dictionary"
        required_keys = [
            'AllowedLoyaltyDiscountAmount', 'AllowedLoyaltyDiscountPoints',
            'BaseAllowedLoyaltyDiscountAmount', 'BaseAllowedLoyaltyDiscountPoints',
            'Presets', 'TotalBaseEarnablePoints', 'TotalEarnablePoints',
            'TotalPointsAvailable', 'TotalPointsToRedeem', 'TotalPromotionalEarnablePoints',
            'TransactionFeePreset'
        ]
        for key in required_keys:
            assert key in loyalty_eligibility, f"LoyaltyEligibility: {key} is missing"

        # Validate MemberPricingDetail
        member_pricing_detail = response['MemberPricingDetail']
        assert isinstance(member_pricing_detail, dict), "MemberPricingDetail must be a dictionary"
        assert 'RateAdjustment' in member_pricing_detail, "MemberPricingDetail: RateAdjustment is missing"
        rate_adjustment = member_pricing_detail['RateAdjustment']
        assert isinstance(rate_adjustment, dict), "RateAdjustment must be a dictionary"
        assert 'CurrencyCode' in rate_adjustment, "RateAdjustment: CurrencyCode is missing"
        assert 'Value' in rate_adjustment, "RateAdjustment: Value is missing"
        assert rate_adjustment['CurrencyCode'] == 'USD', "RateAdjustment: CurrencyCode must be 'USD'"
        assert isinstance(rate_adjustment['Value'], (float, int)), "RateAdjustment: Value must be a float or int"

        # Validate PaidOnlineDistributionDetail
        paid_online_distribution_detail = response['PaidOnlineDistributionDetail']
        assert isinstance(paid_online_distribution_detail, dict), "PaidOnlineDistributionDetail must be a dictionary"
        required_keys = ['CourseGreenFees', 'CourseTaxes', 'CourseTotal', 'GolfNowConvenienceFee', 'GolfNowDeposit', 'GolfNowTaxes', 'GolfNowTotal']
        for key in required_keys:
            assert key in paid_online_distribution_detail, f"PaidOnlineDistributionDetail: {key} is missing"

        # Validate ReservationMetadata
        reservation_metadata = response['ReservationMetadata']
        assert isinstance(reservation_metadata, list), "ReservationMetadata must be a list"
        for item in reservation_metadata:
            assert isinstance(item, dict), "Each item in ReservationMetadata must be a dictionary"
            assert 'Key' in item, "ReservationMetadata item: Key is missing"
            assert 'Value' in item, "ReservationMetadata item: Value is missing"
            assert isinstance(item['Key'], int), "ReservationMetadata item: Key must be an integer"
            assert isinstance(item['Value'], str), "ReservationMetadata item: Value must be a string"

        return True
    except AssertionError as e:
        print(f"Validation failed: {e}")
        return False

# Perform validation
is_valid = validate_response(response)
print("Member Pricing Validation result: Passed =", is_valid)

# Specify the URL
url = "https://rc2-www.golfnowcentral.com/Reservation/Edit/"+str(Reservationnumber)

# Open the URL in the default web browser
webbrowser.open(url)