# Notifications

The IoGT notification system relies on the [Web Push Protocol][1] to ensure the delivery of messages to users. In order to authenticate itself to a Push Service, every deployment of IoGT must generate its own public-private key pair for use with [VAPID][3].

To enable notifications in IoGT the following steps must be performed:

- Generate VAPID keys
- Set required settings (as environment variables)

# Generate VAPID keys

## Using openssl

This method guarantees that the private key remains secret (unless you expose it) and should be suitable for production deployments.

```
openssl ecparam -genkey -name prime256v1 -out private_key.pem
openssl ec -in private_key.pem -pubout -outform DER | tail -c 65 | base64 | tr -d '=' | tr '/+' '_-' >> public_key.txt
openssl ec -in private_key.pem -outform DER | tail -c +8 | head -c 32 | base64 | tr -d '=' | tr '/+' '_-' >> private_key.txt
```

The public and private keys will be written as plaintext to `public_key.txt` and `private_key.txt`, respectively.

## Using online generators

This method is more convenient, especially if openssl is not available, however, it is *not* recommended for production deployments.

- Go to [Web Push Codelab][2].
- Copy the public and private keys directly from the page.

# Set required settings

The notification feature requires several settings, and the easiest way to set them is to provide them to the app as environment variables.

- `VAPID_PUBLIC_KEY`: the VAPID public key in plaintext
- `VAPID_PRIVATE_KEY`: the VAPID private key in plaintext
- `VAPID_ADMIN_EMAIL`: the email address of a person/team responsible for hosting the IoGT application e.g. system administrator

It’s best if `VAPID_ADMIN_EMAIL` is not a personal email address, but rather a group email so that if a person leaves an organization, is unavailable for an extended period, or otherwise can’t respond, someone else on the list can. A Push Service provider may use this to contact you if there is a problem between the app and the push service.


[1]: https://web.dev/push-notifications-web-push-protocol/
[2]: https://web-push-codelab.glitch.me
[3]: https://datatracker.ietf.org/doc/html/draft-thomson-webpush-vapid
