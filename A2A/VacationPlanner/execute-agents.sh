CUR_DIR=$(pwd)
GOOGLE_API_KEY=AIzaSyC22yEKXqwCeUeP6-9paQTapIXVozcV

osascript -e "tell application \"Terminal\" to do script \"cd '${CUR_DIR}'; export GOOGLE_API_KEY=${GOOGLE_API_KEY}; python hotel_booking_agent.py\""
osascript -e "tell application \"Terminal\" to do script \"cd '${CUR_DIR}'; export GOOGLE_API_KEY=${GOOGLE_API_KEY}; python flight_booking_agent.py\""
osascript -e "tell application \"Terminal\" to do script \"cd '${CUR_DIR}'; export GOOGLE_API_KEY=${GOOGLE_API_KEY}; python travel_host_agent.py\""
