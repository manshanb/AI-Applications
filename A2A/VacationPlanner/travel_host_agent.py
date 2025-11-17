"""
Travel Host Agent - Uses Google ADK with A2A Communication
Run this after starting hotel_booking_agent.py: python travel_host_agent.py
"""

import os
import requests
from google import genai
from google.genai import types

# Set your API key
# os.environ["GOOGLE_API_KEY"] = "your-google-api-key-here"

# Remote agent URLs
HOTEL_AGENT_URL = "http://localhost:5000"
FLIGHT_AGENT_URL = "http://localhost:5001"


class A2AHotelClient:
    """Client for communicating with remote Hotel Booking Agent via A2A"""
    
    def __init__(self, agent_url):
        self.agent_url = agent_url
        self.capabilities = None
        self._discover_agent()
    
    def _discover_agent(self):
        """Discover remote agent capabilities (A2A Discovery)"""
        try:
            response = requests.get(f"{self.agent_url}/agent/capabilities", timeout=5)
            if response.status_code == 200:
                self.capabilities = response.json()
                print(f"✓ Connected to {self.capabilities['agent_name']}")
                print(f"  Protocol: {self.capabilities.get('protocol', 'unknown')}")
                print(f"  Available tools: {len(self.capabilities['tools'])}")
                for tool in self.capabilities['tools']:
                    print(f"    - {tool['name']}")
            else:
                print(f"⚠ Agent discovery failed")
        except Exception as e:
            print(f"✗ Cannot connect to Hotel Booking Agent: {e}")
            print(f"  Make sure hotel_booking_agent.py is running on {self.agent_url}")
    
    def call_tool(self, tool_name, parameters):
        """Call a tool on the remote agent (A2A Communication)"""
        try:
            response = requests.post(
                f"{self.agent_url}/agent/execute",
                json={"tool_name": tool_name, "parameters": parameters},
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to communicate with hotel agent: {str(e)}"
            }
    
    def get_adk_tools(self):
        """Convert remote agent capabilities to Google ADK tool declarations"""
        if not self.capabilities or 'tools' not in self.capabilities:
            return []
        
        # Convert remote tools to ADK format
        adk_tools = []
        for tool in self.capabilities['tools']:
            adk_tool = types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name=tool['name'],
                        description=tool['description'],
                        parameters=tool['parameters']
                    )
                ]
            )
            adk_tools.append(adk_tool)
        
        return adk_tools


def create_travel_agent():
    """Create the Google ADK agent with hotel and flight booking tools"""
    
    # Initialize Google ADK client
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
    
    # Initialize A2A clients for both agents
    hotel_client = A2AHotelClient(HOTEL_AGENT_URL)
    flight_client = A2AHotelClient(FLIGHT_AGENT_URL)  # Reusing the same client class
    
    # Get tools from both remote agents
    hotel_tools = hotel_client.get_adk_tools()
    flight_tools = flight_client.get_adk_tools()
    
    all_tools = hotel_tools + flight_tools
    
    if not all_tools:
        print("⚠ Warning: No tools discovered from remote agents")
        return None, None, None, None
    
    print(f"✓ Loaded {len(hotel_tools)} hotel tools and {len(flight_tools)} flight tools")
    
    # Create agent config
    config = types.GenerateContentConfig(
        system_instruction="""You are a helpful travel assistant that can help users search for and book hotels AND flights.

You have access to two A2A (Agent-to-Agent) services:
1. Hotel Booking Service - for searching and booking hotels
2. Flight Booking Service - for searching and booking flights

When helping users:

For Hotels:
- Search for hotels based on location, price, and rating
- Provide detailed hotel information
- Create hotel bookings with guest information and dates
- Check hotel booking status
- Cancel hotel bookings
- If year is not provided in the given dates, use current year 2025

For Flights:
- Search for flights based on origin, destination, date, and price
- Provide detailed flight information
- Book flight tickets with passenger information
- Check flight booking status
- Cancel flight bookings
- If year is not provided in the given dates, use current year 2025

Always be conversational, helpful, and confirm important details such as first name and email before making bookings.
Use dates in YYYY-MM-DD format for all bookings. If year is not provided in the given dates, use 2025 as year.
When users ask about travel, consider suggesting both flight and hotel options.""",
        tools=all_tools,
        temperature=0.7
    )
    
    return client, hotel_client, flight_client, config


