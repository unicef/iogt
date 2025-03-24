from django.conf import settings


def get_azure_auth_details():
    azure_settings = settings.SOCIALACCOUNT_PROVIDERS.get('azure', {})

    return {
        'tenant_id': azure_settings.get('AZURE_AD_TENANT_ID'),  # Example of deriving tenant ID
        'client_id': azure_settings.get('APP', {}).get('client_id'),
        'client_secret': azure_settings.get('APP', {}).get('secret'),
        'server_url': azure_settings.get('SERVER_URL'),
        'redirect_uri': azure_settings.get('REDIRECT_URI'),
        'scope': azure_settings.get('SCOPES'),
        'policy': azure_settings.get('AZURE_AD_SIGNUP_SIGNIN_POLICY'),
        'authority': azure_settings['SERVER_URL'].replace(
            '/.well-known/openid-configuration',
            ''
        ),
    }

def get_b2c_token_url():
    azure_details = get_azure_auth_details()
    tenant = azure_details['tenant_id']
    policy = azure_details['policy']
    url = f"https://{tenant}.b2clogin.com/{tenant}.onmicrosoft.com/{policy}/oauth2/v2.0/token"
    return url


def payload_for_access_token(code):
    azure_details = get_azure_auth_details()

    data = {
        'grant_type': 'authorization_code',
        'client_id': azure_details['client_id'],
        'scope': f"{azure_details['client_id']} offline_access openid",  # Request access token and refresh token
        'code': code,  # The authorization code you received after user consent
        'redirect_uri': azure_details['redirect_uri'],  # The same redirect URI as in your authorization request
        'client_secret': azure_details['client_secret'],
    }

    return data

