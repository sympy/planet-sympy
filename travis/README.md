# Travis File Encryption

This generates a public/private ssh keys and encrypts the private key with the Travis key (that only Travis can decrypt).

Run this with:

	./create_key.sh GH_TOKEN DEPLOY_TOKEN

Where GH_TOKEN is your personal github token (select these scopes: repo, user).
I don't know why Travis needs to login to your GitHub, but it doesn't store the
token anywhere. The DEPLOY_TOKEN is a random password, that will be used to
encrypt the private key.

If it runs successfully, it will generate the following files:

	travisdeploykey       # private ssh key
	travisdeploykey.enc   # private ssh key, encrypted
	travisdeploykey.pub   # public ssh key

It will also print a line of the type:

	openssl aes-256-cbc -K $encrypted_HASH_key -iv $encrypted_HASH_iv -in travisdeploykey.enc -out data/travisdeploykey -d

Which you can put into the `.travis.yml` file. Commit the
`travisdeploykey.enc`, and put `travisdeploykey.pub` into the repository where
you want to push to.
