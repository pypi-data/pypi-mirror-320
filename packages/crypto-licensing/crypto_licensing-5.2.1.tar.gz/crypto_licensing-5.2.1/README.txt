           ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
             CRYPTOGRAPHICALLY SIGNED LICENSE ISSUANCE WITH
                       PAYMENT IN CRYPTOCURRENCY

                             Perry Kundert
           ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


                          2022-01-25 12:32:00


Licensing software and getting paid for it has become extremely
difficult, due to government, regulatory and banking interference.

The `crypto-licensing' Python module allows you automatically and
securely issue licenses, and get paid in various cryptocurrencies.

Table of Contents
─────────────────

1. Software Licensing Using Ed25519 Signatures
.. 1. Issuing Licenses: Your Authoring (Signing) Key
..... 1. `crypto_licensing.authoring': Create an Authoring Keypair in Python
..... 2. `crypto_licensing registered': Load or Create an Authoring Keypair
.. 2. Creating a License: Grants
..... 1. Verifiable Data
..... 2. `issue': Signing a License
..... 3. `verify': Confirm License (and sub-License) Validity
.. 3. Using Licenses
..... 1. `load_keys': Find all Ed25519 Signing Keys
..... 2. `load': Find all Licenses
..... 3. `check': Find all Keys and Valid Licenses
.. 4. Running A `crypto_licensing.licensing' Server
2. Payment with Cryptocurrencies
3. Issuance via Web API


1 Software Licensing Using Ed25519 Signatures
═════════════════════════════════════════════

  Providing software to a client usually includes more than just the
  code; you need a way to configure the software for each client's
  licensed set of capabilities.

  The `crypto_licensing' module provides a way to securely transmit some
  authorizations or configurations specific to each client.

  These configurations are signed using Ed25519 Public/Private keys, and
  are shipped to the client either with the software, or separately, for
  example via email, after a standard online purchase.

  Your organization's or product's Authoring public key is online (using
  the same model as for email's DKIM signature checking), so your
  software can *verify* the License in the field, by securely accessing
  DNS `TXT' records from your organization's domain, and checking the
  License' signature.

  Your software can also sign and save this verification for later runs,
  so it can be assured that the License has been verified – even if the
  software is not normally "online".  Your software just has to have
  access to the Internet /once/, after the new License is installed, to
  verify the License and remember its decision.


1.1 Issuing Licenses: Your Authoring (Signing) Key
──────────────────────────────────────────────────

  To begin authoring Licenses, you need to be able to sign them; you
  need to create and save an encrypted Ed25519 keypair, so you (and only
  you) can obtain it later to sign new Licenses.

  The public key `dqFZIESm5PURJlvKc6YE2QsFKdHfYCvjChmpJXZg0fU=' (related
  to the private key consisting of all `1' bits) may be created via the
  API or CLI.  It should be stored securely, so a `KeypairEncrypted'
  might be appropriate.  Both the `KeypairPlaintext' and
  `KeypairEncrypted' contain the public "verifying" key `.vk'.  The
  `KeypairEncrypted' also contains a `.vk_signature', proving that the
  `.vk' was signed by the corresponding private key at the time of
  creation.


1.1.1 `crypto_licensing.authoring': Create an Authoring Keypair in Python
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

  The raw `ed25519.Keypair' from `authoring' isn't serializable, so get
  a `crypto_licensing' `KeypairEncrypted' or `KeypairPlaintext' and save
  its `str( <Keypair...> )' output to a file.  Here's how they are
  related:

  ┌────
  │ import crypto_licensing as cl
  │ 
  │ username	= 'admin@awesome-inc.com'
  │ password	= 'password'
  │ 
  │ auth_keypair	= cl.authoring( seed=b'\xff' * 32 ) # Supply None, unless you really have a random seed!
  │ encr_keypair	= cl.KeypairEncrypted( auth_keypair, username=username, password=password )
  │ decr_keypair	= cl.KeypairPlaintext( encr_keypair.into_keypair( username=username, password=password ))
  │ 
  │ # How can I know that the KeypairEncrypted holds a real private key?  Because the public key was signed by it!
  │ from crypto_licensing import ed25519
  │ try:
  │     ed25519.crypto_sign_open( encr_keypair.vk_signature + encr_keypair.vk, encr_keypair.vk )
  │     valid = True
  │ except Exception as exc:
  │     valid = exc
  │ 
  │ [
  │     [ "Encrypted:", "" ],
  │     [ "Public Key", encr_keypair['vk'] ],
  │     [ "Salt", encr_keypair['salt'] ],
  │     [ "Ciphertext", encr_keypair['ciphertext'] ],
  │     [ "Signature", encr_keypair['vk_signature'] ],
  │     [ "Valid?", repr(valid) ],
  │     [],
  │     [ "Plaintext:", "" ],
  │     [ "Public Key", decr_keypair['vk'] ],
  │     [ "Private Key", decr_keypair['sk'] ],
  │ ]
  └────

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Encrypted:                                                                                                    
   Public Key   dqFZIESm5PURJlvKc6YE2QsFKdHfYCvjChmpJXZg0fU=                                                     
   Salt         85f6c6c07df3d74fecd82600                                                                         
   Ciphertext   7ed47bd73f8e261b7398f059bd76319915ac7b8923a2568b092f8b1e5277a7a55df6fea031f1bd3cf84d860956a095ef 
   Signature    h44cyYJvofemshmvizrN0+LVisMSTcPD1BGBVkwHVbEKbz+zHsNMjczQh91mLgwv8A6mzlbF7jQqznJOQwcxDA==         
   Valid?       True                                                                                             
   Plaintext:                                                                                                    
   Public Key   dqFZIESm5PURJlvKc6YE2QsFKdHfYCvjChmpJXZg0fU=                                                     
   Private Key  //////////////////////////////////////////92oVkgRKbk9REmW8pzpgTZCwUp0d9gK+MKGakldmDR9Q==         
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Of course, to create a completely random `KeypairEncrypted' (using
  `secrets.token_bytes'), just pass the default None for the `sk'.  All
  `Serializable' objects in `crypto-licensing' are also "mapping" types
  with, so can be converted to a `dict' (values are serialized to their
  default human-readable representations when accessed as keys):

  ┌────
  │ keypair_enc = cl.KeypairEncrypted( username=username, password=password )
  │ [[k,v] for k,v in dict(keypair_enc).items() ]
  └────

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   salt          26df4b08e5002ed3dbad7918                                                                         
   ciphertext    33a6d24f2b9472af4831abe4de180460582b9d97b50e89a632fd754d9ab6b47d1361dcf99d674b1868ae29f86f3128bf 
   vk            V9fMRtLBkcd43dfEma7agr83jGu+AJXRi9ee8WMlcK8=                                                     
   vk_signature  tK05r3x+OqYThBlRU1XnEDyxeabtrU8SRGdgnCbywLJysdAUH2+WIGuvr36ASEF6pAiB2/VLpIjdtFOIgo2xAg==         
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  accessed as an `object' attribute (values are raw when accessed as
  attributes) or item name:

  ┌────
  │ [['.ciphertext', keypair_enc.ciphertext.hex()], 
  │ ['[ciphertext]', keypair_enc['ciphertext']]]
  └────

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   .ciphertext   33a6d24f2b9472af4831abe4de180460582b9d97b50e89a632fd754d9ab6b47d1361dcf99d674b1868ae29f86f3128bf 
   [ciphertext]  33a6d24f2b9472af4831abe4de180460582b9d97b50e89a632fd754d9ab6b47d1361dcf99d674b1868ae29f86f3128bf 
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  or converted to their `JSON' format using `str':

  ┌────
  │ print(keypair_enc)
  └────

  ┌────
  │ {
  │     "ciphertext":"33a6d24f2b9472af4831abe4de180460582b9d97b50e89a632fd754d9ab6b47d1361dcf99d674b1868ae29f86f3128bf",
  │     "salt":"26df4b08e5002ed3dbad7918",
  │     "vk":"V9fMRtLBkcd43dfEma7agr83jGu+AJXRi9ee8WMlcK8=",
  │     "vk_signature":"tK05r3x+OqYThBlRU1XnEDyxeabtrU8SRGdgnCbywLJysdAUH2+WIGuvr36ASEF6pAiB2/VLpIjdtFOIgo2xAg=="
  │ }
  └────


