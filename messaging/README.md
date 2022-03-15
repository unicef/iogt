Users can communicate to RapidPro chatbots in IoGT v2. If you are a content creator on an IoGT site, the technical setup on the IoGT server should have been done, and you can set up a chatbot channel. For completeness, the technical setup is outlined at the bottom, but it should not concern content creators.

## Setting up a Chatbot channel
1. Find the **Authorization Header Value** for the chatbot on your site by navigating in the Admin Panel to Chatbot > Chatbot Channels. It will be displayed at the top.
2. Log in to your workspace on your RapidPro Server. Click Settings > Add Channel
3. Select "External Api"
4. Fill in the following form fields
    1. URN Type: External identifier
    2. Address: Enter a name identifying your RapidPro server, e.g. my_rapidpro_server
    3. Method: HTTP POST
    4. Encoding: Default Encoding (TODO: Confirm this)
    5. Content type: JSON - application/json
    6. Max length: `6400` (on older RapidPro installations the upper allowed limit might be only `640`). Note: Messages longer than this size will be split up into multiple parts, and on the IoGT side we have to stitch them back together, which can cause spaces between words to be lost. Thus, the larger this value, the better, so we can avoid messages getting split as much as possible.
    7. Authorization Header Value: Enter the **Authorization Header Value** from the IoGT Admin Panel > Chatbot > Chatbot Channels mentioned earlier. (Make sure to include the word `Basic` that is displayed, not only the code.)
    8. Send URL: This should be `https://[URL of the IoGT site]/messaging/api/rapidpro-webhook/` where `[URL of the IoGT site]` is the URL of your IoGT site, e.g. `rw.goodinternet.org`.
    9. Request Body: `{"id":{{id}}, "text":{{text}}, "to":{{to}}, "to_no_plus":{{to_no_plus}}, "from":{{from}}, "from_no_plus":{{from_no_plus}}, "channel":{{channel}}, "quick_replies":{{quick_replies}}}` (TODO: Check whether we can omit the `to_no_plus` and `from_no_plus`)
    10. MT Response check: `ok`
5. Click _Submit_
6. You will land on a page _External API Configuration_
7. Copy the _Received URL_ that is displayed on the page. This URL should look roughly like this: `https://[your RapidPro server]/c/ex/some-uuid-here-7afd839d7123-a95d/receive`
8. Go back to the IoGT Admin Panel > Chatbot > Chatbot. Create a new channel.
    1. DISPLAY NAME: This is the name that users will see when interacting with the bot.
    2. REQUEST URL: Enter the _Received URL_ from **step 7** here

## Allowing users to interact with a Chatbot
As part of an article's content, you can now add a _Chatbut button_. It has the following form fields:

1. Subject: The title identifiying the conversation with the chatbot in the user's inbox.
2. Button text: The text to be displayed on the button
3. Trigger string: The initial message that will be sent to the chatbot, starting the conversation
4. Channel: Select the channel that you just created.

Upon clicking the button, the user will be directed to a conversation view with the chatbot.

The inbox view can be accessed via the URL `https://[URL of the IoGT site]/messaging/inbox/`. To allow users to resume conversations later, you can e.g. create a flat menu entry (Admin Panel > Settings > Flat Menus) linking to this inbox view, or to an article explaining about the chatbot that also has a link to the inbox.

## Technical set up

In order to communicate with the IoGT website, RapidPro needs an IoGT user account as which it can authenticate.
This user needs to be set up on the IoGT side. Once that is done, you can set up a channel on your RapidPro server,
and add this channel to the IoGT site so you can start communicating with it.

1. Run the command `python manage.py sync_rapidpro_bot_user` in django container (to go inside django container run `make ssh`)
2. Optional: Run the command `python manage.py get_rapidpro_authentication_header_value` in django container to get the **Authorization Header Value** for RapidPro server. (This value should also be displayed in the admin panel.)
