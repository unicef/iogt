## Notifications

- Notifications rely on [VAPID](https://web.dev/push-notifications-web-push-protocol/) keys
- You can generate these keys using `openssl` as follows
  ```
  $ openssl ecparam -genkey -name prime256v1 -out private_key.pem
  $ openssl ec -in private_key.pem -pubout -outform DER|tail -c 65|base64|tr -d '=' |tr '/+' '_-' >> public_key.txt
  $ openssl ec -in private_key.pem -outform DER|tail -c +8|head -c 32|base64|tr -d '=' |tr '/+' '_-' >> private_key.txt
  ```
- Set `VAPID_PUBLIC_KEY` env. variable from `public_key.txt`
- Set `VAPID_PRIVATE_KEY` env. variable from `private_key.txt`
- Set `VAPID_ADMIN_EMAIL` env. variables accordingly
  - It’s best if this email is not a personal email address, but rather a group email so that if a person leaves an organization, is unavailable for an extended period, or otherwise can’t respond, someone else on the list can. Push Notification Service Provider will only use this if we notice a problem with your feed and need to contact you.
