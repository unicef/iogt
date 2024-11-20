import requests
from django.template.loader import render_to_string


def send_email_via_mailjet(api_key, api_secret, from_email, from_name, to_email, to_name, subject, template_name, context):
    """
    Sends an email using the Mailjet API.

    Args:
        api_key (str): Mailjet API key.
        api_secret (str): Mailjet API secret.
        from_email (str): Sender's email address.
        from_name (str): Sender's name.
        to_email (str): Recipient's email address.
        to_name (str): Recipient's name.
        subject (str): Email subject.
        text_part (str): Plain text content of the email.
        html_part (str): HTML content of the email.

    Returns:
        dict: Response from the Mailjet API.
    """
    url = "https://api.mailjet.com/v3.1/send"
    print("hdhdhdhdddddddddddddddddddddddddddddddddddddddddd")
    # Render the template with the context

    html_content = render_to_string(template_name, context)

    try:
        html_content = render_to_string(template_name, context)
    except Exception as e:
        print(e, "((((((((((((((")
        return {"error": f"Template rendering failed: {e}"}
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "Messages": [
            {
                "From": {
                    "Email": from_email,
                    "Name": from_name,
                },
                "To": [
                    {
                        "Email": to_email,
                        "Name": to_name,
                    }
                ],
                "Subject": subject,
                "TextPart": 'Text',
                "HTMLPart": html_content,
            }
        ]
    }

    try:
        response = requests.post(
            url,
            auth=(api_key, api_secret),
            json=data,
            headers=headers,
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        print(response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print(e)
        return {"error": str(e)}