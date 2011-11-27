package client;

import java.io.*;
import java.net.*;

public class SocketInterface extends Thread {
	
	/* Socket related goodies */
	private Socket clientSocket; 
	private DataOutputStream outToServer;
	private BufferedReader inFromServer;
	
	ClientUI ui;
	
	/* Create sockets and stream readers */
	public SocketInterface( ClientUI uiPtr ) throws Exception{
		/* Create new socket */
		ui = uiPtr;
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
		System.out.printf(s);
		byte[] c = s.getBytes();
		outToServer.write(c, 0, s.length());
	
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
				/* Push the message to the UI */
				ui.fromSocketParse(modSentence + "\n");
			}
		} while (modSentence != null);
	}
	
	/* Called after user inputs "QUIT" command */
	/* Closes data buffers and joins thread */
	public void close () {
		try {
			inFromServer.close();
			outToServer.close();
			this.join();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
}
