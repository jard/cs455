//package client;
import java.awt.TextArea;
import java.awt.TextField;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

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
				this.socketI.toSocket(s);
				if(s.equals("QUIT")){
					socketI.close();
					System.exit(0);
				}
			} catch (Exception e1) {
				e1.printStackTrace();
			}
			clientInput.setText(null);
		}
		
	}	

	/**
	 * Creates the GUI portion of the client
	 */
	private void createFrame( ){
		topFrame = new JFrame( "jamIRC" );
		lbl = new JPanel();
		topFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
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
