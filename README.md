Product presentation :
----------------------

MnemoPwd is a client-server application to store and retrieve secret informations.
It is based on OpenSSL cryptographic library and its installation is required both
on the client and the server.

MnemoPwd use the PyElliptic module developped by Yann GUIBET under BSD License,
that is a high level wrapper of OpenSSL (see https://github.com/yann2192/pyelliptic).

See OpenSSL web site for more information (https://www.openssl.org)

Require Python3, OpenSSL

Always use the last version for security.

Features :
----------

- One central server serves multiple clients
- Multiple clients can be used on a same node (each with a different user)
- Client identity is controlled by a challenge and a id value stored per client on the server
- For easy usage, a client can store locally its password but it is not required
- A client can be launched on the same node of the server but it is not recommended
- Each secret information is encrypted with the ECIES scheme
- Integrity is controlled by two hmac : a 256-bits hmac for each secret
  information (ECIES scheme) and a 512-bits hmac for each block
- Client and server share a master secret via ECDH protocol
- Keys are computed on the fly by the client and the server
- Keys are not stored by the server or by the client
- Communications between the client and the server is secured by SSL/TLS protocol
- Identities (client and server) can be controlled by certificat X.509 (optional TLS feature)
- Double level of security : encryption by SSL/TLS protocol and encryption by the client
- Possibility of three stages of data encryption by client's configuration
- Design for local network usage only

Usage :
-------

- First start the server

??????

- Start a client

????????
