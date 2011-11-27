package client;

import javax.swing.*;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import java.util.Vector;
import java.awt.*;
import java.awt.event.*;


public class ClientUI implements ActionListener, ListSelectionListener {
	
	/*******************/
	/* Class Variables */
	/*******************/
	
	/* Frame Components */
	private JFrame topFrame;
	private JPanel contentPane;
	private TextArea clientOutput; 
	//private TextArea channelList;
	private TextField clientInput;
	private JList channelList;
	
	/* User string */
	String user; //User name
	
	/* Channel strings */
	private String channelToJoin;
	private DefaultListModel channels;
	//private Vector<String> channels;
	private int currentChannelIndex;
	
	/* Socket reference */
	SocketInterface socketI;
	
	/* Global message state, used to interpret incoming server ACKs */
	private enum MSG {
		USER , JOIN , LIST , PRIVMSG , QUIT , ERROR
	}
	
	/* The global message state */
	private MSG currentMessage;
	
	
	/*****************/
	/* CLASS METHODS */
	/*****************/

	/* MAIN, entry point */
	public static void main( String [] args) throws Exception {
		new ClientUI();
	}
	
	/* ClientUI constructor, create frame and socket */
	public ClientUI( ) {
		
		/* Create socket */
		try {
			socketI = new SocketInterface(this);
		} catch ( Exception e ) {
			e.printStackTrace();
		}
		
		/* Set up frame */
		createFrame( );	
		
		/* Initial get user name */
		user = getUserName("Please Enter Your IRC Nickname :");
		
			
		
	}
	
	/* Listener for the JList */
	public void valueChanged( ListSelectionEvent e ){
		
	}
	
	/* User input a string, and hit enter */
	/* Input string simply passed to "toSocketParse()" */
	public void actionPerformed( ActionEvent e ){
		if( e.getSource() == clientInput ){
			
			String s = clientInput.getText();
			try {
				toSocketParse( s + "\n" );
			} catch (Exception e1) {
				e1.printStackTrace();
			}
			clientInput.setText(null);
		}
		
	}
	
	/* The message parse on the way to the socket */
	/* Goal: Determine the message, save global state */
	/*     then react accordingly when ACK is returned */
	void toSocketParse ( String s ) throws Exception {
		String [] msgSplit;
		msgSplit = s.split(" ");
		
		if( msgSplit[0].contains("USER") ){
			
			currentMessage = MSG.USER;
		} else if ( msgSplit[0].contains("QUIT") ) {
			/* User input quit, push command to socket, bail out */
			socketI.toSocket(s);
			quit();
		} else if ( msgSplit[0].contains("JOIN") ) {
			/* User attempting to join or create a channel */
			channelToJoin = msgSplit[1];
			currentMessage = MSG.JOIN;
		} else if ( msgSplit[0].contains("LIST") ) {
			/* Nothing to do , relay messages to / from   */
			currentMessage = MSG.LIST;
		} else if ( msgSplit[0].contains("PRIVMSG") ) {
			currentMessage = MSG.PRIVMSG;
			
		} else {
			/* Message Not recognizable */
			toInterface("Not a valid command\n");
			return;
		}
		/* Any command that is correct falls through to here */
		/* Pass message to socket */
		socketI.toSocket(s);
	}
	
	/* The message parse from the socket to the UI */
	/* Using the global state, determine appropriate action */
	/*    to take on a given ACK msg */
	void fromSocketParse( String s ) {
		
		switch(currentMessage) {
			case USER:
				if( s.contains("SUCCESS_WELCOME_TO_SERVER")) {
					toInterface("Welcome to JamIRC " + user + "\n");
				} else if ( s.contains("ERROR_ALREADY_REGISTERED") ){
					user = getUserName( "Name Entered Already Registered : " );
				} else if ( s.contains("ERROR_CANNOT_CHANGE_USERNAME") ) {
					// Do Nothing, get here through weird bug sometimes
					System.out.println("In fromSocketParse(), bug? on case USER");
					// From opening multiple instances of the client on the same machine?
				} else {
					user = getUserName( "Please Enter Your IRC Nickname :" );
				}
				return;
			case JOIN: 
				if( s.contains("SUCCESS_WELCOME_TO_CHANNEL") ||
						s.contains("SUCCESS_NEW_CHANNEL_CREATED")){
					System.out.println(channelToJoin);
					channels.addElement(channelToJoin);
					
				}
				break;
			case LIST:
				/* Do Nothing */
				break;
			case PRIVMSG:
				
				break;
		}
		
		toInterface(s);
	}
	
	
	/* Goal: to get user name, first invoke in initialization */
	/* Continuing invocations until user server accepts user name */
	private String getUserName( String s ) {
		String tempUser;
		
		tempUser = JOptionPane.showInputDialog(null, s , "JAM IRC" , 1);
		
		/* Push to socket */
		try {  this.toSocketParse("USER " + tempUser + "\n" ); } 
		catch ( Exception e1 ) { /* Do nothing */ }
		
		return tempUser;
	}
	
	
	/* Close program */
	private void quit () {
		socketI.close();
		System.exit(0);
	}
	
	/* Messages to be appended to text area */
	public void toInterface( String s ){
		clientOutput.append(s);	
	}
	
	/* Create me some GUI */
	private void createFrame( ){
		topFrame = new JFrame( "JamIRC" );
		contentPane = new JPanel( new BorderLayout() );
		topFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		topFrame.setResizable(false);
		topFrame.setSize(500,500);
		topFrame.setLocationRelativeTo(null);
		
		
		clientOutput = new TextArea("", 20, 50, TextArea.SCROLLBARS_BOTH);
		clientOutput.setEditable(false);
		
		clientInput = new TextField(50);
		clientInput.addActionListener(this);
	
		/* Old Text area channel list */
		//channelList = new TextArea("<jamChannels>\n", 20, 20, TextArea.SCROLLBARS_BOTH);
		//channelList.setEditable(false);
		
		channels = new DefaultListModel();
		channelList = new JList( channels );
		channelList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		channelList.setLayoutOrientation(JList.HORIZONTAL_WRAP);
		channelList.setVisibleRowCount( -1 );
		channelList.addListSelectionListener( this );
		
		JScrollPane channelScroller = new JScrollPane( channelList );
		channelScroller.setPreferredSize(new Dimension(150, 100) );
		
		contentPane.add(clientInput, BorderLayout.SOUTH);
		contentPane.add(clientOutput, BorderLayout.WEST);
		contentPane.add(channelScroller, BorderLayout.EAST);
		
		/* Done, Pack Frame */
		topFrame.add(contentPane);
		topFrame.pack();
		topFrame.setVisible(true);
	}
	
}


