const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3030;

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB connection (using in-memory data for simplicity)
const dealerships = [
    { "id": 1, "city": "El Paso", "state": "Texas", "st": "TX", "address": "3 Nova Dr", "zip": "88005", "lat": "32.359", "long": "-106.37", "short_name": "El Paso", "full_name": "Dealership El Paso" },
    { "id": 2, "city": "Kansas City", "state": "Kansas", "st": "KS", "address": "1823 W 48th Pl", "zip": "66205", "lat": "39.0473", "long": "-94.6274", "short_name": "Kansas City", "full_name": "Dealership Kansas City" },
    { "id": 3, "city": "Topeka", "state": "Kansas", "st": "KS", "address": "1448 SE 29th St", "zip": "66605", "lat": "39.0267", "long": "-95.6890", "short_name": "Topeka", "full_name": "Dealership Topeka" },
    { "id": 29, "city": "New York", "state": "New York", "st": "NY", "address": "625 W 55th St", "zip": "10019", "lat": "40.7663", "long": "-73.9816", "short_name": "New York", "full_name": "Dealership New York" }
];

const reviews = [
    { "id": 1, "name": "Berkly Shepley", "dealership": 29, "review": "Great service and excellent customer support!", "purchase": true, "purchase_date": "07/11/2020", "car_make": "Audi", "car_model": "A6", "car_year": 2010, "sentiment": "positive" },
    { "id": 2, "name": "Modestine Trevaskiss", "dealership": 29, "review": "Had an amazing experience buying my new car here.", "purchase": true, "purchase_date": "12/25/2020", "car_make": "BMW", "car_model": "X5", "car_year": 2018, "sentiment": "positive" },
    { "id": 3, "name": "Tova Kohnert", "dealership": 3, "review": "Excellent dealership with professional staff.", "purchase": true, "purchase_date": "02/15/2021", "car_make": "Toyota", "car_model": "Camry", "car_year": 2019, "sentiment": "positive" }
];

// Routes
app.get('/', (req, res) => {
    res.json({ message: "Dealership and Reviews Service", status: "running" });
});

// Fetch all dealerships
app.get('/fetchDealers', (req, res) => {
    res.json(dealerships);
});

// Fetch dealership by ID
app.get('/fetchDealer/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const dealer = dealerships.find(d => d.id === id);
    if (dealer) {
        res.json(dealer);
    } else {
        res.status(404).json({ error: "Dealer not found" });
    }
});

// Fetch dealers by state - FIXED VERSION
app.get('/fetchDealers/:state', (req, res) => {
    const state = req.params.state;
    console.log(`Filtering dealers by state: ${state}`);
    
    const stateDealers = dealerships.filter(d => 
        d.state.toLowerCase().includes(state.toLowerCase()) || 
        d.st.toLowerCase() === state.toLowerCase() ||
        d.city.toLowerCase().includes(state.toLowerCase())
    );
    
    console.log(`Found ${stateDealers.length} dealers for state: ${state}`);
    res.json(stateDealers);
});

// Fetch all reviews
app.get('/fetchReviews', (req, res) => {
    res.json(reviews);
});

// Fetch reviews for a specific dealer
app.get('/fetchReviews/dealer/:id', (req, res) => {
    const dealerId = parseInt(req.params.id);
    const dealerReviews = reviews.filter(r => r.dealership === dealerId);
    res.json(dealerReviews);
});

// Insert a new review
app.post('/insertReview', (req, res) => {
    const newReview = {
        id: reviews.length + 1,
        name: req.body.name,
        dealership: req.body.dealership,
        review: req.body.review,
        purchase: req.body.purchase,
        purchase_date: req.body.purchase_date,
        car_make: req.body.car_make,
        car_model: req.body.car_model,
        car_year: req.body.car_year,
        sentiment: req.body.sentiment || "neutral"
    };
    
    reviews.push(newReview);
    res.json({ message: "Review added successfully", review: newReview });
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