1.1.2 `crypto_licensing registered': Load or Create an Authoring Keypair
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

  But the simplest way to manage creating and then (later) obtaining
  your Authoring Keypair is to use the CLI to check if one is already
  `registered' and saved in your `~/.crypto-licensing' directory under a
  given name, using some encryption credentials.

  The first time you do this, one will be created for you; subsequently,
  the existing one will be opened, displaying the file path, the public
  key, and (with `-v') the `KeypairEncrypted':

  ┌────
  │ python3 -m crypto_licensing -v --name "Awesome-Inc" registered --username admin@awesome-inc.com --password password \
  │     --seed "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff" 
  └────

  ┌────
  │     [
  │ 	"/Users/perry/.crypto-licensing/Awesome-Inc.crypto-keypair",
  │ 	"dqFZIESm5PURJlvKc6YE2QsFKdHfYCvjChmpJXZg0fU=",
  │ 	{
  │ 	    "ciphertext":"aef7cf9884bc13bd7b4ee0cde402d2b666a084335f5d7b2bb6d2c31a8910499b5b19d450b2ccab03b83e9bb586612fb2",
  │ 	    "salt":"a84d6df719af9f50dcdc1416",
  │ 	    "vk":"dqFZIESm5PURJlvKc6YE2QsFKdHfYCvjChmpJXZg0fU=",
  │ 	    "vk_signature":"h44cyYJvofemshmvizrN0+LVisMSTcPD1BGBVkwHVbEKbz+zHsNMjczQh91mLgwv8A6mzlbF7jQqznJOQwcxDA=="
  │ 	}
  │     ]
  └────
  You may instead obtain the decrypted private signing key instead of
  the public key, using the `--private' option, for you to use in
  toolchains requiring it

  ┌────
  │ python3 -m crypto_licensing -v --private --name "Awesome-Inc" registered --username admin@awesome-inc.com --password password
  └────

  ┌────
  │     [
  │ 	"/Users/perry/.crypto-licensing/Awesome-Inc.crypto-keypair",
  │ 	"//////////////////////////////////////////92oVkgRKbk9REmW8pzpgTZCwUp0d9gK+MKGakldmDR9Q==",
  │ 	{
  │ 	    "ciphertext":"aef7cf9884bc13bd7b4ee0cde402d2b666a084335f5d7b2bb6d2c31a8910499b5b19d450b2ccab03b83e9bb586612fb2",
  │ 	    "salt":"a84d6df719af9f50dcdc1416",
  │ 	    "vk":"dqFZIESm5PURJlvKc6YE2QsFKdHfYCvjChmpJXZg0fU=",
  │ 	    "vk_signature":"h44cyYJvofemshmvizrN0+LVisMSTcPD1BGBVkwHVbEKbz+zHsNMjczQh91mLgwv8A6mzlbF7jQqznJOQwcxDA=="
  │ 	}
  │     ]
  └────
  Use `jq' to process the JSON output:
  ┌────
  │ python3 -m crypto_licensing -v --private --name "Awesome-Inc" registered --username admin@awesome-inc.com --password password \
  │ 	| jq '.[1]'
  └────

  ┌────
  │ "//////////////////////////////////////////92oVkgRKbk9REmW8pzpgTZCwUp0d9gK+MKGakldmDR9Q=="
  └────


  Of course, if you get the password wrong, then you'll get an error
  (we'll never over-write existing files):
  ┌────
  │ python3 -m crypto_licensing -v --name "Awesome-Inc" registered --username admin@awesome-inc.com --password wrong 2>&1
  └────

  ┌────
  │ 2024-12-30 16:40:56 WARNING  licensing  load_keypa Cannot load Keypair(s) from /Users/perry/.crypto-licensing/Awesome-Inc.crypto-keypair: Failed to decrypt ChaCha20Poly1305-encrypted Keypair w/ admin@awesome-inc.com's credentials
  │ 2024-12-30 16:40:56 WARNING  doh.cli    <module>   Failed: '/Users/perry/.crypto-licensing/Awesome-Inc.crypto-keypair'
  └────


  We've provided the (very poor) `--seed 0xff...' option above for
  consistency with the API calls in the example above, but you
  shouldn't; a random seed will be used to create it, unless you specify
  `--no-registering' to prevent creation:

  ┌────
  │ python3 -m crypto_licensing -v --name "Awesome-Again" registered --username admin@awesome-inc.com --password password \
  │     --no-registering 2>&1
  └────

  ┌────
  │ 2024-12-30 16:40:56 WARNING  doh.cli    <module>   Failed: Failed to find a admin@awesome-inc.com Keypair; registering a new one was declined
  └────


  But don't worry; if an existing `KeypairEncrypted' file with the
  specified name `Awesome-Inc.crypto-keypair' exists anywhere in your
  `crypto_licensing' search paths, we won't re-create it if you specify
  the wrong password, but will instead report a failure.

  It is not recommended to use the `--password ...' command-line option;
  specify the password in the `CRYPTO_LIC_PASSWORD' environment
  variable, or specify `-' to read it securely from standard input.
  `CRYPTO_LIC_USERNAME' may be used instead of `--username'.


1.2 Creating a License: Grants
──────────────────────────────

  A License carries a verifiable payload from your organization that
  will "grant" some capabilities, privileges or simply data to your
  client while they use your software.


1.2.1 Verifiable Data
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

  The simplest kind of license just grants some data, in such a way that
  your application can load the License, verify that it was issued by
  your organization, and remember for the future so it doesn't have to
  re-verify the License and associated data.

  For example, you might need to issue an API or license key for some
  component of your software, and you just want to make sure it's valid
  data issued by your organization.  Let's create a License using our
  `Awesome-Inc' authoring keypair, granting a Python `pysimplegui'
  Distribution key:

  ┌────
  │ python3 -m crypto_licensing -v --name "Awesome-Inc" \
  │     --why "AwesomePyApp: PySimpleGUI Distribution Key" \
  │     license \
  │     --username admin@awesome-inc.com --password password \
  │     --product "AwesomePyApp" \
  │     --domain "awesome-py-app.dominionrnd.com"  --no-confirm \
  │     --grant '{ "PySimpleGUI": { "License": "ebyzJLMp...20c3" }}' 2>&1
  └────

  ┌────
  │     2024-12-30 16:40:56 NORMAL   licensing  registered Found AwesomePyApp: PySimpleGUI Distribution Key Keypair at /Users/perry/.crypto-licensing/Awesome-Inc.crypto-keypair: dqFZIESm5PURJlvKc6YE2QsFKdHfYCvjChmpJXZg0fU=
  │     2024-12-30 16:40:56 DETAIL   crypto_lic license    Authoring Agent ID Pubkey: dqFZIESm5PURJlvKc6YE2QsFKdHfYCvjChmpJXZg0fU=, from /Users/perry/.crypto-licensing/Awesome-Inc.crypto-keypair
  │     2024-12-30 16:40:56 NORMAL   crypto_lic license    Issued License <LicenseSigned (from '/Users/perry/.crypto-licensing/AwesomePyApp.crypto-license')> in /Users/perry/.crypto-licensing/AwesomePyApp.crypto-license
  │     [
  │ 	"/Users/perry/.crypto-licensing/AwesomePyApp.crypto-license",
  │ 	{
  │ 	    "license":{
  │ 		"author":{
  │ 		    "domain":"awesome-py-app.dominionrnd.com",
  │ 		    "name":"Awesome-Inc",
  │ 		    "product":"AwesomePyApp",
  │ 		    "pubkey":"dqFZIESm5PURJlvKc6YE2QsFKdHfYCvjChmpJXZg0fU="
  │ 		},
  │ 		"dependencies":[],
  │ 		"grant":{
  │ 		    "PySimpleGUI":{
  │ 			"License":"ebyzJLMp...20c3"
  │ 		    }
  │ 		}
  │ 	    },
  │ 	    "signature":"tKnpz97zmfg7IlrWOjcO+Row3ZAv/gQRHIAj8I9r8vhNYMygbYz5asCUr5tPBlXmf2QPPYpudeBlnOBLp2hUAg=="
  │ 	}
  │     ]
  └────


1.2.2 `issue': Signing a License
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

  A License can be as simple, free-standing authorization with no other
  License dependencies, or it may have a tree of sub-Licenses that must
  also be confirmed as valid.


1.2.3 `verify': Confirm License (and sub-License) Validity
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌


1.3 Using Licenses
──────────────────

1.3.1 `load_keys': Find all Ed25519 Signing Keys
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌


1.3.2 `load': Find all Licenses
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌


1.3.3 `check': Find all Keys and Valid Licenses
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

  Loads every available Ed25519 Keypairs (with the provided
  credentials), and all available Licenses, yielding all
  <Keypair>,<LicenseSigned> that are valid in the current environment.

  If no valid License is available for some key found, then
  <Keypair>,None is yielded, allowing the caller to use the Key to issue
  a License if desired.

  If nothing at all is yielded, then this indicates that *no* Keypairs
  were found; either you need to "register" (create and save) one, or
  provide different credentials.


1.4 Running A `crypto_licensing.licensing' Server
─────────────────────────────────────────────────

  Supply the `username' and `password' to the `KeypairEncrypted' via
  environment variables `CRYPTO_LIC_USERNAME' and `CRYPTO_LIC_PASSWORD'.


2 Payment with Cryptocurrencies
═══════════════════════════════


3 Issuance via Web API
══════════════════════
