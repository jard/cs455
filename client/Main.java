//package client;

public class Main {
	
	static ClientUI topLevel;
	static SocketInterface socketI;
	static MessageHandler MH;
	
	public static void main(String[] args) throws Exception {
		topLevel = new ClientUI();
		socketI = new SocketInterface();
		MH = new MessageHandler();
	}

}