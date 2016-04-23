# Deploy Keys Encryption

This generates a public/private ssh keys and encrypts the private key with a
user specified password.

Run this with:

	./create_key.sh PASSWORD

Where PASSWORD is a strong password/key.

It will generate the following files:

	deploykey       # private ssh key
	deploykey.enc   # private ssh key, encrypted
	deploykey.pub   # public ssh key

Commit the `deploykey.enc`, decrypt it when needed and use it for deployment,
and put `deploykey.pub` into the repository where you want to push to.
