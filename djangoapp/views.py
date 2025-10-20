from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import CarMake, CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request, analyze_review_sentiments
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def get_dealerships(request, state=None):
    context = {}
    if request.method == "GET":
        # Get state from URL parameter or GET parameter
        if not state:
            state = request.GET.get('state')
        
        url = "http://localhost:3030/fetchDealers"
        if state and state.strip():
            url = f"http://localhost:3030/fetchDealers/{state}"
        
        try:
            dealerships = get_dealers_from_cf(url)
            context["dealership_list"] = dealerships
            context["selected_state"] = state
        except:
            print("Error occurred while getting dealerships")
            context["dealership_list"] = []
        
        if request.user.is_authenticated:
            context['username'] = request.user.username
        return render(request, 'djangoapp/index.html', context)

def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        # Get dealer details
        dealer_url = f"http://localhost:3030/fetchDealer/{dealer_id}"
        try:
            dealership_data = get_dealers_from_cf(dealer_url)
            context["dealer"] = dealership_data[0] if dealership_data else None
        except:
            print("Error getting dealer details")
            context["dealer"] = None
        
        # Get dealer reviews
        reviews_url = f"http://localhost:3030/fetchReviews/dealer/{dealer_id}"
        try:
            reviews = get_dealer_reviews_from_cf(reviews_url, dealer_id)
            context["reviews"] = reviews
        except:
            print("Error getting reviews")
            context["reviews"] = []
        
        context["dealer_id"] = dealer_id
        if request.user.is_authenticated:
            context['username'] = request.user.username
        
        return render(request, 'djangoapp/dealer_details.html', context)

def get_dealer_reviews(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = f"http://localhost:3030/fetchReviews/dealer/{dealer_id}"
        try:
            reviews = get_dealer_reviews_from_cf(url, dealer_id)
            context["reviews"] = reviews
            context["dealer_id"] = dealer_id
        except:
            print("Error getting reviews")
            context["reviews"] = []
        return render(request, 'djangoapp/dealer_details.html', context)

def add_review(request):
    context = {}
    dealer_id = request.GET.get('dealer')
    
    if not dealer_id:
        return redirect('djangoapp:get_dealers')
    
    if request.method == "GET":
        try:
            # Make sure Express server is running
            url = f"http://localhost:3030/fetchDealer/{dealer_id}"
            print(f"Fetching dealer from: {url}")
            dealership_data = get_dealers_from_cf(url)
            
            if dealership_data:
                context["dealer"] = dealership_data[0]
                print(f"Found dealer: {dealership_data[0].full_name}")
            else:
                print("No dealer data returned")
                # Create a mock dealer for testing
                context["dealer"] = type('MockDealer', (), {
                    'id': dealer_id,
                    'full_name': f'Test Dealership {dealer_id}',
                    'city': 'Test City',
                    'st': 'TX'
                })()
            
            context["dealer_id"] = dealer_id
            context["cars"] = CarModel.objects.all()
            
        except Exception as e:
            print(f"Error getting dealer for review: {e}")
            # Create a mock dealer for testing
            context["dealer"] = type('MockDealer', (), {
                'id': dealer_id,
                'full_name': f'Test Dealership {dealer_id}',
                'city': 'Test City',
                'st': 'TX'
            })()
            context["cars"] = CarModel.objects.all()
            
        return render(request, 'djangoapp/add_review.html', context)
    
    elif request.method == "POST":
        if request.user.is_authenticated:
            username = request.user.username
            payload = dict()
            car_id = request.POST.get("car")
            
            if car_id:
                try:
                    car = CarModel.objects.get(pk=car_id)
                    payload["car_make"] = car.car_make.name
                    payload["car_model"] = car.name
                except CarModel.DoesNotExist:
                    payload["car_make"] = "Unknown"
                    payload["car_model"] = "Unknown"
            else:
                payload["car_make"] = "Unknown"
                payload["car_model"] = "Unknown"
            
            payload["time"] = datetime.utcnow().isoformat()
            payload["name"] = username
            payload["dealership"] = int(dealer_id)
            payload["review"] = request.POST.get("content", "")
            payload["purchase"] = "purchasecheck" in request.POST
            payload["purchase_date"] = request.POST.get("purchasedate", "")
            payload["car_year"] = int(request.POST.get("car_year", 2023))

            try:
                review_post_url = "http://localhost:3030/insertReview"
                post_request(review_post_url, payload)
            except Exception as e:
                print(f"Error posting review: {e}")
        
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)

