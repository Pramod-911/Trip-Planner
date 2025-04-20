# AI-Based Travel Planner 🧳🌍

## Project Overview
The **AI-Based Travel Planner** is a web-based application designed to simplify and personalize the trip planning experience using machine learning techniques. By analyzing user preferences such as destination, budget, group size, and interests, the application generates customized travel itineraries, recommending optimal places, hotels, and restaurants.

## Features 🚀
- **Personalized Itinerary Generation** based on user preferences.
- **Dynamic Clustering** of destinations using KMeans.
- **Hotel & Restaurant Recommendations** filtered by budget, rating, and location.
- **Intelligent Planning** using user behavior and preference patterns.
- **User-Friendly Interface** built with HTML and CSS.
- **Real-Time Recommendations** and error handling.

## Tech Stack 🛠️
- **Frontend**: HTML, CSS
- **Backend**: Flask (Python)
- **Libraries**: pandas, scikit-learn (KMeans, OneHotEncoder, silhouette_score)
- **Data Sources**: Places, Hotels, and Restaurants datasets

## Machine Learning Approach 🤖
- **KMeans Clustering**: Groups destinations based on features like significance, rating, and location.
- **OneHotEncoder**: Transforms categorical data into machine-readable format.
- **Silhouette Score**: Validates the clustering quality.

## Datasets 📊
- **Places Dataset**: Zone, significance, reviews, best time to visit.
- **Hotels Dataset**: Name, price, amenities, ratings, proximity.
- **Restaurants Dataset**: Name, cuisine, rating, city, cost.

## Application Flow 📈
1. **User Input**: Destination, days, budget, group info, significance.
2. **ML Processing**: Filter and cluster places, pick hotels and restaurants.
3. **Output**: Day-wise itinerary with place, restaurant, and hotel.

## Future Enhancements 🔮
- Real-time data integration via APIs (e.g., Google Places, TripAdvisor)
- Map-based route visualization
- User login system with saved itineraries and history

## How to Run 🧑‍💻
1. Clone the repository.
2. Ensure Flask and required Python libraries are installed.
3. Run the Flask app:
   ```bash
   python Travel_Planner.py
