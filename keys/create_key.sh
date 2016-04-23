#! /bin/bash

set -e
set -x

secret_password=$1

echo -e  'y\n' | ssh-keygen -P "" -f deploykey
openssl aes-256-cbc -k ${secret_password} -in deploykey -out deploykey.enc

# This example shows how to decrypt it:
#openssl aes-256-cbc -k ${secret_password} -in deploykey.enc -out deploykey2 -d
