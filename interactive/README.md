Users can communicate with RapidPro by creating an Interactive chatbots in IoGT.

## Create a service account in IoGT

RapidPro needs a service account within IoGT to be able to authenticate itself to IoGT and establish communication. The service account is set up within IoGT as an unprivileged user account within a specific user group. Any Wagtail Admin should be able to set up the service account manually.

- Create a new group (_Settings_ > _Groups_, _Add a group_)
  - The name must be exactly 'rapidpro_chatbot'
  - No permissions are required
- Create the service account (_Settings_ > _Users_, _Add a user_)
  - The username just has to be unique
  - Use a long and varied password (no need to remember it)
  - It is recommended to give the user a descriptive first and last name, e.g. 'RapidPro Bot'
  - Add the user to the 'rapidpro_chatbot' group (in the _Roles_ section)
- Verify everything is set up correctly, by checking that the authorization header to be used by RapidPro when authenticating to IoGT now appears in _Chatbot_ > _Chatbot Channels_.

You can now set up a channel in RapidPro, and add this channel to IoGT so you can start communicating with it.

## Setting up an Interactive Chatbot channel
1. Find the _Chatbot Authentication Header_ for the chatbot in the IoGT admin panel at _Interactive_ > _Interactive RapidPro Channels_ - displayed at the top of the page.
2. In your workspace in RapidPro, go to _Settings_ > _Add Channel_.
3. Select _External Api_.
4. Fill in the following form fields
    1. **URN Type**: External identifier
    2. **Address**: Enter a name identifying your RapidPro server, e.g. my_rapidpro_server
    3. **Method**: HTTP POST
    4. **Encoding**: Default Encoding (TODO: Confirm this)
    5. **Content type**: JSON - application/json
    6. **Max length**: 6400 (see notes: [1](#note-1), [2](#note-2))
    7. **Authorization Header Value**: Enter the _Chatbot Authentication Header_ from the IoGT admin panel _Interactive_ > _Interactive RapidPro Channels_, mentioned earlier (include the word 'Bearer' as well as the code)
    8. **Send URL**: `https://[URL of the IoGT site]/api/interactive/rapidpro-webhook/ ` where `[URL of the IoGT site]` is the URL of your IoGT site, e.g. `rw.goodinternet.org`.
    9. **Request Body**: `{"id":{{id}}, "text":{{text}}, "to":{{to}}, "to_no_plus":{{to_no_plus}}, "from":{{from}}, "from_no_plus":{{from_no_plus}}, "channel":{{channel}}, "quick_replies":{{quick_replies}}}` (TODO: Check whether we can omit the `to_no_plus` and `from_no_plus`)
    10. **MT Response check**: ok
5. Click _Submit_
6. You will land on the _External API Configuration_ page
7. Copy the _Received URL_ that is displayed on the page. This URL should look roughly like this: `https://[your RapidPro server]/c/ex/some-uuid-here-7afd839d7123-a95d/receive`
8. Go back to the IoGT admin panel, _Interactive_ > _Interactive RapidPro Channels_, _Add interactive channel_.
    1. **DISPLAY NAME**: This is the name that users will see when interacting with the interactive bot.
    2. **REQUEST URL**: Enter the _Received URL_ from step 7, immediately above.

### Notes

<a id="note-1">**1**</a> On older RapidPro installations the upper limit might only be up to 640.

<a id="note-2">**2**</a> Messages longer than the limit will be split up into multiple parts and will have to be re-joined on the IoGT side, which can cause spaces between words to be lost. Thus, larger limits are better, so we can avoid messages being split as much as possible.

## Allowing users to interact with a Chatbot
As part of an Interactive page content, you can now add an _Interactive RapidPro Chatbot button_. It has the following form fields:

- **Title**: The title identifying the conversation with the chatbot in the user's inbox.
- **Trigger string**: The initial message that will be sent to the chatbot, starting the conversation
- **Channel**: Select the channel you just created.

Upon clicking the page title, the user will be directed to the interactive page (showing the first message from RapidPro).

## Create a service account in IoGT with the management command

This is only an option for those who are operating an instance of IoGT (system administrator, ops team). The management commmand performs the manual steps for creating a service account in IoGT (detailed above) and is provided to automate the process (e.g. when an IoGT site is first created).

The setup command.
```
python manage.py sync_rapidpro_bot_user
```

There is another command that will print the authorization header to be used by RapidPro when authenticating to IoGT.
```
python manage.py get_rapidpro_authentication_header_value
```

This is the same value that appears in the IoGT admin panel under _Chatbot_ > _Chatbot channels_.
