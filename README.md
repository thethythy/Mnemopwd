This software is still under development. 
[x] The server development is almost finished and can been tested.
[ ] The client development is not started.

## Product presentation:
---------------------

MnemoPwd is a client-server application to store and retrieve secret informations.
It is based on OpenSSL cryptographic library and its installation is required both
on the client and the server.

MnemoPwd use the PyElliptic module developped by Yann GUIBET under BSD License,
that is a high level wrapper of OpenSSL (see https://github.com/yann2192/pyelliptic).

See [OpenSSL] (https://www.openssl.org "OpenSSL Homepage") web site for more information.

Require Python3.4 or newer, OpenSSL, GNU/Linux or Mac OS X

Always use the last version for security.

Copyright (c) 2015-2016, Thierry Lemeunier <thierry at lemeunier dot net> under 
BSD Licence

## Features:
---------

- One central server serves multiple clients
- Multiple clients can be used on a same node (each with a different user)
- Double level of connection security : the secure SSL/TLS protocol and the secure application protocol
- Server identity can be controlled by X.509 certificat (optional TLS feature)
- Client and server share a master secret via ECDH scheme
- Each secret information is encrypted with the ECIES scheme
- Integrity is controlled by two hmac : a 256-bits hmac for each secret information (ECIES scheme) and a 512-bits hmac for each block
- Possibility of three stages of data encryption by client's configuration
- Keys are computed on the fly by the client and the server
- Keys are never stored by the server or by the client
- Do some self-controls before starting
- Configuration by file and/or by command line options
- Server running in background (only on POSIX systems)
- UML model of the secure application protocol

## Usage:
------

### Start the server:

   `./serverctl -h`          --> get a help screen

   `./serverctl --start`     --> start the server

   `./serverctl [--status]`  --> get a status message

   `./serverctl --stop`      --> stop the server

### Start a client

   Client not yet developed :disappointed:

### Certificat usage:
-----------------

To autenticate server, a X.509 certificat can be used. You can use an existing certificat or use
a new self-signed certificat created with OpenSSL. In the last case, please follow next steps:

1. Generate a self-signed certificat: in a terminal, launch the next command line

   `openssl req -x509 -new -utf8 -nodes -out mnemopwdcert -keyout mnemopwdkey`

   where `mnemopwdcert` is the certificat file to share and `mnemopwdkey` is the private key
   file to keep secret (never shared this file)
   
   See https://www.openssl.org/docs/manmaster/apps/req.html for more informations.

2. Test the certificat: in the test/test_certificat directory and in a terminal launch
   the next command line:

   `./server.py -c /path/to/mnemopwdcert -k /path/to/mnemopwdkey`
   
   that start a local server application using the certificat (use `./server.py -h` to get help).

   In a second terminal and in the test/test_certificat directory, launch:

   `./client.py -c /path/to/mnemopwd`

   that start a local client that communicate with the previous local server (use `./client.p -h` to get help).

   If the certificat is accepted, the client shows it and the message `The certificat seems compatible`.

3. Move certificat file and key file in a secure directory on server (I recommend the mnemopwddata
directory created by the server application the first start you launch it).

4. The certificat file (`mnemopwdcert`) must be copy on each client computer to share it.

5. Finally, indicate to the server the `-c` and `-k` options and to the client the `-c` option or 
modify configuration files (by default `~/.mnemopwds` for server and `~/mnemopwdc` for client).
For example (stop server if it is already started):

   `./serverctl --start -c /path/to/mnemopwdcert -k /path/to/mnemopwdkey`
