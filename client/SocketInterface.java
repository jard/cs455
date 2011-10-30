//package client;

import java.io.*;
import java.net.*;

public class SocketInterface extends Thread {
	
	private Socket clientSocket; 
	private DataOutputStream outToServer;
	private BufferedReader inFromServer;
	
	/* Create sockets and stream readers */
	public SocketInterface( ) throws Exception{
		/* Create new socket */
		clientSocket = new Socket("localhost", 5000);
		/* Create stream Readers */
		outToServer = new DataOutputStream( clientSocket.getOutputStream() );
		inFromServer = new BufferedReader( new InputStreamReader(
				clientSocket.getInputStream()));
		this.start();
		
	}
	
	/* Send string to server */
	public void toSocket( String s ) throws Exception{
		/* Write command to socket */
		System.out.printf("Sending: ");
		System.out.println(s);
		outToServer.writeBytes(s);
	
	}
	
	public void run() {
		String modSentence = null;
		do {
			try {
				modSentence = inFromServer.readLine();
			} catch (IOException e) {
				e.printStackTrace();
			}
			if(modSentence != null){
				Main.MH.fromSocket(modSentence);
			}
		} while (modSentence != null);
	}
	
}
