import requests
import json
from .models import CarDealer, DealerReview

def get_request(url, **kwargs):
    print(f"GET from {url}")
    try:
        response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Network exception occurred: {e}")
        return None

def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url)
    if json_result:
        # Handle both single dealer and multiple dealers
        dealers = json_result if isinstance(json_result, list) else [json_result]
        for dealer in dealers:
            dealer_obj = CarDealer(
                address=dealer.get("address", ""),
                city=dealer.get("city", ""),
                full_name=dealer.get("full_name", ""),
                id=dealer.get("id", 0),
                lat=dealer.get("lat", ""),
                long=dealer.get("long", ""),
                short_name=dealer.get("short_name", ""),
                st=dealer.get("st", ""),
                zip=dealer.get("zip", "")
            )
            results.append(dealer_obj)
    return results

def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    json_result = get_request(url)
    if json_result:
        reviews = json_result
        for review in reviews:
            review_obj = DealerReview(
                dealership=review.get("dealership", dealerId),
                name=review.get("name", ""),
                purchase=review.get("purchase", False),
                review=review.get("review", "")
            )
            review_obj.id = review.get("id")
            review_obj.purchase_date = review.get("purchase_date")
            review_obj.car_make = review.get("car_make")
            review_obj.car_model = review.get("car_model")
            review_obj.car_year = review.get("car_year")
            review_obj.sentiment = review.get("sentiment", "neutral")
            results.append(review_obj)
    return results

def post_request(url, json_payload, **kwargs):
    print(f"POST to {url}")
    try:
        response = requests.post(url, json=json_payload, headers={'Content-Type': 'application/json'})
        print(f"Status code: {response.status_code}")
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Network exception occurred: {e}")
        return None

def analyze_review_sentiments(text):
    # Simple sentiment analysis for demo
    if any(word in text.lower() for word in ["great", "excellent", "amazing", "love", "best"]):
        return "positive"
    elif any(word in text.lower() for word in ["bad", "terrible", "awful", "hate", "worst"]):
        return "negative"
    else:
        return "neutral"
