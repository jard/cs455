//package client;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;


public class ClientUI implements ActionListener {
	/* Class Variables */
	/* Frame Components */
	private JFrame topFrame;
	private JPanel lbl;
	private TextArea clientOutput; 
	private TextField clientInput;	
	
	/* Set up frame */
	public ClientUI( ){
		createFrame( );
	}
	
	/* User inputed a string, and hit enter */
	public void actionPerformed( ActionEvent e ){
		if( e.getSource() == clientInput ){
			
			String s = clientInput.getText();
			try {
				Main.MH.fromClient(s);
			} catch (Exception e1) {
				e1.printStackTrace();
			}
			clientInput.setText(null);
		}
		
	}
	
	/* Incoming messages to be appended to text area */
	public void toInterface( String s ){
		clientOutput.append(s);	
	}
	
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
	
}
