/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package client;

/**
 *
 * @author dangtx
 */
import java.io.*;
import java.net.*;

class JAMIRCClient {

    public static void main(String argv[]) throws Exception {
        
        
        //input from user
        String sentence;
        
        //returned input from server
        String modifiedSentence;
        
        //reader to get input from user
        BufferedReader inFromUser = new BufferedReader(
                new InputStreamReader(System.in));
        
        //creating a new client socket
        Socket clientSocket = new Socket("localhost", 6789);
        
        //stream to write TO the server
        DataOutputStream outToServer = new DataOutputStream(
                clientSocket.getOutputStream());
        
        //stream to read FROM the server
        BufferedReader inFromServer = new BufferedReader(new InputStreamReader(
                clientSocket.getInputStream()));
        
        //get the input from user
        sentence = inFromUser.readLine();
        
        //write to server
        outToServer.writeBytes(sentence + '\n');
        
        System.out.println("FROM SERVER: \n");
        do {
	        //read from the server
	        modifiedSentence = inFromServer.readLine();
	        if(modifiedSentence != null){
	        	//output to user
	        	System.out.println(modifiedSentence);
	        }
        } while (modifiedSentence != null);
        //close the socket
        clientSocket.close();
    }
}
