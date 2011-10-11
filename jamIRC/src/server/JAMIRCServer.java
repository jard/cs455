/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package server;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;

/**
 *
 * @author dangtx
 */
public class JAMIRCServer {
    public static void main(String argv[]) throws Exception
      {
         //input from client 
         String clientSentence;
         
         //converted string (captalized)
         String capitalizedSentence;
         
         //server socket
         ServerSocket welcomeSocket = new ServerSocket(6789);

         
         while(true) 
         {
           //waiting for clients to connect to this socket
           Socket connectionSocket = welcomeSocket.accept();
           InetAddress clientAddress = connectionSocket.getInetAddress();
           String clientHostName = clientAddress.getHostName();
           String clientIP = clientAddress.getHostAddress();
           System.out.println("connection made by " + clientAddress.toString());
           
            BufferedReader inFromClient =
               new BufferedReader(new InputStreamReader(connectionSocket.getInputStream()));
            
            DataOutputStream outToClient =
               new DataOutputStream(connectionSocket.getOutputStream());
            
            //get the input from the client
            clientSentence = inFromClient.readLine();
            
            //captialized the input
            capitalizedSentence = 
                  clientSentence.toUpperCase() + '\n';
            
            //write back to client
            outToClient.writeBytes(capitalizedSentence);
            
            //write client host name and address back to client
            clientSentence = "your host name = " + clientHostName + "\n";
            clientSentence += "your address = " + clientIP + "\n";
            outToClient.writeBytes(clientSentence);
            outToClient.close();
         }
      }
}
