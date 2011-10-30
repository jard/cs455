//package client;

public class MessageHandler {

	private enum MSG {
		USER , JOIN , LIST , PRIVMSG , QUIT , ERROR
	}
	
	private MSG currentMessage;
	
	public MessageHandler( ){
		currentMessage = MSG.ERROR;
	}
	
	/* Passing messages from the client to the socket */
	public void fromClient( String s ){
		
		/* Send to socket */
		try {
			Main.socketI.toSocket(s + "\n");
		} catch (Exception e) {
			e.printStackTrace();
		}
		
	}
	
	
	/* Passing messages from the socket to the client */
	public void fromSocket( String s ){
		
		Main.topLevel.toInterface(s + "\n");
	}
	
}

