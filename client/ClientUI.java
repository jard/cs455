//package client;
import java.awt.TextArea;
import java.awt.TextField;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.IOException;

import javax.swing.BoxLayout;
import javax.swing.JFrame;
import javax.swing.JPanel;



public class ClientUI implements ActionListener {
	/* Class Variables */
	/* Frame Components */
	private JFrame topFrame;
	private JPanel lbl;
	private TextArea clientOutput; 
	private TextField clientInput;
	
	// Networking Components
	private SocketInterface socketI;	
	
	
	public static void main(String[] args) throws Exception {
		new ClientUI();
	}
	
	/* Set up frame */
	public ClientUI( ){
		createFrame( );
		try {
			socketI = new SocketInterface(this);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}		
	}
	
	/* User inputed a string, and hit enter */
	public void actionPerformed( ActionEvent e ){
		if( e.getSource() == clientInput ){
			
			String s = clientInput.getText();
			// TODO: parse client message into IRC protocol format
			
			try {
				if(s.equals("QUIT")){
					quit();
				} else {
					this.socketI.toSocket(s);
				}
			} catch (Exception e1) {
				e1.printStackTrace();
			}
			clientInput.setText(null);
		}
		
	}	

	/**
	 * This method is called when the user enters the message QUIT or if
	 * they close the client window.
	 */
	private void quit() {
		try {
			this.socketI.toSocket("QUIT");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		socketI.close();
		System.exit(0);		
	}

	/**
	 * Creates the GUI portion of the client
	 */
	@SuppressWarnings("serial")
	private void createFrame( ){
		topFrame = new JFrame( "jamIRC" ){
			@Override
			// this method is called when the window is closed
			public void dispose() {
				quit();	// calls the client's quit method
			}
			
		};
		lbl = new JPanel();
		topFrame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);	// call Jframe's dispose method when closed
		topFrame.setResizable(false);
		topFrame.setSize(500,500);
		topFrame.setLocationRelativeTo(null);
		
		
		clientOutput = new TextArea("<jamIRC>\n", 20, 50, TextArea.SCROLLBARS_BOTH);
		clientOutput.setEditable(false);
		
		clientInput = new TextField(50);
		clientInput.addActionListener(this);
		
		lbl.setLayout(new BoxLayout(lbl, BoxLayout.Y_AXIS)); 
		lbl.add(clientOutput);
		lbl.add(clientInput);
		/* Done, Pack Frame */
		topFrame.add(lbl);
		topFrame.pack();
		topFrame.setVisible(true);
	}

	/**
	 * This message is called by the SocketInterface when a message is
	 * received from the server.
	 * @param msg	The server message.
	 */
	public void receiveMessage(String msg) {
		// TODO: parse and interpret msg based on IRC protocol
		
		// print out interpreted message
		// TODO: currently prints out uninterpreted message
		clientOutput.append(msg + "\n");
		
	}

}
