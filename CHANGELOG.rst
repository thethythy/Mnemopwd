Changelog
=========


v1.2.1 (2018-07-10)
-------------------

Changes
~~~~~~~
- New process for generating the session number. [Thierry Lemeunier]
- UML model updated. [thethythy]


v1.2.0 (2017-07-23)
-------------------

New
~~~
- Add clear and secure importation / exportation functionalities.
  [thethythy]
- Add a FileChooserWindow standard dialog box. [thethythy]
- Add a ListBox widget. [thethythy]
- Add the possibility to use colours in client interface (#6)
  [thethythy]

Changes
~~~~~~~
- UML model updated. [thethythy]
- Better UX using the vertical scrollbar widget. [thethythy]
- Replace and delete SearchPanelResult by ListBox widget in
  SearchWindow. [thethythy]
- Better cursor handler in editors. [Thierry Lemeunier]
- Now the configuration file is updated if necessary when a new version
  of MnemoPwd is installed. [Thierry Lemeunier]

Fix
~~~
- Fix a bug in the vertical scroll bar widget. [thethythy]
- Bug correction when LAN is not conform with RFC 1918. [thethythy]


v1.1.0 (2017-03-28)
-------------------
- Add a limitation of number of login and user account creation per hour
  (#2) [thethythy]
- Add IP auto-configuration of the client (enhancement #3) [thethythy]
- ULM model updated. [thethythy]
- Add a scrolling bar in the research result panel (issue #4 fixed)
  [thethythy]
- Add a 3D effect to dialog windows (enhancement #5) [thethythy]


v1.0.0 (2017-02-22)
-------------------
- Add a change log file generated with gitchangelog
  (https://github.com/vaab/gitchangelog) [thethythy]
- UI and UX enhancements. [thethythy]

  - A widget button is 'inversed' only when it obtains the focus
  - Each menu has a border
  - Shortcuts are now in lowercase
- Add the number of blocks loaded in the progress bar. [thethythy]
- Bug #17 fixed (client disconnection when too many blocks are received)
  [thethythy]
- Issue #16 fixed (links between edition window and search window)
  [thethythy]
- Issue #15 fixed (search panel refreshing bug) [thethythy]


v1.0.0rc3 (2016-12-16)
----------------------
- UML model updated (add LabelBox class in the class diagram) [Thierry
  Lemeunier]
- Add the LabelBox widget (issues #13 and #14 fixed) [Thierry Lemeunier]
- Issue #12 fixed (InputBox widget bug) [Thierry Lemeunier]
- Issue #11 fixed (impossible to login from two different OS) [Thierry
  Lemeunier]
- Issue #11 fixed (impossible to login from two different OS) [Thierry
  Lemeunier]


v1.0.0rc2 (2016-11-26)
----------------------
- Update file list to take into account in the fingerprint. [Thierry
  Lemeunier]
- Issues #10 #9 #8 fixed. [Thierry Lemeunier]
- README file updated. [Thierry Lemeunier]
- Add some directories to reject in .gitignore. [Thierry Lemeunier]


v1.0.0rc1 (2016-11-05)
----------------------
- Update README.rst. [Thierry Lemeunier]
- Update README.rst. [Thierry Lemeunier]
- Modification of README file syntax. [Thierry Lemeunier]
- Release candidat v1.0.0rc1. [Thierry Lemeunier]
- Use last version of pyelliptic (fork) [Thierry Lemeunier]
- Make source code compliant much as possible with PEP 8. [Thierry
  Lemeunier]
- Fix a bug when a SIB is truncated by the network. [Thierry Lemeunier]
- UML model updated. [Thierry Lemeunier]
- Now the result panel is updated after an edition, a creation or a
  deletion of a block. [Thierry Lemeunier]
- Add the scrolling of components in the result panel. [Thierry
  Lemeunier]
- Fix a bug in the exception handler of the protocol and another bug in
  user account creation. [Thierry Lemeunier]
- The UI layer use internally SIBs to minimize clear confidential
  information in memory. [Thierry Lemeunier]
- Now connection is correctly closed when user quit application.
  [Thierry Lemeunier]
- Now error messages of the server contain no indication of the source
  of the error. [Thierry Lemeunier]
- Had an error message when the server address is already use. [Thierry
  Lemeunier]
- Add the date of starting and duration in the status message of the
  server. [Thierry Lemeunier]
- Control the terminal size with the number of fields of a block type.
  [Thierry Lemeunier]
- Add screen lock in the edition window and in the search window.
  [Thierry Lemeunier]
- Add a salt value in the password digest computation. [Thierry
  Lemeunier]
- Fix a bug in the configuration at the first launching. [Thierry
  Lemeunier]
- Add an automatic or manual configurable screen lock. [Thierry
  Lemeunier]
- Implementation of the state S32 (client side) [Thierry Lemeunier]
- Minor modification about connection error handling. [Thierry
  Lemeunier]
- User account creation/deletion processes are operational. [Thierry
  Lemeunier]
- Add a window to create a new user window. [Thierry Lemeunier]
- Modification of the menu. [Thierry Lemeunier]
- Search window + bug corrections. [Thierry Lemeunier]
- Implementation of the state S37 (client side) [Thierry Lemeunier]
- Now I use PyCharm IDE for developping. [Thierry Lemeunier]
- Now the notification in the protocolar states is done in a separate
  thread. [Thierry Lemeunier]
- Fix a bug in case there is no result. [Thierry Lemeunier]
- Add a task execution loop inside the main asyncio loop. [Thierry
  Lemeunier]

  - Commands coming from UI layer are registered like tasks
  - Each task is enqueued and then executed one by one
  - The task loop execute each task and wait for the task's end
  - Protocol states are executed in a thread one by one (using a reentrant lock)
- Implementation of the state S34 (client side) [Thierry Lemeunier]
- Add some logs in protocolar states of the server. [Thierry Lemeunier]
- Implementation of the state S36 (client side) [Thierry Lemeunier]
- Implementation of the state S35 (client side) [Thierry Lemeunier]
- Add the block edition window. [Thierry Lemeunier]
- Rationalization of the component hierarchy and add redraw method.
  [thethythy]
- Add block type and the create menu. [thethythy]

  - Block types are loaded from a json file during configuration at starting
  - A menu to create a new block is accessible after connection
- Implementation of the state S31 on client side. [thethythy]
- Add a symbol in the status window to show server connection state.
  [thethythy]
- Add a timeout on server connection request. [thethythy]
- Communication from UI layer to core layer has been improved.
  [thethythy]
- Login and logout processus are plenty operational. [thethythy]
- Modification of connection exception handling in ClientCore.
  [thethythy]

  - ClientCore outputs exception messages
  - clientctl exits in case of exception
- Modification of some error messages. [thethythy]
- Implementation of the states S21 and S22 on client side. [thethythy]
- Add a special widget for secret text edition (class SecretTextEditor)
  [thethythy]
- Add TextEditor class. [thethythy]

  - TextEditor class is a copy of the official Textbox class
  - TextEditor class can edit extended ASCII characters
- Implementation of the state S1 in the client side. [thethythy]
- Modification of the protocol error message in the server states.
  [thethythy]
- Add MainWindow MainWindow is the principal window of the client
  application. [thethythy]
- Add uiapplication module The module named uiapplication contains the
  windows of the client application. [thethythy]
- Add the class BaseWindow - BaseWindow is a window without border and
  without title but with a mouse and keyboard handler -
  TitledBorderWindow is a BaseWindow but with a border and a title.
  [thethythy]
- Add shortcut keys in InputBox and ButtonBox components. [thethythy]
- New architecture of client module - UI layer and Core layer are now
  two different modules - UI components are now in a separated module.
  [thethythy]
- Fist version of the user interface in curses - UI is a curses
  interface in a thread - Communication from UI to client core is made
  by a Facade (ClientCore) - Communication from the domain layer to the
  UI layer uses the design pattern Observer - First version of the
  connection window - Beginning of the domain layer (mainly application
  protocol) - Configuration of the client by file or by options on the
  command line. [thethythy]
- Fix a bug in the fingerprint processing. [thethythy]
- Server can now be launched with an extern ip address (other than
  "localhost") - The server finds an extern address connected to the LAN
  - The ip address can be changed in the configuration file or by the
  command line. [thethythy]
- Change the location of the script MnemopwdFingerPrint.py. [thethythy]
- Add a control of the validity period if a X509 certificat is used.
  [thethythy]
- Update README.md. [Thierry Lemeunier]
- Add the possibility to control server identity with a X509 certificat.
  [thethythy]
- Add a fingerprint control mechanism of the source code. [Thierry
  Lemeunier]
- Optimization of the database access with a central dictionary of RLock
  instances. [thethythy]
- Add a module to start and stop the server for working in background
  (only on POSIX system) [thethythy]
- Renovation of the protocol (the substate Importation has been removed)
  [thethythy]
- Design, implementation and test of the state S32 (Exportation)
  [thethythy]
- UML model updated. [thethythy]
- Test and implementation of the state S34 (Deletion) finished.
  [thethythy]
- Implementation of the state S34 (Deletion) [thethythy]
- Design of the state S34 (Deletion) [thethythy]
- Implementation of the state S37 (DeleteData) + correction of a bug
  (index handling in search_data and update_crypto) [thethythy]
- Design of the state S37 (DeleteData) [thethythy]
- Add an index entry in each databse file to delete easily. [thethythy]
- Add file StateS38.py. [thethythy]
- Implementation of the state S38 (UpdateData) [thethythy]
- Design of the state S38 (UpdateData) [thethythy]
- Now execution of configure_crypto and update_crypto methods is
  controlled by a Lock object. [thethythy]
- Now database access is controlled by a lock object. [thethythy]
- Design and implementation of the state S35 (SearchData) [thethythy]
- Now server communicates with clients in a threadsafe manner.
  [thethythy]
- Implementation of the state S31 finished (the new configuration case)
  [thethythy]
- UML model updated. [thethythy]
- Implementation of the state S36. [thethythy]
- Now secret information block integrity value takes account of the
  cryptographic configuration to be computed. [thethythy]
- Correction of the __contains__ method of InfoBlock. [thethythy]
- Integrity control is now in a separate method. [thethythy]
- Important modification of SecretInfoBlock - SecretInfoBlock is now a
  subclass of InfoBlock - SecretInfoBlock takes place of CryptoHandler
  (deleted) for not sharing cryptographic configuration -
  SecretInfoBlock integrity control is changed for not being dependent
  of the stockage order. [thethythy]
- Design of the S36 state (AddData) + Modification of the design of the
  S31 state (Configuration) [thethythy]
- Implementation od the S31 state (todo : new configuration case)
  [thethythy]
- Change licence : now Mnemopwd is under BSD 2-Clause License.
  [thethythy]
- Design of state S3 of the protocol + class diagram updates.
  [thethythy]
- Change place of 2 functions to 2 methods of StateSCC class.
  [thethythy]
- UML model updated. [thethythy]
- Random session value generation finished + server log is now in the
  database directory. [thethythy]
- Implementation of the new protocol including session - New state S1
  (S1S and S1C) = Session + Challenge - New state SCC = Challenge
  Controller - S21 and S22 updated - S21 and S22 are not linked anymore
  - Tests for S1, SCC, S21 and S22. [Thierry Lemeunier]
- Some protocol optimizations. [Thierry Lemeunier]
- New protocol design including session. [Thierry Lemeunier]
- Add database directory control (permissions, type of file, owner of
  file) [Thierry Lemeunier]
- Add configuration file control (permissions, type of file, owner of
  file) [Thierry Lemeunier]
- Add configuration feature. [Thierry Lemeunier]
- S11 and S12 completed - Delete unused files - Add test cases for S0,
  S11 and S12 protocol states. [Thierry Lemeunier <>]
- States S11 and S12 Minor modification of the protocol. [toto]
- Major modifications of the protocol. [Thierry Lemeunier]
- States S0, S1 and S11 Minor modification of the protocol. [Thierry
  Lemeunier <>]
- Starting protocol conception and architecture to handle it - The
  server is an asyncio server based on an i/o asynchronous loop (class
  Server) - Each client connection is handled by a separate object
  (class ClientHandler) - Protocol is composed of differents states
  (StateS0, StateS1...) - Each state is a singleton class with a do
  method - do method of each state is executed by an executor for not
  blocking i/o asynchronous loop - Exception raised by do method is
  treated asynchronously by a callable of the client handler. [Thierry
  Lemeunier <>]
- Add verification of the keypair. [Thierry Lemeunier]
- Change pyelliptic version to 1.5.7. [Thierry Lemeunier]
- Common classes with encryption and decryption treatments - Add
  decorators on two SecretInfoBlock methods (__getitem__ and
  __setitem__) - These decorators are defined in CryptoHandler -
  Decorators use encrypt/decrypt methods of KeyHandler - KeyHandler use
  ECIES scheme (IEEE 1363a) to compute keypairs, to encrypt and to
  decrypt (via OpenSSL library) - ECC keypairs are computed from a
  master secret (shared with client and server) - Three stages of
  encryption/decryption can be used. [Thierry Lemeunier <>]


