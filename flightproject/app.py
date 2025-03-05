# app.py

from flask import Flask, render_template, request, jsonify
import heapq
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# Flight route data using full city names.
flight_routes = {
    "New York City": {"London": 500, "Dubai": 900, "Tokyo": 700},
    "Los Angeles": {"San Francisco": 100, "Miami": 400, "New York City": 300},
    "Chicago": {"Atlanta": 200, "Miami": 350},
    "Atlanta": {"Miami": 150, "London": 600},
    "Miami": {"London": 550},
    "San Francisco": {"Los Angeles": 100, "Tokyo": 650},
    "London": {"Paris": 100, "Berlin": 150, "Manchester": 80},
    "Manchester": {"London": 80},
    "Paris": {"Berlin": 120, "Rome": 150},
    "Berlin": {"Amsterdam": 100, "Rome": 180},
    "Rome": {"Amsterdam": 90, "Athens": 120},
    "Amsterdam": {"Athens": 150},
    "Athens": {"Tokyo": 700},
    "Tokyo": {"Seoul": 80, "Bangkok": 400},
    "Seoul": {"Bangkok": 350, "Tokyo": 80},
    "Bangkok": {"Singapore": 200, "Dubai": 400},
    "Singapore": {"Dubai": 350, "Sydney": 600},
    "Dubai": {"Sydney": 800, "Mumbai": 250},
    "Mumbai": {"Delhi": 100, "Bangalore": 90},
    "Delhi": {"Bangalore": 100},
    "Bangalore": {"Delhi": 100},
    "Sydney": {"Melbourne": 100},
    "Melbourne": {"Sydney": 100},
    "São Paulo": {"New York City": 600}
}

# Flight times (in hours) for each segment.
flight_times = {
    "New York City": {"London": 7.0, "Dubai": 12.0, "Tokyo": 14.0},
    "Los Angeles": {"San Francisco": 1.0, "Miami": 5.5, "New York City": 6.0},
    "Chicago": {"Atlanta": 2.0, "Miami": 3.5},
    "Atlanta": {"Miami": 1.5, "London": 7.5},
    "Miami": {"London": 7.0},
    "San Francisco": {"Los Angeles": 1.0, "Tokyo": 11.0},
    "London": {"Paris": 1.0, "Berlin": 1.5, "Manchester": 0.75},
    "Manchester": {"London": 0.75},
    "Paris": {"Berlin": 1.25, "Rome": 2.0},
    "Berlin": {"Amsterdam": 1.0, "Rome": 2.5},
    "Rome": {"Amsterdam": 1.0, "Athens": 2.0},
    "Amsterdam": {"Athens": 2.0},
    "Athens": {"Tokyo": 11.0},
    "Tokyo": {"Seoul": 1.5, "Bangkok": 6.5},
    "Seoul": {"Bangkok": 5.5, "Tokyo": 1.5},
    "Bangkok": {"Singapore": 2.5, "Dubai": 7.0},
    "Singapore": {"Dubai": 6.5, "Sydney": 8.5},
    "Dubai": {"Sydney": 14.0, "Mumbai": 3.0},
    "Mumbai": {"Delhi": 1.5, "Bangalore": 1.0},
    "Delhi": {"Bangalore": 1.5},
    "Bangalore": {"Delhi": 1.5},
    "Sydney": {"Melbourne": 1.0},
    "Melbourne": {"Sydney": 1.0},
    "São Paulo": {"New York City": 9.0}
}

# Coordinates for each city.
coordinates = {
    "New York City": [40.7128, -74.0060],
    "Los Angeles": [34.0522, -118.2437],
    "Chicago": [41.8781, -87.6298],
    "Atlanta": [33.7490, -84.3880],
    "Miami": [25.7617, -80.1918],
    "San Francisco": [37.7749, -122.4194],
    "London": [51.5074, -0.1278],
    "Manchester": [53.4808, -2.2426],
    "Paris": [48.8566, 2.3522],
    "Berlin": [52.5200, 13.4050],
    "Rome": [41.9028, 12.4964],
    "Amsterdam": [52.3676, 4.9041],
    "Athens": [37.9838, 23.7275],
    "Tokyo": [35.6895, 139.6917],
    "Seoul": [37.5665, 126.9780],
    "Bangkok": [13.7563, 100.5018],
    "Singapore": [1.3521, 103.8198],
    "Dubai": [25.2048, 55.2708],
    "Mumbai": [19.0760, 72.8777],
    "Delhi": [28.7041, 77.1025],
    "Bangalore": [12.9716, 77.5946],
    "Sydney": [-33.8688, 151.2093],
    "Melbourne": [-37.8136, 144.9631],
    "São Paulo": [-23.5505, -46.6333]
}

def find_optimal_route(source, destination):
    """Uses Dijkstra's algorithm to find the lowest-cost route."""
    heap = [(0, source, [])]
    visited = set()
    while heap:
        cost, city, path = heapq.heappop(heap)
        if city in visited:
            continue
        path = path + [city]
        visited.add(city)
        if city == destination:
            return {"route": path, "total_cost": cost}
        for neighbor, flight_cost in flight_routes.get(city, {}).items():
            if neighbor not in visited:
                heapq.heappush(heap, (cost + flight_cost, neighbor, path))
    return {"route": [], "total_cost": float("inf")}

def calculate_total_travel_time(route):
    """Calculates the total travel time (in hours) along the route."""
    total_time = 0.0
    for i in range(len(route) - 1):
        src = route[i]
        dest = route[i+1]
        total_time += flight_times.get(src, {}).get(dest, 0)
    return total_time

def adjust_route_with_metta(route, total_cost):
    """Dummy integration with a hypothetical SingularityNET service."""
    url = "https://metta.singularitynet.io/api/optimize"  # Hypothetical endpoint
    payload = {"route": route, "total_cost": total_cost}
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("route", route), data.get("total_cost", total_cost)
    except Exception as e:
        print("Error calling SingularityNET metta service:", e)
    return route, total_cost

@app.route('/')
def home():
    return render_template(
        "index.html",
        cities=list(coordinates.keys()),
        coordinates=coordinates,
        flight_routes=flight_routes
    )

@app.route('/get_routes', methods=['POST'])
def get_routes():
    data = request.json
    source = data.get("source")
    destination = data.get("destination")
    if source not in flight_routes or destination not in flight_routes:
        return jsonify({"error": "Invalid cities selected"}), 400
    result = find_optimal_route(source, destination)
    if not result["route"]:
        return jsonify({"error": "No route found"}), 404
    refined_route, refined_cost = adjust_route_with_metta(result["route"], result["total_cost"])
    total_travel_time = calculate_total_travel_time(refined_route)
    # Calculate estimated arrival time (assuming departure time is now)
    departure_time = datetime.now()
    arrival_time = departure_time + timedelta(hours=total_travel_time)
    arrival_time_str = arrival_time.strftime("%Y-%m-%d %H:%M:%S")
    route_coords = [coordinates[city] for city in refined_route]
    return jsonify({
        "route": refined_route,
        "total_cost": refined_cost,
        "total_travel_time": total_travel_time,
        "arrival_time": arrival_time_str,
        "coordinates": route_coords
    })

if __name__ == '__main__':
    app.run(debug=True)
