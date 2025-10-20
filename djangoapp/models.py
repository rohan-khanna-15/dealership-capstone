from django.db import models
from django.utils.timezone import now

# Car Make model
class CarMake(models.Model):
    name = models.CharField(null=False, max_length=100, default='')
    description = models.TextField(max_length=500)

    def __str__(self):
        return self.name

# Car Model model
class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=100, default='')
    
    CAR_TYPES = [
        ('SEDAN', 'Sedan'),
        ('SUV', 'SUV'),
        ('WAGON', 'Wagon'),
        ('HATCHBACK', 'Hatchback'),
        ('CONVERTIBLE', 'Convertible'),
        ('COUPE', 'Coupe'),
        ('TRUCK', 'Truck'),
    ]
    type = models.CharField(null=False, max_length=15, choices=CAR_TYPES, default='SEDAN')
    year = models.DateField(null=True)

    def __str__(self):
        return f"{self.car_make.name} {self.name}"

# Car Dealer model (for proxy service)
class CarDealer:
    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        self.address = address
        self.city = city
        self.full_name = full_name
        self.id = id
        self.lat = lat
        self.long = long
        self.short_name = short_name
        self.st = st
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name

# Dealer Review model (for proxy service)
class DealerReview:
    def __init__(self, dealership, name, purchase, review):
        self.dealership = dealership
        self.name = name
        self.purchase = purchase
        self.review = review
        self.purchase_date = None
        self.car_make = None
        self.car_model = None
        self.car_year = None
        self.sentiment = None
        self.id = None

    def __str__(self):
        return "Review: " + self.review