def handle_tool_calls(tool_calls, hotel_client, flight_client):
    """Handle tool calls by forwarding them to the appropriate remote agent"""
    responses = []
    
    for tool_call in tool_calls:
        function_name = tool_call.name
        function_args = tool_call.args
        print('-------------------------------------------------------------')
        print(f"\n[Host Agent] Calling remote tool: {function_name}")
        print(f"  Parameters: {function_args}")
        agentName = ''
        # Route to appropriate agent based on tool name
        if function_name.startswith('search_hotels') or function_name.startswith('get_hotel') or \
           function_name.startswith('create_booking') or function_name.startswith('get_booking') or \
           function_name.startswith('cancel_booking'):
            # Hotel agent
            agentName = 'Hotel Agent'
            result = hotel_client.call_tool(function_name, function_args)
        elif function_name.startswith('search_flights') or function_name.startswith('get_flight') or \
             function_name.startswith('book_flight') or function_name.startswith('cancel_flight'):
            # Flight agent
            agentName = 'Flight Agent'
            result = flight_client.call_tool(function_name, function_args)
        else:
            result = {
                "success": False,
                "error": f"Unknown tool: {function_name}"
            }
        
        if result.get('success'):
            response_data = result['result']
            print(f"\n********* Response from '{agentName}' : {function_name} ******************** \n")
            print(f"  ✓ Success: {response_data}")
            print('-------------------------------------------------------------\n')
        else:
            response_data = {"error": result.get('error', 'Unknown error')}
            print(f"  ✗ Error: {response_data}")
        
        # Create tool response
        responses.append(
            types.Part.from_function_response(
                name=function_name,
                response=response_data
            )
        )
    
    return responses


def chat_loop(client, hotel_client, flight_client, config):
    """Interactive chat loop with the agent"""
    
    print("\n" + "="*70)
    print("Travel Assistant Ready!")
    print("="*70)
    # print("\nExample queries:")
    # print("  HOTELS:")
    # print("    - Find hotels in Miami under $200 per night")
    # print("    - Book a room at the Grand Plaza Hotel for December 1-5")
    # print("  FLIGHTS:")
    # print("    - Search for flights from New York to Miami")
    # print("    - Book a flight from Chicago to Denver on 2025-12-15")
    # print("  COMBINED:")
    # print("    - Plan a trip to Miami (I'll suggest both flights and hotels)")
    print("\nType 'quit' to exit\n")
    
    # Initialize chat history
    chat_history = []
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            # Add user message to history
            chat_history.append(types.Content(
                role="user",
                parts=[types.Part(text=user_input)]
            ))
            
            # Generate response
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=chat_history,
                config=config
            )
            
            # Process response
            while True:
                # Check if there are tool calls
                if response.candidates[0].content.parts:
                    first_part = response.candidates[0].content.parts[0]
                    
                    if hasattr(first_part, 'function_call') and first_part.function_call:
                        # Extract all function calls from parts
                        tool_calls = []
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, 'function_call') and part.function_call:
                                tool_calls.append(part.function_call)
                        
                        if tool_calls:
                            # Add assistant's tool calls to history
                            chat_history.append(response.candidates[0].content)
                            
                            # Handle tool calls via A2A
                            tool_responses = handle_tool_calls(tool_calls, hotel_client, flight_client)
                            
                            # Add tool responses to history
                            chat_history.append(types.Content(
                                role="user",
                                parts=tool_responses
                            ))
                            
                            # Generate next response with tool results
                            response = client.models.generate_content(
                                model="gemini-2.0-flash-exp",
                                contents=chat_history,
                                config=config
                            )
                            continue
                
                # No more tool calls, show final response
                final_text = response.text
                print(f"\nAgent: {final_text}")
                
                # Add assistant response to history
                chat_history.append(types.Content(
                    role="model",
                    parts=[types.Part(text=final_text)]
                ))
                break
                
        except Exception as e:
            print(f"\nError: {str(e)}")
            # Remove the last user message if there was an error
            if chat_history and chat_history[-1].role == "user":
                chat_history.pop()


def main():
    """Run the travel host agent"""
    print("="*70)
    print("Travel Host Agent with Google ADK - A2A Communication")
    print("Multi-Agent System: Hotels + Flights")
    print("="*70)
    print("\nInitializing agent...")
    
    result = create_travel_agent()
    if result is None or None in result:
        print("Failed to initialize agent. Exiting.")
        return
    
    client, hotel_client, flight_client, config = result
    
    print("\n✓ Agent ready!")
    
    # Start chat loop
    chat_loop(client, hotel_client, flight_client, config)


if __name__ == "__main__":
    main()
