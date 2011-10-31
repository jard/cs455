//package client;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.Socket;

public class SocketInterface extends Thread {
	
	private Socket clientSocket; 
	private DataOutputStream outToServer;
	private BufferedReader inFromServer;
	
	// stores the client instance that this socket is interfacing with
	private ClientUI client;
	
	/* Create sockets and stream readers */
	public SocketInterface( ClientUI c) throws Exception{
		this.client = c;
		/* Create new socket */
		clientSocket = new Socket("localhost", 5000);
		/* Create stream Readers */
		outToServer = new DataOutputStream( clientSocket.getOutputStream() );
		inFromServer = new BufferedReader( new InputStreamReader(
				clientSocket.getInputStream()));
		this.start();
		
	}

	

	/**
	 * Send the client message to the server.
	 * 
	 * @param s		The message to be sent.
	 * @throws IOException	Thrown by write method
	 */
	public void toSocket( String s ) throws IOException{
		/* Write command to socket */
		System.out.printf("Sending: ");
		System.out.println(s);
		byte[] c = s.getBytes();
		outToServer.write(c, 0, s.length());
	
	}
	
	/**
	 * Close the input and output sockets and stop this thread.
	 */
	public void close(){
		try {
			inFromServer.close(); //throws IOException
			outToServer.close();
			this.join();	// throws InterruptedException
		} catch (Exception e) {	
			e.printStackTrace();
		}
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
				client.receiveMessage(modSentence);
			}
		} while (modSentence != null);
	}
	
}
