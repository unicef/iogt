In order to communicate with the IoGT website, RapidPro needs an IoGT user account as which it can authenticate.
This user needs to be set up on the IoGT side. Once that is done, you can set up a channel on your RapidPro server,
and add this channel to the IoGT site so you can start communicating with it.

## Setting up the ChatBot user
1. Set the values of `RAPIDPRO_BOT_USER_USERNAME` and `RAPIDPRO_BOT_USER_PASSWORD` in settings (`local.py`)
2. Run the command `python manage.py sync_rapidpro_bot_user`
3. Running the command should return a user_id. Set the User ID in the settings (`local.py`) file `RAPIDPRO_BOT_USER_ID=...`
4. Run the command `python manage.py get_rapidpro_authentication_header_value` to get the **Authorization Header Value** for RapidPro server

## Setting up a Chatbot channel
5. Create channel on RapidPro Server with the **Authorization Header Value** from **step 4** (for more details, see https://github.com/unicef/iogt/pull/116). As MT Response check, enter _ok_
6. In the IoGT website, create a ChatbotChannel entry in the corresponding DB table (e.g. using the django-admin interface).
This requires a request_url, which is the "Received URL" you got when submitting the channel form in RapidPro.
7. As part of an article, you can now add a **Chatbot button**.
