from flask import Flask, render_template, request
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import silhouette_score

# Initialize Flask app
app = Flask(__name__)

# Define datasets
places_data = pd.read_csv("Places_data.csv")

restaurants_data = pd.read_csv("restaurants_data.csv")

hotels_data = pd.DataFrame({
    "HotelID": [1, 2, 3, 4, 5],
    "Name": ["Sunset Resort", "Heritage Stay", "Peak Retreat", "Urban Comfort", "Jungle Escape"],
    "Location": ["Goa", "Delhi", "Manali", "Delhi", "Goa"],
    "RoomTypes": ["Deluxe, Suite", "Single, Double", "Suite", "Economy, Deluxe", "Luxury"],
    "PriceRange": ["Medium", "High", "High", "Low", "Medium"],
    "Rating": [4.8, 4.6, 4.7, 4.4, 4.9],
    "Amenities": ["WiFi, Pool, Spa", "Breakfast, WiFi", "Parking, WiFi", "WiFi", "Nature View, Pool"],
    "DistanceToAttractions": ["500m", "1km", "2km", "800m", "600m"]
})

# Clustering function
def cluster_places(places_data):
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    encoded_features = encoder.fit_transform(places_data[['Zone', 'State', 'City', 'Google review rating', 'Significance']])
    
    kmeans = KMeans(n_clusters=10, random_state=42)
    places_data['Cluster'] = kmeans.fit_predict(encoded_features)

    # Calculate silhouette score to evaluate clustering quality
    silhouette_avg = silhouette_score(encoded_features, places_data['Cluster'])
    print(f"Silhouette Score: {silhouette_avg}")

    return kmeans, places_data

kmeans_model, clustered_places = cluster_places(places_data)

# Generate Trip Plan
def create_trip_plan(destination, days, significance, budget, group_size, group_type):
    # Filter places based on Zone, State, City, or Name matching destination
    filtered_places = clustered_places[
        clustered_places['Zone'].str.contains(destination, case=False, na=False) |
        clustered_places['State'].str.contains(destination, case=False, na=False) |
        clustered_places['City'].str.contains(destination, case=False, na=False) |
        clustered_places['Name'].str.contains(destination, case=False, na=False)
    ]

    if filtered_places.empty:
        return None, None, "No recommendations available for the specified criteria."

    # Filter places based on multiple selected significance values
    if significance:  # Check if there are any selected significance values
        places_by_significance = filtered_places[
            filtered_places['Significance'].apply(lambda x: any(val in x for val in significance))
        ]
    else:
        places_by_significance = filtered_places  # If no significance is selected, show all

    if places_by_significance.empty:
        places_by_significance = filtered_places

    # Repeat rows if not enough places are available
    repeated_places = pd.concat([places_by_significance] * ((days // len(places_by_significance)) + 1))
    recommended_places = repeated_places.head(days)

    # Extract the city of the recommended places
    recommended_cities = recommended_places['City'].unique()

    # Filter hotels and restaurants based on the city of recommended places
    filtered_hotels = hotels_data[hotels_data['Location'].isin(recommended_cities)]
    filtered_restaurants = restaurants_data[restaurants_data['City'].isin(recommended_cities)]

    if filtered_hotels.empty or filtered_restaurants.empty:
        return None, None, "No hotels or restaurants available in the recommended places."

    # Select the top-rated hotel for the stay
    selected_hotel = filtered_hotels.nlargest(1, 'Rating').iloc[0]

    # List to track used restaurants
    used_restaurants = []
    daily_plan = []

    for day in range(days):
        # Get the city of the place for the current day
        current_city = recommended_places.iloc[day]['City']
        
        # Filter restaurants for the current city, excluding used restaurants
        city_restaurants = filtered_restaurants[
            (filtered_restaurants['City'] == current_city) &
            (~filtered_restaurants['Name'].isin(used_restaurants))
        ]
        
        # If no unused restaurants are found in the current city, reset the used list for that city
        if city_restaurants.empty:
            used_restaurants = []
            city_restaurants = filtered_restaurants[filtered_restaurants['City'] == current_city]
        
        # Select the top-rated unused restaurant for the current city
        selected_restaurant = city_restaurants.nlargest(1, 'Rating').iloc[0]
        
        # Add the restaurant to the used list
        used_restaurants.append(selected_restaurant['Name'])
        
        # Append the plan for the day
        daily_plan.append({
            "Day": day + 1,
            "Place_Name": recommended_places.iloc[day]['Name'],
            "Place_Zone": recommended_places.iloc[day]['Zone'],
            "Place_State": recommended_places.iloc[day]['State'],
            "Place_City": recommended_places.iloc[day]['City'],
            "Place_Significance": recommended_places.iloc[day]['Significance'],
            "Place_GoogleReviewRating": recommended_places.iloc[day]['Google review rating'],
            "Place_EntranceFeeinINR": places_data.loc[places_data['Name'] == recommended_places.iloc[day]['Name']]['Entrance Fee in INR'].values,
            "Place_Airportwith50kmRadius": places_data.loc[places_data['Name'] == recommended_places.iloc[day]['Name']]['Airport with 50km Radius'].values,
            "Place_BestTimetovisit": places_data.loc[places_data['Name'] == recommended_places.iloc[day]['Name']]['Best Time to visit'].values,
            "Restaurant_Name": selected_restaurant['Name'],
            "Restaurant_Location": selected_restaurant['Location'],
            "Restaurant_Locality": selected_restaurant['Locality'],
            "Restaurant_City": selected_restaurant['City'],
            "Restaurant_Cuisine": selected_restaurant['Cuisine'],
            "Restaurant_Rating": selected_restaurant['Rating'],
            "Restaurant_Cost": selected_restaurant['Cost'],
        })

    return daily_plan, selected_hotel, None

# Flask Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/plan', methods=['POST'])
def plan():
    destination = request.form.get("destination")
    days = request.form.get("days")
    if not days or not days.isdigit():
        return "Please enter a valid number of days."
    days = int(days)

    significance = request.form.getlist("significance")
    budget = request.form.get("budget")
    group_size = request.form.get("group_size")
    if not group_size or not group_size.isdigit():
        return "Please enter a valid number for group size."
    group_size = int(group_size)
    
    group_type = request.form.get("group_type")

    trip_plan, hotel, error_message = create_trip_plan(destination, days, significance, budget, group_size, group_type)

    if error_message:
        return error_message

    return render_template(
        'plan.html',
        trip_plan=trip_plan,
        hotel=hotel
    )

if __name__ == "__main__":
    app.run(debug=True)
