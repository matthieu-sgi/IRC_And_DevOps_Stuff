# DVIC Chat

Simple chatroom project to test devops and sockets

The project is made of a client and a server.

The Server:

- Receives a connection on a socket
- Handle multiple clients
- Broadcasts messages to clients
- Handles when a client disconnects (send "`<username>` disconnected" )

The Client:

- Connects to the server
- Sends its information (username)
- Sends and receives messages from the server