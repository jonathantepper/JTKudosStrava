import requests
import os
import sys

# CONFIGURATION
# Sip Logic: Only kudos this many people per run to avoid rate limits
MAX_KUDOS_PER_RUN = 25 
auth_url = "https://www.strava.com/oauth/token"
activites_url = "https://www.strava.com/api/v3/activities/following"
kudos_base_url = "https://www.strava.com/api/v3/activities"

def get_access_token():
    """Exchanges the refresh token for a temporary access token."""
    payload = {
        'client_id': os.environ['STRAVA_CLIENT_ID'],
        'client_secret': os.environ['STRAVA_CLIENT_SECRET'],
        'refresh_token': os.environ['STRAVA_REFRESH_TOKEN'],
        'grant_type': 'refresh_token',
        'f': 'json'
    }
    
    res = requests.post(auth_url, data=payload)
    if res.status_code != 200:
        print(f"Error getting token: {res.text}")
        sys.exit(1)
    return res.json()['access_token']

def give_kudos():
    token = get_access_token()
    headers = {'Authorization': f"Bearer {token}"}
    
    # Get recent feed (default is 30 items)
    print("Fetching recent activities...")
    res = requests.get(activites_url, headers=headers)
    
    if res.status_code != 200:
        print(f"Error fetching feed: {res.text}")
        return

    activities = res.json()
    kudos_count = 0

    for activity in activities:
        if kudos_count >= MAX_KUDOS_PER_RUN:
            print("Sip limit reached. Stopping for now.")
            break
        
        # Check if we already liked it
        if not activity['has_kudoed']:
            id = activity['id']
            # Attempt to Kudos
            kudo_res = requests.post(f"{kudos_base_url}/{id}/kudos", headers=headers)
            
            if kudo_res.status_code == 200:
                print(f"Gave kudos to {activity['athlete']['firstname']} for activity {id}")
                kudos_count += 1
            else:
                print(f"Failed to kudos {id}: {kudo_res.status_code}")
        else:
            # print(f"Already liked activity {activity['id']}")
            pass
            
    print(f"Run complete. Total Kudos given: {kudos_count}")

if __name__ == "__main__":
    give_kudos()