def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)

def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        email = request.POST['email']
        
        username_exist = False
        email_exist = False
        try:
            User.objects.get(username=username)
            username_exist = True
        except:
            pass
        
        if not username_exist:
            user = User.objects.create_user(username=username, first_name=first_name, 
                                          last_name=last_name, password=password, email=email)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists"
            return render(request, 'djangoapp/registration.html', context)

def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })
    return JsonResponse({"CarModels": cars})

def initiate():
    car_make_data = [
        {"name": "NISSAN", "description": "Great cars. Japanese technology"},
        {"name": "Mercedes", "description": "Great cars. German technology"},
        {"name": "Audi", "description": "Great cars. German technology"},
        {"name": "Kia", "description": "Great cars. Korean technology"},
        {"name": "Toyota", "description": "Great cars. Japanese technology"},
        {"name": "BMW", "description": "Great cars. German technology"},
        {"name": "Honda", "description": "Great cars. Japanese technology"},
        {"name": "Ford", "description": "Great cars. American technology"},
        {"name": "Chevrolet", "description": "Great cars. American technology"},
        {"name": "Hyundai", "description": "Great cars. Korean technology"},
    ]

    car_make_instances = []
    for data in car_make_data:
        car_make_instances.append(CarMake(name=data['name'], description=data['description']))
    CarMake.objects.bulk_create(car_make_instances)

    car_model_data = [
        {"name": "Pathfinder", "type": "SUV", "year": "2023-01-01", "make_name": "NISSAN"},
        {"name": "Qashqai", "type": "SUV", "year": "2023-01-01", "make_name": "NISSAN"},
        {"name": "XTRAIL", "type": "SUV", "year": "2023-01-01", "make_name": "NISSAN"},
        {"name": "A-Class", "type": "SEDAN", "year": "2023-01-01", "make_name": "Mercedes"},
        {"name": "C-Class", "type": "SEDAN", "year": "2023-01-01", "make_name": "Mercedes"},
        {"name": "E-Class", "type": "SEDAN", "year": "2023-01-01", "make_name": "Mercedes"},
        {"name": "A4", "type": "SEDAN", "year": "2023-01-01", "make_name": "Audi"},
        {"name": "A5", "type": "COUPE", "year": "2023-01-01", "make_name": "Audi"},
        {"name": "A3", "type": "SEDAN", "year": "2023-01-01", "make_name": "Audi"},
        {"name": "Soul", "type": "SUV", "year": "2023-01-01", "make_name": "Kia"},
        {"name": "Forte", "type": "SEDAN", "year": "2023-01-01", "make_name": "Kia"},
        {"name": "Sportage", "type": "SUV", "year": "2023-01-01", "make_name": "Kia"},
        {"name": "Corolla", "type": "SEDAN", "year": "2023-01-01", "make_name": "Toyota"},
        {"name": "Camry", "type": "SEDAN", "year": "2023-01-01", "make_name": "Toyota"},
        {"name": "RAV4", "type": "SUV", "year": "2023-01-01", "make_name": "Toyota"},
    ]

    for model_data in car_model_data:
        car_make = CarMake.objects.get(name=model_data["make_name"])
        car_model = CarModel(name=model_data["name"], 
                           car_make=car_make, 
                           type=model_data["type"], 
                           year=model_data["year"])
        car_model.save()

def analyze_sentiment(request, text):
    """Mock sentiment analyzer endpoint for demonstration"""
    # Simple sentiment analysis logic
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["great", "excellent", "amazing", "love", "best", "wonderful", "fantastic"]):
        sentiment = "positive"
        confidence = 0.85
    elif any(word in text_lower for word in ["bad", "terrible", "awful", "hate", "worst", "horrible"]):
        sentiment = "negative"
        confidence = 0.80
    else:
        sentiment = "neutral"
        confidence = 0.60
    
    result = {
        "text": text,
        "sentiment": sentiment,
        "confidence": confidence,
        "service": "Mock Sentiment Analyzer",
        "status": "success"
    }
    
    return JsonResponse(result)
