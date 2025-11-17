"""
Hotel Booking Agent - A2A Compliant Remote Service using Google ADK
Run this first: python hotel_booking_agent.py
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

# Mock hotel database
HOTELS = {
    "1": {
        "id": "1",
        "name": "Marriott",
        "location": "Frankfurt",
        "price_per_night": 250,
        "available_rooms": 5,
        "rating": 4.5,
        "amenities": ["WiFi", "Pool", "Gym", "Restaurant"]
    },
    "2": {
        "id": "2",
        "name": "Hyatt Residency",
        "location": "Chicago",
        "price_per_night": 180,
        "available_rooms": 10,
        "rating": 4.2,
        "amenities": ["WiFi", "Beach Access", "Pool", "Bar"]
    },
    "3": {
        "id": "3",
        "name": "Grand Hyatt",
        "location": "New York",
        "price_per_night": 150,
        "available_rooms": 8,
        "rating": 4.7,
        "amenities": ["WiFi", "Hiking Trails", "Restaurant", "Spa"]
    },
    "4": {
        "id": "4",
        "name": "Holiday Inn",
        "location": "Frankfurt",
        "price_per_night": 120,
        "available_rooms": 15,
        "rating": 4.0,
        "amenities": ["WiFi", "Breakfast", "Parking"]
    },
    "5": {
        "id": "5",
        "name": "Marriott",
        "location": "Chicago",
        "price_per_night": 165,
        "available_rooms": 25,
        "rating": 4.2,
        "amenities": ["WiFi", "Breakfast"]
    }
}

# Mock bookings storage
bookings = {}
booking_counter = 1000


# Google ADK Tool Definitions
TOOL_DEFINITIONS = [
    {
        "name": "search_hotels",
        "description": "Search for available hotels based on location, price, and rating criteria",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City or location to search for hotels"
                },
                "max_price": {
                    "type": "number",
                    "description": "Maximum price per night in USD"
                },
                "min_rating": {
                    "type": "number",
                    "description": "Minimum hotel rating (0-5)"
                }
            }
        }
    },
    {
        "name": "get_hotel_details",
        "description": "Get detailed information about a specific hotel",
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {
                    "type": "string",
                    "description": "The unique identifier of the hotel"
                }
            },
            "required": ["hotel_id"]
        }
    },
    {
        "name": "create_booking",
        "description": "Create a new hotel booking reservation",
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {
                    "type": "string",
                    "description": "The hotel ID to book"
                },
                "guest_name": {
                    "type": "string",
                    "description": "Name of the guest"
                },
                "check_in": {
                    "type": "string",
                    "description": "Check-in date in YYYY-MM-DD format"
                },
                "check_out": {
                    "type": "string",
                    "description": "Check-out date in YYYY-MM-DD format"
                },
                "num_guests": {
                    "type": "integer",
                    "description": "Number of guests"
                }
            },
            "required": ["hotel_id", "guest_name", "check_in", "check_out", "num_guests"]
        }
    },
    {
        "name": "get_booking_status",
        "description": "Check the status of an existing booking",
        "parameters": {
            "type": "object",
            "properties": {
                "booking_id": {
                    "type": "string",
                    "description": "The booking confirmation ID"
                }
            },
            "required": ["booking_id"]
        }
    },
    {
        "name": "cancel_booking",
        "description": "Cancel an existing hotel booking",
        "parameters": {
            "type": "object",
            "properties": {
                "booking_id": {
                    "type": "string",
                    "description": "The booking confirmation ID to cancel"
                }
            },
            "required": ["booking_id"]
        }
    }
]


class HotelBookingAgent:
    """A2A Compliant Hotel Booking Agent with Google ADK"""
    
    def __init__(self):
        self.name = "HotelBookingAgent"
        self.version = "1.0"
        self.tools = TOOL_DEFINITIONS
    
    def get_capabilities(self):
        """Return agent capabilities (A2A Discovery) - ADK Format"""
        return {
            "agent_name": self.name,
            "version": self.version,
            "tools": self.tools,
            "status": "online",
            "protocol": "google-adk-a2a"
        }
    
    def search_hotels(self, location=None, max_price=None, min_rating=None):
        """Search for available hotels"""
        results = []
        
        for hotel_id, hotel in HOTELS.items():
            match = True
            
            if location and location.lower() not in hotel["location"].lower():
                match = False
            if max_price and hotel["price_per_night"] > max_price:
                match = False
            if min_rating and hotel["rating"] < min_rating:
                match = False
            
            if match and hotel["available_rooms"] > 0:
                results.append({
                    "hotel_id": hotel["id"],
                    "name": hotel["name"],
                    "location": hotel["location"],
                    "price_per_night": hotel["price_per_night"],
                    "available_rooms": hotel["available_rooms"],
                    "rating": hotel["rating"],
                    "amenities": hotel["amenities"]
                })
        
        return {
            "count": len(results),
            "hotels": results
        }
    
    def get_hotel_details(self, hotel_id):
        """Get detailed information about a specific hotel"""
        if hotel_id not in HOTELS:
            raise ValueError(f"Hotel with ID {hotel_id} not found")
        
        return HOTELS[hotel_id]
    
    def create_booking(self, hotel_id, guest_name, check_in, check_out, num_guests):
        """Create a new hotel booking"""
        global booking_counter
        
        if hotel_id not in HOTELS:
            raise ValueError(f"Hotel with ID {hotel_id} not found")
        
        hotel = HOTELS[hotel_id]
        
        if hotel["available_rooms"] < 1:
            raise ValueError("No rooms available")
        
        # Calculate nights and total cost
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
            nights = (check_out_date - check_in_date).days
            
            if nights <= 0:
                raise ValueError("Check-out must be after check-in")
        except ValueError as e:
            raise ValueError(f"Invalid date format or range: {str(e)}")
        
        total_cost = hotel["price_per_night"] * nights
        
        # Create booking
        booking_id = f"BK{booking_counter}"
        booking_counter += 1
        
        bookings[booking_id] = {
            "booking_id": booking_id,
            "hotel_id": hotel_id,
            "hotel_name": hotel["name"],
            "guest_name": guest_name,
            "check_in": check_in,
            "check_out": check_out,
            "num_guests": num_guests,
            "nights": nights,
            "price_per_night": hotel["price_per_night"],
            "total_cost": total_cost,
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        # Update available rooms
        HOTELS[hotel_id]["available_rooms"] -= 1
        
        return bookings[booking_id]
    
    def get_booking_status(self, booking_id):
        """Get status of a booking"""
        if booking_id not in bookings:
            raise ValueError(f"Booking {booking_id} not found")
        
        return bookings[booking_id]
    
    def cancel_booking(self, booking_id):
        """Cancel a booking"""
        if booking_id not in bookings:
            raise ValueError(f"Booking {booking_id} not found")
        
        booking = bookings[booking_id]
        
        if booking["status"] == "cancelled":
            raise ValueError("Booking already cancelled")
        
        # Update booking status
        booking["status"] = "cancelled"
        
        # Restore room availability
        hotel_id = booking["hotel_id"]
        HOTELS[hotel_id]["available_rooms"] += 1
        
        return booking
    
    def execute_tool(self, tool_name, parameters):
        """Execute a tool and return result (ADK Format)"""
        try:
            if tool_name == "search_hotels":
                result = self.search_hotels(**parameters)
            elif tool_name == "get_hotel_details":
                result = self.get_hotel_details(**parameters)
            elif tool_name == "create_booking":
                result = self.create_booking(**parameters)
            elif tool_name == "get_booking_status":
                result = self.get_booking_status(**parameters)
            elif tool_name == "cancel_booking":
                result = self.cancel_booking(**parameters)
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
agent = HotelBookingAgent()


# A2A API Endpoints (Google ADK Compatible)
@app.route('/agent/capabilities', methods=['GET'])
def capabilities():
    """A2A Discovery endpoint - returns available tools in ADK format"""
    return jsonify(agent.get_capabilities())


@app.route('/agent/execute', methods=['POST'])
def execute():
    """A2A Execute endpoint - ADK tool execution format"""
    data = request.json
    tool_name = data.get('tool_name')
    parameters = data.get('parameters', {})

    result = agent.execute_tool(tool_name, parameters)

    print("\n---------------------------------------------------------")
    print(f"[HotelBookingAgent] Received A2A request:")
    print(f"  Tool: {tool_name}")
    print(f"  Parameters: {parameters}")
    print("\nResult:")
    print(result['result'])
    print("---------------------------------------------------------\n")

    print(f"[HotelBookingAgent] Response: {'Success' if result['success'] else 'Error'}")
    return jsonify(result)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "agent": agent.name})


if __name__ == '__main__':
    print("="*70)
    print("Hotel Booking Agent (A2A Remote Service - Google ADK)")
    print("="*70)
    print(f"Agent: {agent.name}")
    print(f"Tools: {len(agent.tools)}")
    for tool in agent.tools:
        print(f"  - {tool['name']}")
    print("\nStarting server on http://localhost:5000")
    print("="*70)
    app.run(host='0.0.0.0', port=5000, debug=True)
