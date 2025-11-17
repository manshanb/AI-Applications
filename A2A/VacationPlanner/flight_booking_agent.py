"""
Flight Booking Agent - A2A Compliant Remote Service using Google ADK
Run this alongside hotel_booking_agent.py: python flight_booking_agent.py
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Mock flight database
FLIGHTS = {
    "FL001": {
        "id": "FL001",
        "airline": "Luftansa",
        "flight_number": "CJ201",
        "origin": "Frankfurt",
        "destination": "Bangalore",
        "departure_time": "18:00",
        "arrival_time": "20:30",
        "price": 220,
        "available_seats": 30,
        "class": "Economy"
    },
    "FL002": {
        "id": "FL002",
        "airline": "Luftansa",
        "flight_number": "CJ202",
        "origin": "Bangalore",
        "destination": "Frankfurt",
        "departure_time": "14:00",
        "arrival_time": "17:30",
        "price": 180,
        "available_seats": 30,
        "class": "Economy"
    },
    "FL003": {
        "id": "FL003",
        "airline": "SkyHigh Airlines",
        "flight_number": "SH305",
        "origin": "Bangalore",
        "destination": "Chicago",
        "departure_time": "09:30",
        "arrival_time": "13:00",
        "price": 320,
        "available_seats": 40,
        "class": "Economy"
    },
    "FL004": {
        "id": "FL004",
        "airline": "Premier Air",
        "flight_number": "PA450",
        "origin": "Chicago",
        "destination": "Bangalore",
        "departure_time": "06:00",
        "arrival_time": "09:15",
        "price": 200,
        "available_seats": 25,
        "class": "Economy"
    },
    "FL005": {
        "id": "FL005",
        "airline": "CloudJet",
        "flight_number": "CJ678",
        "origin": "Mumbai",
        "destination": "Chicago",
        "departure_time": "15:45",
        "arrival_time": "19:30",
        "price": 290,
        "available_seats": 35,
        "class": "Economy"
    },
    "FL006": {
        "id": "FL006",
        "airline": "CloudJet",
        "flight_number": "CJ777",
        "origin": "Chicago",
        "destination": "Mumbai",
        "departure_time": "15:45",
        "arrival_time": "19:30",
        "price": 310,
        "available_seats": 35,
        "class": "Economy"
    }
}

# Mock flight bookings storage
flight_bookings = {}
flight_booking_counter = 5000


# Google ADK Tool Definitions for Flight Agent
FLIGHT_TOOL_DEFINITIONS = [
    {
        "name": "search_flights",
        "description": "Search for available flights based on origin, destination, date, and price criteria",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "Departure city"
                },
                "destination": {
                    "type": "string",
                    "description": "Arrival city"
                },
                "travel_date": {
                    "type": "string",
                    "description": "Travel date in YYYY-MM-DD format"
                },
                "max_price": {
                    "type": "number",
                    "description": "Maximum ticket price in USD"
                }
            },
            "required": ["origin", "destination"]
        }
    },
    {
        "name": "get_flight_details",
        "description": "Get detailed information about a specific flight",
        "parameters": {
            "type": "object",
            "properties": {
                "flight_id": {
                    "type": "string",
                    "description": "The unique identifier of the flight"
                }
            },
            "required": ["flight_id"]
        }
    },
    {
        "name": "book_flight",
        "description": "Book a flight ticket for a passenger",
        "parameters": {
            "type": "object",
            "properties": {
                "flight_id": {
                    "type": "string",
                    "description": "The flight ID to book"
                },
                "passenger_name": {
                    "type": "string",
                    "description": "Name of the passenger"
                },
                "travel_date": {
                    "type": "string",
                    "description": "Travel date in YYYY-MM-DD format"
                },
                "num_passengers": {
                    "type": "integer",
                    "description": "Number of passengers"
                },
                "passenger_email": {
                    "type": "string",
                    "description": "Email address for booking confirmation"
                }
            },
            "required": ["flight_id", "passenger_name", "travel_date", "num_passengers", "passenger_email"]
        }
    },
    {
        "name": "get_flight_booking_status",
        "description": "Check the status of an existing flight booking",
        "parameters": {
            "type": "object",
            "properties": {
                "booking_reference": {
                    "type": "string",
                    "description": "The flight booking reference number"
                }
            },
            "required": ["booking_reference"]
        }
    },
    {
        "name": "cancel_flight_booking",
        "description": "Cancel an existing flight booking",
        "parameters": {
            "type": "object",
            "properties": {
                "booking_reference": {
                    "type": "string",
                    "description": "The flight booking reference number to cancel"
                }
            },
            "required": ["booking_reference"]
        }
    }
]


class FlightBookingAgent:
    """A2A Compliant Flight Booking Agent with Google ADK"""
    
    def __init__(self):
        self.name = "FlightBookingAgent"
        self.version = "1.0"
        self.tools = FLIGHT_TOOL_DEFINITIONS
    
    def get_capabilities(self):
        """Return agent capabilities (A2A Discovery) - ADK Format"""
        return {
            "agent_name": self.name,
            "version": self.version,
            "tools": self.tools,
            "status": "online",
            "protocol": "google-adk-a2a"
        }
    
    def search_flights(self, origin, destination, travel_date=None, max_price=None):
        """Search for available flights"""
        results = []
        
        for flight_id, flight in FLIGHTS.items():
            match = True
            
            if origin and origin.lower() not in flight["origin"].lower():
                match = False
            if destination and destination.lower() not in flight["destination"].lower():
                match = False
            if max_price and flight["price"] > max_price:
                match = False
            
            if match and flight["available_seats"] > 0:
                results.append({
                    "flight_id": flight["id"],
                    "airline": flight["airline"],
                    "flight_number": flight["flight_number"],
                    "origin": flight["origin"],
                    "destination": flight["destination"],
                    "departure_time": flight["departure_time"],
                    "arrival_time": flight["arrival_time"],
                    "price": flight["price"],
                    "available_seats": flight["available_seats"],
                    "class": flight["class"]
                })
        
        return {
            "count": len(results),
            "flights": results,
            "travel_date": travel_date or "Not specified"
        }
    
    def get_flight_details(self, flight_id):
        """Get detailed information about a specific flight"""
        if flight_id not in FLIGHTS:
            raise ValueError(f"Flight with ID {flight_id} not found")
        
        return FLIGHTS[flight_id]
    
    def book_flight(self, flight_id, passenger_name, travel_date, num_passengers, passenger_email):
        """Book a flight"""
        global flight_booking_counter
        
        if flight_id not in FLIGHTS:
            raise ValueError(f"Flight with ID {flight_id} not found")
        
        flight = FLIGHTS[flight_id]
        
        if flight["available_seats"] < num_passengers:
            raise ValueError(f"Not enough seats available. Only {flight['available_seats']} seats left")
        
        # Validate date
        try:
            booking_date = datetime.strptime(travel_date, "%Y-%m-%d")
            if booking_date < datetime.now():
                raise ValueError("Travel date cannot be in the past")
        except ValueError as e:
            raise ValueError(f"Invalid date format or range: {str(e)}")
        
        total_cost = flight["price"] * num_passengers
        
        # Create booking
        booking_reference = f"FLT{flight_booking_counter}"
        flight_booking_counter += 1
        
        flight_bookings[booking_reference] = {
            "booking_reference": booking_reference,
            "flight_id": flight_id,
            "airline": flight["airline"],
            "flight_number": flight["flight_number"],
            "origin": flight["origin"],
            "destination": flight["destination"],
            "departure_time": flight["departure_time"],
            "arrival_time": flight["arrival_time"],
            "passenger_name": passenger_name,
            "passenger_email": passenger_email,
            "travel_date": travel_date,
            "num_passengers": num_passengers,
            "price_per_ticket": flight["price"],
            "total_cost": total_cost,
            "status": "confirmed",
            "booked_at": datetime.now().isoformat()
        }
        
        # Update available seats
        FLIGHTS[flight_id]["available_seats"] -= num_passengers
        
        return flight_bookings[booking_reference]
    
    def get_flight_booking_status(self, booking_reference):
        """Get status of a flight booking"""
        if booking_reference not in flight_bookings:
            raise ValueError(f"Booking {booking_reference} not found")
        
        return flight_bookings[booking_reference]
    
    def cancel_flight_booking(self, booking_reference):
        """Cancel a flight booking"""
        if booking_reference not in flight_bookings:
            raise ValueError(f"Booking {booking_reference} not found")
        
        booking = flight_bookings[booking_reference]
        
        if booking["status"] == "cancelled":
            raise ValueError("Booking already cancelled")
        
        # Update booking status
        booking["status"] = "cancelled"
        
        # Restore seat availability
        flight_id = booking["flight_id"]
        FLIGHTS[flight_id]["available_seats"] += booking["num_passengers"]
        
        return booking
    
    def execute_tool(self, tool_name, parameters):
        """Execute a tool and return result (ADK Format)"""
        try:
            if tool_name == "search_flights":
                result = self.search_flights(**parameters)
            elif tool_name == "get_flight_details":
                result = self.get_flight_details(**parameters)
            elif tool_name == "book_flight":
                result = self.book_flight(**parameters)
            elif tool_name == "get_flight_booking_status":
                result = self.get_flight_booking_status(**parameters)
            elif tool_name == "cancel_flight_booking":
                result = self.cancel_flight_booking(**parameters)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Initialize agent
flight_agent = FlightBookingAgent()


# A2A API Endpoints (Google ADK Compatible)
@app.route('/agent/capabilities', methods=['GET'])
def capabilities():
    """A2A Discovery endpoint - returns available tools in ADK format"""
    return jsonify(flight_agent.get_capabilities())


@app.route('/agent/execute', methods=['POST'])
def execute():
    """A2A Execute endpoint - ADK tool execution format"""
    data = request.json
    tool_name = data.get('tool_name')
    parameters = data.get('parameters', {})
    
    result = flight_agent.execute_tool(tool_name, parameters)

    print("\n---------------------------------------------------------")
    print(f"[FlightBookingAgent] Received A2A request:")
    print(f"  Tool: {tool_name}")
    print(f"  Parameters: {parameters}")
    print("\nResult:")
    print(result['result'])
    print("---------------------------------------------------------\n")
    
    print(f"[FlightBookingAgent] Response: {'Success' if result['success'] else 'Error'}")
    return jsonify(result)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "agent": flight_agent.name})


if __name__ == '__main__':
    print("="*70)
    print("Flight Booking Agent (A2A Remote Service - Google ADK)")
    print("="*70)
    print(f"Agent: {flight_agent.name}")
    print(f"Tools: {len(flight_agent.tools)}")
    for tool in flight_agent.tools:
        print(f"  - {tool['name']}")
    print("\nStarting server on http://localhost:5001")
    print("="*70)
    app.run(host='0.0.0.0', port=5001, debug=True)
