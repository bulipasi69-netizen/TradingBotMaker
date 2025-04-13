import requests
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse

def connect_coinbase(request):
    """
    Redirects the user to Coinbase's OAuth authorization URL.
    """
    client_id = settings.COINBASE_CLIENT_ID
    redirect_uri = settings.COINBASE_REDIRECT_URI
    # Define the scopes you need. Adjust as required.
    scope = "wallet:accounts:read"
    # Construct the Coinbase OAuth URL.
    oauth_url = (
        f"https://www.coinbase.com/oauth/authorize?"
        f"response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"
    )
    return redirect(oauth_url)

def coinbase_callback(request):
    """
    Handles the callback from Coinbase after user authorization.
    Exchanges the authorization code for an access token, then uses it
    to fetch wallet (accounts) information.
    """
    code = request.GET.get("code")
    if not code:
        return HttpResponse("Error: No code provided", status=400)

    client_id = settings.COINBASE_CLIENT_ID
    client_secret = settings.COINBASE_CLIENT_SECRET
    redirect_uri = settings.COINBASE_REDIRECT_URI
    token_url = "https://api.coinbase.com/oauth/token"

    # Prepare the data to exchange code for an access token.
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri
    }
    token_response = requests.post(token_url, data=data)
    if token_response.status_code != 200:
        return HttpResponse("Failed to get access token from Coinbase", status=token_response.status_code)

    token_data = token_response.json()
    access_token = token_data.get("access_token")
    # Optionally: Save the access token to your user profile for future API calls

    # Fetch the user's Coinbase accounts (wallets)
    accounts_url = "https://api.coinbase.com/v2/accounts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    accounts_response = requests.get(accounts_url, headers=headers)
    if accounts_response.status_code != 200:
        return HttpResponse("Failed to fetch accounts from Coinbase", status=accounts_response.status_code)

    accounts_data = accounts_response.json()
    # For now, simply return the account data as JSON.
    # In your real app, you'd link this data to the logged-in user in your database.
    return JsonResponse(accounts_data)
