import requests

# Define the URI
uri = "http://kinetic-release-testing.q-free-asa.net/maxtime-12/maxtime/api/mibs"

# Define the payload for the POST request
pattern_on = {1: 0}
post_on = {
    'data': [
        {'name': 'vehicleDetectorControlGroupActuation', 'data': pattern_on}
    ],
    'noChangeLog': True,
    'username': 'Admin'
}

# Create a session
with requests.Session() as session:
    try:
        # Make the POST request
        response = session.post(uri, json=post_on)
        # Print the response
        print(response.status_code)
        print(response.json())  # Or response.text if you expect a non-JSON response
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the request
        print(f"An error occurred: {e}")
# inputPointGroupControl-1
#vehicleDetectorControlGroupActuation-2