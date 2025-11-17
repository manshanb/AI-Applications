"""
# A2A Hotel Booking Demo with Google ADK

This project demonstrates Agent-to-Agent (A2A) communication using Google's Agent Development Kit (ADK).

## Architecture

- **Travel Host Agent** (travel_host_agent.py): Google Gemini based agent that handles user queries
- **Remote Agent** (hotel_booking_agent.py): A2A compliant hotel booking agent
- **Remote Agent** (flight_booking_agent.py): A2A compliant hotel booking agent

## Setup

1. Install dependencies:
```bash
pip install google-genai flask requests python-dotenv
```

2. Set your Google API key:
```bash
export GOOGLE_API_KEY="AIzaSyBLA8hcQnJUbfeCePaGVx40f0YDvZ"
```

## Running the Demo

### Step 1: Start the Hotel Booking Agent in a new terminal (Remote)
```bash
python hotel_booking_agent.py
```

This starts A2A compliant agent on http://localhost:5000

The agent exposes:
- Tool definitions in Google ADK format
- A2A discovery endpoint (`/agent/capabilities`)
- A2A execution endpoint (`/agent/execute`)

### Step 2: Start the Flight Booking Agent in a new terminal (Remote)
```bash
python flight_booking_agent.py
```
This starts A2A compliant agent on http://localhost:5001


The agent exposes:
- Tool definitions in Google ADK format
- A2A discovery endpoint (`/agent/capabilities`)
- A2A execution endpoint (`/agent/execute`)

### Step 3: Start the Travel Host Agent
In a new terminal:
```bash
python travel_host_agent.py
```

This starts the interactive Google ADK agent that:
1. Discovers remote agent capabilities
2. Converts remote tools to ADK format
3. Handles user queries with A2A communication

## Example Interactions

1. **Plan trips**
   - "Plan my trip to Chicago from December 1-5, 2025 for 2 guests from Bangalore"
   - "Find hotels in Chicago"
   - "Show me hotels in New York with rating above 3.5"
   - "Search for hotels under $150 per night in Frankfurt"

2. **Get details:**
   - "Tell me more about hotel ID 1"
   - "What amenities does the Grand Hyatt have?"
   - "How much flight to Frankfurt costs for 3 people?"

3. **Create a booking:**
   - "Book a room at Grand Plaza Hotel for December 1-5, 2025 for John Doe, 2 guests"
   - "I want to book a flight for 2 from Mumbai to New York on December 10, 2025"

4. **Check booking:**
   - "Check status of booking BK1000"
   - "Show me my booking details"

5. **Cancel booking:**
   - "Cancel booking BK1000"

## A2A Communication Flow

1. **Discovery Phase:**
   - Host agent calls `/agent/capabilities` on remote agent
   - Remote agent returns tool definitions in ADK format
   - Host agent converts these to ADK tools

2. **Execution Phase:**
   - User sends query to host agent
   - Host agent (Google ADK) determines which tools to use
   - Host agent calls `/agent/execute` with tool_name and parameters
   - Remote agent executes the tool and returns result
   - Host agent formulates final response to user

## Google ADK Features Used

- **Function Declarations**: Remote tools are declared as ADK functions
- **Tool Calling**: Automatic tool selection and parameter extraction
- **Multi-turn Conversations**: Chat history management
- **System Instructions**: Agent behavior and personality

## A2A Protocol

The remote agent implements Google ADK-compatible A2A protocol:

### Discovery Endpoint
```
GET /agent/capabilities
Returns: {
  "agent_name": "HotelBookingAgent",
  "tools": [...],  // ADK function declarations
  "protocol": "google-adk-a2a"
}
```

### Execution Endpoint
```
POST /agent/execute
Body: {
  "tool_name": "search_hotels",
  "parameters": {"location": "Miami"}
}
Returns: {
  "success": true,
  "result": {...}
}
```

## Project Structure

```
a2a-demo/
├── hotel_booking_agent.py    # Remote A2A agent 
├── flight_booking_agent.py    # Remote A2A agent 
├── travel_host_agent.py       # Host agent 
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Benefits of This Architecture

1. **Separation of Concerns**: Host and remote agents are independent
2. **Scalability**: Remote agent can handle multiple host agents
3. **Standardization**: Uses Google ADK tool format for interoperability
4. **Flexibility**: Easy to add more remote agents with different capabilities
"""