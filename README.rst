Product presentation
====================

MnemoPwd is a client-server application to store and retrieve secret information.
It is based on OpenSSL cryptographic library and its installation is required both
on the client side and the server side.

MnemoPwd use a fork of the PyElliptic module developped by Yann GUIBET under BSD License,
that is a high level wrapper of OpenSSL (see https://github.com/yann2192/pyelliptic).

See https://www.openssl.org ("OpenSSL Homepage") web site for more information.

Require Python 3.4.4 or newer, OpenSSL, GNU/Linux or Mac OS X

Always use the last version for security.

Copyright (c) 2015-2016, Thierry Lemeunier <thierry at lemeunier dot net> under 
BSD Licence

Features
========

- Double level of connection security : the SSL/TLS protocol and the application protocol
- Server identity can be controlled by X.509 certificate (optional TLS feature)
- Client and server share a master secret via ECDH scheme
- Each secret information is encrypted with the ECIES scheme
- Integrity is controlled by two HMAC (ECIES scheme + a 512-bits HMAC per block)
- Possibility of three stages of data encryption by client's configuration
- Keys are computed on the fly by the client and the server
- Keys are never stored by the server or by the client
- Do some self-controls before starting
- Configuration by file and/or by command line options
- Server running in background (only on POSIX systems)
- UML model of the secure application protocol (see https://github.com/thethythy/Mnemopwd)

Installation (and uninstalling)
===============================

They are two installation modes:

- PIP Installation

With PIP just hit in a terminal: ``pip install MnemoPwd``
For uninstalling just hit in a terminal: ``pip uninstall MnemoPwd``
Do not forget to delete configuration files and the database directory (see configuration explanation).

For more information about PIP see https://pip.readthedocs.io/.

- Source Installation

You can get the ZIP archive from GitHub (https://github.com/thethythy/Mnemopwd) using the button ``Clone or download``.
Just unzip the archive file and go in the source directory.
For uninstalling, delete the ZIP archive and the source directory.
Do not forget to delete configuration files and the database directory (see configuration explanation).

Configuration
=============

Server configuration
--------------------

The server use ``~/.mnemopwds`` as configuration file. This file is automatically created
at the first launch if it does not already exist. You can edit this file, for example,
to indicate a private key file and a certificate file. You can change the following options:

- Host IP (by default it is the address in the local network);
- Log level;
- Private key file and certificate file (none by default);
- Host port (``62230`` by default);
- Path to the database directory (by default it is ``~/mnemopwddata``);
- Some other options about logging.

Secret information are always left encrypted in the database in ``~/mnemopwddata`` directory.
This directory contains also log files. This directory is accessible only for the user
who launch the server.

You can also change some options on the command line. Use option ``-h`` or ``--help`` to get a help screen.
The command line has priority over configuration file.

Client configuration
--------------------

The client use ``~/.mnemopwdc`` as configuration file. This file is automatically created
at the first launch if it does not already exist. You can edit this file, for example,
to indicate a shared certificate file. You can change the following options:

- Shared certificate file (none by default);
- Server IP;
- Server port;
- Lock screen timeout (one minute by default);
- Cryptographic suites (by default one stage with sect571r1 and aes-256-cbc).

The user can define in the configuration file three stages of encryption. There is
one stage defined by default. Paranoiac users can add one or two stages of encryption
but it will be more slow to encrypt and to decrypt secret information...

You can also change some options on the command line. Use option ``-h`` or ``--help`` to get a help screen.
The command line has priority over configuration file.

Usage
=====

Start a server or client from PIP installation
----------------------------------------------

Start a server
..............

   ``mnemopwds -h``          --> get a help screen

   ``mnemopwds --start``     --> start the server

   ``mnemopwds [--status]``  --> get a status message

   ``mnemopwds --stop``      --> stop the server

Start a client
..............

   ``mnemopwdc -h``          --> get a help screen

   ``mnemopwdc``             --> start the client (you may indicate the server ip address)

   ``mnemopwdc --status``    --> get a status message

Start a server or a client from the source directory
----------------------------------------------------

You can use ``python3 mnemopwds.py`` for launching the server. You can also change the execution property
of the server launcher with ``chmod +x mnemopwds.py`` and then use directly ``./mnemopwds.py``.
You can do the same things for client launcher (``mnemopwdc.py``).

Certificate usage
-----------------

To authenticate the server, a X.509 certificate can be used. You can use an existing certificate or use
a new self-signed certificate created with OpenSSL. In the last case, please follow next steps:

1. Generate a self-signed certificate: in a terminal, launch the next command line

   ``openssl req -x509 -new -utf8 -nodes -out mnemopwdcert -keyout mnemopwdkey``

   where ``mnemopwdcert`` is the certificate file to share and ``mnemopwdkey`` is the private key
   file to keep secret (never shared this file).
   
   See https://www.openssl.org/docs/manmaster/apps/req.html for more information.

2. Move certificate file and key file in a secure directory on server (I recommend the ``~/mnemopwddata``
   directory created by the server application the first start you launch it).

3. The certificate file (``mnemopwdcert``) **must be copy** on each client computer to share it.

4. Finally, indicate to the server the ``-c`` and ``-k`` options and to the client the ``-c`` option or
   modify configuration files (by default ``~/.mnemopwds`` for server and ``~/.mnemopwdc`` for client).
   For example (stop server if it is already started):

   ``mnemopwds --start -c /path/to/mnemopwdcert -k /path/to/mnemopwdkey`` --> start the server using SSl/TLS identity control mechanism

   ``mnemopwdc -c /path/to/mnemopwdcert`` --> start the client with the same certificate file to control server identity
