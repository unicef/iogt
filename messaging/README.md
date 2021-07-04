## Running the ChatBot
1. Set the values of `RAPIDPRO_BOT_USER_USERNAME` and `RAPIDPRO_BOT_USER_PASSWORD` in settings (`local.py`)
2. Run the command `python manage.py sync_rapidpro_bot_user`
3. Running the command should return a user_id. Set the User ID in the settings (`local.py`) file `RAPIDPRO_BOT_USER_ID=...`
4. Run the command `python manage.py get_rapidpro_authentication_header_value` to get the **Authorization Header Value** for RapidPro server
5. Create channel on RapidPro Server with the **Authorization Header Value** from **step 4**