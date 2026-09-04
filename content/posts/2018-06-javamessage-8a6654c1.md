---
title: "Java_message"
date: "2018-06-24T06:46:00.005+08:00"
updated: "2019-09-13T08:56:03.031+08:00"
permalink: "/2018/06/javamessage.html"
original_url: "https://x8795278.blogspot.com/2018/06/javamessage.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2730190660230660722"
tags: ["Java", "Tutorial", "Projects"]
layout: post
---

## 即時通

## --- 相信大家都有用過Yahoo即時通，那時候還有一個漏洞呢，輸入超過很多字元會讓對方斷線，那麼我們來土炮一個來看看吧! [![](https://hackpad-attachments.s3.amazonaws.com/hackpad.com_vDkBw7qGbac_p.517873_1481408899524_%E5%9C%96%E7%89%87.png)](https://hackpad-attachments.s3.amazonaws.com/hackpad.com_vDkBw7qGbac_p.517873_1481408899524_%E5%9C%96%E7%89%87.png) ![](https://hackpad-attachments.s3.amazonaws.com/hackpad.com_vDkBw7qGbac_p.517873_1481408938448_%E5%9C%96%E7%89%87.png) ![](https://hackpad-attachments.s3.amazonaws.com/hackpad.com_vDkBw7qGbac_p.517873_1481408976557_%E5%9C%96%E7%89%87.png) message.code

##

**`main.java`**

```java
package messager;

import java.awt.EventQueue;
import javax.swing.JOptionPane;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.border.EmptyBorder;
import javax.swing.JTree;
import javax.swing.GroupLayout;
import javax.swing.GroupLayout.Alignment;
import javax.swing.JButton;
import javax.swing.LayoutStyle.ComponentPlacement;
import javax.swing.JTextField;
import java.awt.Font;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JMenu;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import javax.swing.AbstractAction;
import javax.swing.Action;
import javax.swing.tree.DefaultTreeModel;

import javax.swing.tree.DefaultMutableTreeNode;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import javax.swing.JScrollPane;

import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;

import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import javax.swing.JTabbedPane;

public class main extends JFrame {
	
	public String IP;
	public static String data_ip;
	public static String local_ip = null;
	public String send_ip = null;
	public int send_port = 9000;
	public String msg;
	private JPanel contentPane;
	private JTextField textField;
	private final Action action = new SwingAction();
	public static String user;
	public static String password;
	public String mysqlback_friends = null;
	public SocketServer task = new SocketServer();
	public Thread t = new Thread(task); // 產生Thread物件

	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {

					main frame = new main(user, password, data_ip,local_ip);
					frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});

	}

	public void mysql_exc(String exc) {
		try {
			Class.forName("com.mysql.jdbc.Driver");
			Connection con = DriverManager.getConnection(
					"jdbc:mysql://"+this.data_ip+"/messager?useUnicode=true&characterEncoding=UTF8", "root",
					"x123456789");
			Statement st = con.createStatement();
			ResultSet rs = st.getResultSet();
			st.execute(exc);
			rs = st.getResultSet();
		} catch (ClassNotFoundException o) {
			System.out.println("DriverClassNotFound :" + o.toString());
		} // 有可能會產生sqlexception
		catch (SQLException x) {
			System.out.println("Exception :" + x.toString());
		}
	}

	public main(String user, String password, String data_ip,String local_ip) {
		this.user = user;
		this.password = password;
		this.data_ip = data_ip;
		this.local_ip= local_ip;
		JMenuBar menuBar = new JMenuBar();
		JButton btnNewButton = new JButton("+");
		JPanel panel = new JPanel();
		JTabbedPane tabbedPane = new JTabbedPane(JTabbedPane.TOP);
		String tmp2 = mysql_search("SELECT * FROM user where id='" + user + "' &&" + " password='" + password + "'","friends");
		JTree tree = new JTree();
		JScrollPane scrollPane = new JScrollPane();
		JMenu mnNewMenu = new JMenu("即時通");
		JMenuItem item = new JMenuItem("登出");
		mysql_exc("UPDATE user SET port = '"+send_port+"' where id='" + user + "' &&" + " password='" + password + "'");


		item.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				mysql_exc("UPDATE user SET online = '0' where id='" + user + "' &&" + " password='" + password + "'");
				System.exit(0);
			}
		});
		mysql_exc("UPDATE user SET ip = '"+local_ip+"' where id='" + user + "' &&" + " password='" + password + "'");
		setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
		setBounds(100, 100, 249, 414);


		setJMenuBar(menuBar);

		menuBar.add(mnNewMenu);
		contentPane = new JPanel();
		contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
		setContentPane(contentPane);

		mnNewMenu.add(item);



		btnNewButton.setFont(new Font("微軟正黑體", Font.PLAIN, 9));

		textField = new JTextField();
		textField.setColumns(10);

		
		JScrollPane scrollPane_1 = new JScrollPane();

		
		JTree tree_1 = new JTree();
		tree_1.addMouseListener(new MouseAdapter() {
			@Override
			public void mouseClicked(MouseEvent e) {

					DefaultMutableTreeNode node = (DefaultMutableTreeNode) tree_1.getLastSelectedPathComponent();
					if (node == null)
						return;
					Object nodeInfo = node.getUserObject();// 通訊點入那個當client
					if (!nodeInfo.toString().equals("好友清單")) {
						IP = nodeInfo.toString();
						new SocketClient();
					
				}
			}
		});
	
		scrollPane_1.setViewportView(tree_1);
		btnNewButton.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				DefaultTreeModel model = (DefaultTreeModel) tree_1.getModel();
				DefaultMutableTreeNode root = (DefaultMutableTreeNode) model.getRoot();
				if (!textField.getText().trim().equals("")) {
					root.add(new DefaultMutableTreeNode(textField.getText()));
					model.reload();
				}

				else {
					JOptionPane.showMessageDialog(null, "fuck dick");
				}

			}
		});
		GroupLayout gl_panel = new GroupLayout(panel);
				
				JTabbedPane tabbedPane_1 = new JTabbedPane(JTabbedPane.TOP);
				GroupLayout gl_contentPane = new GroupLayout(contentPane);
				gl_contentPane.setHorizontalGroup(
					gl_contentPane.createParallelGroup(Alignment.LEADING)
						.addGroup(gl_contentPane.createSequentialGroup()
							.addGap(7)
							.addComponent(panel, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
							.addGap(5)
							.addComponent(textField, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
							.addGap(5)
							.addComponent(btnNewButton)
							.addGap(5)
							.addComponent(tabbedPane, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
							.addContainerGap(69, Short.MAX_VALUE))
						.addComponent(tabbedPane_1, GroupLayout.DEFAULT_SIZE, 261, Short.MAX_VALUE)
				);
				gl_contentPane.setVerticalGroup(
					gl_contentPane.createParallelGroup(Alignment.LEADING)
						.addGroup(gl_contentPane.createSequentialGroup()
							.addGap(5)
							.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
								.addGroup(gl_contentPane.createSequentialGroup()
									.addGap(6)
									.addComponent(panel, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE))
								.addComponent(textField, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
								.addComponent(btnNewButton)
								.addGroup(gl_contentPane.createSequentialGroup()
									.addGap(8)
									.addComponent(tabbedPane, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)))
							.addPreferredGap(ComponentPlacement.UNRELATED)
							.addComponent(tabbedPane_1, GroupLayout.DEFAULT_SIZE, 291, Short.MAX_VALUE))
				);
				tabbedPane_1.addTab("New tab", null, scrollPane_1, null);

				tree_1.setModel(new DefaultTreeModel(
					new DefaultMutableTreeNode("廢物群") {
						{
							String tmp = tmp2;
							String[] tokens = tmp.split(",");
							for (String token : tokens) {
add(new DefaultMutableTreeNode(token));
							
							}
						}
					}
				));
				this.setVisible(true);
				contentPane.setLayout(gl_contentPane);
				t.start();
	}
	
	public String mysql_search(String exc,String label) {
		String tmp = null;

		try {
			Class.forName("com.mysql.jdbc.Driver");
			// 註冊driver
			Connection con = DriverManager.getConnection(
					"jdbc:mysql://"+this.data_ip+"/messager?useUnicode=true&characterEncoding=UTF8", "root",
					"x123456789");
			// 取得connection
			Statement st = con.createStatement();
			st.execute(exc);
			ResultSet rs = st.getResultSet();
			while (rs.next()) {
				tmp = rs.getString(label);

			}

			if (tmp == null) {
				JOptionPane.showMessageDialog(null, "與伺服器取得資料失敗!");
			} else
				return tmp;
		} catch (ClassNotFoundException o) {
			System.out.println("DriverClassNotFound :" + o.toString());
		} // 有可能會產生sqlexception
		catch (SQLException x) {

			System.out.println("Exception :" + x.toString());
		}
		return tmp;
	}

	private class SwingAction extends AbstractAction {
		public SwingAction() {
			putValue(NAME, "SwingAction");
			putValue(SHORT_DESCRIPTION, "Some short description");
		}

		public void actionPerformed(ActionEvent e) {
		}
	}

	public class SocketServer extends java.lang.Thread {

		private boolean OutServer = false;
		private ServerSocket server;
		private final int ServerPort = 10000;// 要監控的port

		public SocketServer() {
			try {

				server = new ServerSocket(ServerPort);

			} catch (java.io.IOException e) {
				System.out.println("Socket啟動有問題 !");
				System.out.println("IOException :" + e.toString());
			}
		}

		public void run() {
			InputStreamReader inSR = null;
			OutputStreamWriter outSW = null;
			Socket socket;
			java.io.BufferedInputStream in;

			System.out.println("監聽伺服器已啟動 !");
			while (!OutServer) {
				socket = null;
				try {

					synchronized (server) {

						socket = server.accept();
					}
					System.out.println("取得連線 : InetAddress = " + socket.getInetAddress());
					// TimeOut時間
					socket.setSoTimeout(15000);
					inSR = new InputStreamReader(socket.getInputStream(), "UTF-8");
					BufferedReader br = new BufferedReader(inSR);

					in = new java.io.BufferedInputStream(socket.getInputStream());
					byte[] b = new byte[1024];
					String data = "";
					int length;
					while ((length = in.read(b)) > 0)// <=0的話就是結束了
					{
						data += new String(b, 0, length, "big5");// 注意編碼
					}
					String tmp = data;
					String[] tokens = data.split(":");
					//String tmp3 = mysql_search("SELECT * FROM user where id='" +Integer.valueOf(tokens[1])+ "'","port");
					//if(Integer.valueOf(tmp3 )>send_port)
					send_port=Integer.valueOf(Integer.valueOf(tokens[1]));
					send_ip = tokens[0];
			   
	
					new_message(send_ip, send_port);
					String tmp2 = "確實收到資料" + send_ip + ":" + tokens[1];
					System.out.print(tmp2);
		
					in.close();
					in = null;
					socket.close();
				

				} catch (java.io.IOException e) {
					System.out.println("Socket連線有問題 !");

					System.out.println("IOException :" + e.toString());

				}

			}
			server = null;
		}

		public void stopThread() throws IOException {
			server.close();
			this.OutServer = true;
		}
	}

	public void new_message(String ip, int port) {
		msg test = new msg(ip,port);
		test.setTitle(ip);
		send_port++;
	}

	public class SocketClient extends java.lang.Thread {

		private String address = IP;// 連線的ip
		private int port = 10000;// 連線的port

		public SocketClient() {

			Socket client = new Socket();

			InetSocketAddress isa = new InetSocketAddress(this.address, this.port);
			try {
				client.connect(isa,10000);
				BufferedOutputStream out = new BufferedOutputStream(client.getOutputStream());
				// 送出字串
		
		
				String tmp =local_ip+ ":" + String.valueOf(send_port);
				System.out.print("已向對方發送請求連接需求"+tmp);
				out.write(tmp.getBytes());
				new_message(IP, Integer.valueOf(send_port));
				out.flush();
				out.close();
				out = null;
				client.close();
				client = null;
				

			} catch (java.io.IOException e) {
				System.out.println("Socket連線有問題 !");
				System.out.println("IOException :" + e.toString());
			}
		}

	}
}
```

**`msg.java`**

```java
package messager;

import java.awt.BorderLayout;
import java.awt.EventQueue;
import java.awt.Frame;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.border.EmptyBorder;

import java.util.Date;
import java.text.SimpleDateFormat;
import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.DefaultListModel;
import javax.swing.GroupLayout;
import javax.swing.GroupLayout.Alignment;
import javax.swing.JTextField;
import javax.swing.LayoutStyle.ComponentPlacement;
import javax.swing.JButton;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.io.BufferedOutputStream;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import javax.swing.JTextPane;
import javax.swing.ScrollPaneConstants;
import javax.swing.DropMode;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.Font;
import java.awt.event.InputMethodListener;
import java.awt.event.InputMethodEvent;

public class msg extends JFrame {

	public boolean start = false;
	public SocketServer task;
	public Thread t;// ����Thread����
	public static String IP;
	public static int send_port;
	public String msg;
	java.io.BufferedInputStream in;
	private JPanel contentPane;
	private JTextField textField;
	public static DefaultListModel model = new DefaultListModel();
	public static DefaultListModel model2 = new DefaultListModel();
	public JList list = new JList(model);
	public JTextPane textPane = new JTextPane();
	public JScrollPane scrollPane = new JScrollPane();
	public Frame src;
	private final JButton btnNewButton_1 = new JButton("~");
	/**
	 * Launch the application.
	 */

	/**
	 * Create the frame.
	 */
	public String getDateTime() {
		SimpleDateFormat sdFormat = new SimpleDateFormat("yyyy/MM/dd hh:mm:ss");
		Date date = new Date();
		String strDate = sdFormat.format(date);
		// System.out.println(strDate);
		return strDate;
	}

	public msg(String ip, int port) {
		this.IP = ip;
		this.send_port = port;
		addWindowListener(new WindowAdapter() {
			@Override
			public void windowClosing(WindowEvent arg0) {

				src.dispose();

			}

			@Override
			public void windowOpened(WindowEvent e) {
				src = (Frame) e.getSource();
			}
		});
		setResizable(false);

		setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
		setBounds(100, 100, 482, 399);
		contentPane = new JPanel();
		contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
		setContentPane(contentPane);

		textField = new JTextField();
		textField.addKeyListener(new KeyAdapter() {
			@Override
			public void keyPressed(KeyEvent e) {
				 if(e.getKeyCode() == KeyEvent.VK_ENTER) {
					 new SocketClient( textField.getText());
					 textField.setText("");;
				   }
			}
		});

		textField.setColumns(10);

		JButton btnNewButton = new JButton("\u9001\u51FA");
		btnNewButton.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {

				new SocketClient( textField.getText());
			}
		});
		GroupLayout gl_contentPane = new GroupLayout(contentPane);
		gl_contentPane.setHorizontalGroup(
			gl_contentPane.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_contentPane.createSequentialGroup()
					.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING, false)
						.addGroup(gl_contentPane.createSequentialGroup()
							.addContainerGap()
							.addComponent(textField, GroupLayout.PREFERRED_SIZE, 309, GroupLayout.PREFERRED_SIZE)
							.addGap(18)
							.addComponent(btnNewButton_1, GroupLayout.PREFERRED_SIZE, 56, GroupLayout.PREFERRED_SIZE)
							.addPreferredGap(ComponentPlacement.RELATED)
							.addComponent(btnNewButton))
						.addGroup(gl_contentPane.createSequentialGroup()
							.addGap(2)
							.addComponent(scrollPane)))
					.addGap(496)
					.addComponent(list, GroupLayout.PREFERRED_SIZE, 94, GroupLayout.PREFERRED_SIZE))
		);
		gl_contentPane.setVerticalGroup(
			gl_contentPane.createParallelGroup(Alignment.TRAILING)
				.addGroup(gl_contentPane.createSequentialGroup()
					.addContainerGap()
					.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
						.addComponent(list, Alignment.TRAILING, GroupLayout.PREFERRED_SIZE, 233, GroupLayout.PREFERRED_SIZE)
						.addGroup(Alignment.TRAILING, gl_contentPane.createSequentialGroup()
							.addComponent(scrollPane, GroupLayout.DEFAULT_SIZE, 296, Short.MAX_VALUE)
							.addPreferredGap(ComponentPlacement.RELATED)
							.addGroup(gl_contentPane.createParallelGroup(Alignment.BASELINE)
								.addComponent(btnNewButton_1, GroupLayout.PREFERRED_SIZE, 35, GroupLayout.PREFERRED_SIZE)
								.addComponent(btnNewButton, GroupLayout.PREFERRED_SIZE, 38, GroupLayout.PREFERRED_SIZE)
								.addComponent(textField, GroupLayout.PREFERRED_SIZE, 54, GroupLayout.PREFERRED_SIZE))
							.addContainerGap())))
		);

		scrollPane.setViewportView(textPane);
		textPane.setFont(new Font("Consolas", Font.PLAIN, 11));
		
				textPane.setContentType("text/html");
		btnNewButton_1.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				new SocketClient( "shake");
			}
		});
		contentPane.setLayout(gl_contentPane);

		setVisible(true); // -->��� Frame2
		start_server();

	}

	public void start_server() {
		task = new SocketServer();
		t = new Thread(task);
		t.start(); // �}�l����t.run()
	}

	public static void main(String[] args) {

		EventQueue.invokeLater(new Runnable() {

			public void run() {
				try {

					msg frame = new msg(IP, send_port);
					frame.setVisible(true);

				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	public class SocketServer extends java.lang.Thread {

		private boolean OutServer = false;
		private ServerSocket server;
		private int ServerPort = send_port;// �n�ʱ���port

		public SocketServer() {
			try {

				server = new ServerSocket(ServerPort);

			} catch (java.io.IOException e) {
				System.out.println("Socket�Ұʦ����D !");
				System.out.println("IOException :" + e.toString());
			}
		}

		public void run() {
			InputStreamReader inSR = null;
			OutputStreamWriter outSW = null;
			Socket socket;
			java.io.BufferedInputStream in;
			System.out.println("\n���A���w�Ұ� !");
			System.out.println("IP:" + IP + " Port:" + send_port + "\n���A���w�]�w����");

			while (!OutServer) {

				socket = null;
				try {

					synchronized (server) {

						socket = server.accept();
					}
					System.out.println("�����s�u : InetAddress = " + socket.getInetAddress());
					//

					socket.setSoTimeout(15000);
					inSR = new InputStreamReader(socket.getInputStream(), "UTF-8");
					BufferedReader br = new BufferedReader(inSR);

					in = new java.io.BufferedInputStream(socket.getInputStream());
					byte[] b = new byte[1024];
					String data = "";
					int length;
					while ((length = in.read(b)) > 0)// <=0���ܴN�O�����F
					{
						data += new String(b, 0, length, "big5");
					}

					model.addElement("<" + IP + getDateTime() + "> :" + data);
					get_msg();
					System.out.println(IP + data);
					in.close();
					in = null;
					socket.close();

				} catch (java.io.IOException e) {

					System.out.println("Socket�s�u�����D !");
					System.out.println("IOException :" + e.toString());

				}

			}

		}

	}

	public class SocketClient extends java.lang.Thread {
		private String address = IP;// �s�u��ip
		private int port = send_port;// �s�u��port

		public SocketClient(String tmp) {

			Socket client = new Socket();
			InetSocketAddress isa = new InetSocketAddress(this.address, this.port);
			try {
				client.connect(isa, 10000);
				BufferedOutputStream out = new BufferedOutputStream(client.getOutputStream());
				// �e�X�r��

				model.addElement("<" + "�ڻ�" + getDateTime() + "> :" + tmp);
				get_msg();
				out.write(tmp.getBytes());
				out.flush();
				out.close();
				out = null;
				client.close();
				client = null;

			} catch (java.io.IOException e) {
				System.out.println(this.address);
				System.out.println(this.port);
				System.out.println("Socket�s�u�����D !");
				System.out.println("IOException :" + e.toString());
			}
		}

	}

	public String get_msg() throws IOException {
		String tmp = "<html><head>" + " <meta charset=" + '"' + "big-5" + '"' + " /></head>\n";

		for (int i = 0; i < model.size(); i++) {
			tmp += model.get(i).toString() + "<br>";
			if (model.size() - 1 == i) {
				if (model.get(i).toString().indexOf(":shake") != -1) {
					shake();

				}

			}
		}
		tmp += "</body></html>";
		String url = "file:///C:/test.gif";
		tmp = (tmp.replace(":QQ", "<img src=" + url + "></img>"));
		tmp = (tmp.replace(":shake", "</p><font color=" + '"' + "red" + '"' + ">�o�e�_��</font>"));

		tmp += "/n";
		System.out.print(tmp);

		textPane.setText(tmp);
		textPane.setCaretPosition(textPane.getDocument().getLength()); 
		textPane.repaint();
		return tmp;

	}

	public void shake() {

		// TODO Auto-generated method stub
		int or_x = this.location().x;
		int or_y = this.location().y;
		this.setLocation(or_x, or_y + 10);
		try {
			Thread.sleep(30);
			this.setLocation(or_x + 20, or_y + 20);
			Thread.sleep(30);
			this.setLocation(or_x, or_y + 0);
			Thread.sleep(30);
			this.setLocation(or_x + 20, or_y + 0);
			Thread.sleep(30);
			this.setLocation(or_x, or_y + 20);
			Thread.sleep(30);
			this.setLocation(or_x, or_y + 0);
			Thread.sleep(1000);

		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		this.setLocation(or_x, or_y);

	}
}
```

**`test.java`**

```java
package messager;

import java.awt.BorderLayout;
import java.awt.EventQueue;
import java.awt.Image;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.border.EmptyBorder;
import javax.swing.JButton;
import javax.swing.SwingConstants;
import javax.swing.UIManager;
import javax.swing.UnsupportedLookAndFeelException;

import java.awt.FlowLayout;
import java.awt.Frame;
import java.awt.GridLayout;
import javax.swing.GroupLayout;
import javax.swing.GroupLayout.Alignment;
import javax.swing.ImageIcon;
import javax.swing.JTextField;
import javax.swing.LayoutStyle.ComponentPlacement;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPasswordField;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import javax.swing.event.AncestorListener;

import messager.msg.SocketClient;

import java.awt.Graphics;
import java.io.File;
import java.net.InetAddress;
import java.net.UnknownHostException;

import javax.swing.event.AncestorEvent;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.Color;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;

public class test extends JFrame {

	private JPanel contentPane;
	private JTextField txtX;
	private JPasswordField passwordField;
	public	InetAddress myComputer = InetAddress.getLocalHost() ;
	// linux �ƾڮw
	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {

		EventQueue.invokeLater(new Runnable() {

			public void run() {
				try {
					test frame = new test();
					frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the frame.
	 * @throws UnknownHostException 
	 * 
	 * @throws UnsupportedLookAndFeelException
	 * @throws IllegalAccessException
	 * @throws InstantiationException
	 * @throws ClassNotFoundException
	 */

	public test() throws UnknownHostException {
		setResizable(false);

		// UIManager.setLookAndFeel("com.sun.java.swing.plaf.windows.WindowsLookAndFeel");
		addWindowListener(new WindowAdapter() {
			@Override
			public void windowClosing(WindowEvent e) {
				Frame src = (Frame) e.getSource();
				src.dispose();
			}
		});
		JButton btnNewButton = new JButton("\u767B\u5165");
		JLabel lblNewLabel = new JLabel("\u5E33\u865F");
		JLabel lblNewLabel_2 = new JLabel("");
		JLabel lblNewLabel_1 = new JLabel("\u5BC6\u78BC");
		JLabel lblNewLabel_3 = new JLabel("");
		setTitle("Messager");
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(100, 100, 241, 532);
		contentPane = new JPanel();
		contentPane.setBackground(new Color(255, 255, 255));
		contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
		setContentPane(contentPane);
		this.setVisible(false);
		btnNewButton.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				 login();
			}
		});

		btnNewButton.setHorizontalAlignment(SwingConstants.TRAILING);

		txtX = new JTextField();
		txtX.addKeyListener(new KeyAdapter() {
			@Override
			public void keyPressed(KeyEvent e) {
				 if(e.getKeyCode() == KeyEvent.VK_ENTER) {
					 login();
					 txtX.setText("");;
				   }
			}
		});
		txtX.setText("x213212");
		txtX.setColumns(10);


		passwordField = new JPasswordField();
		passwordField.addKeyListener(new KeyAdapter() {
			@Override
			public void keyPressed(KeyEvent e) {
				 if(e.getKeyCode() == KeyEvent.VK_ENTER) {
					 login();
					 passwordField.setText("");;
				   }
			}
		});
		
		
		passwordField.setToolTipText("");

		lblNewLabel_3.setVerticalAlignment(SwingConstants.BOTTOM);
		lblNewLabel_3.addAncestorListener(new AncestorListener() {
			public void ancestorAdded(AncestorEvent event) {
				ImageIcon icon = new ImageIcon("src\\HOO.jpg");
				lblNewLabel_3.setIcon(icon);
			}
			public void ancestorMoved(AncestorEvent event) {
			}
			public void ancestorRemoved(AncestorEvent event) {
			}
		});
		
		GroupLayout gl_contentPane = new GroupLayout(contentPane);
		gl_contentPane.setHorizontalGroup(
			gl_contentPane.createParallelGroup(Alignment.TRAILING)
				.addGroup(gl_contentPane.createSequentialGroup()
					.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
						.addGroup(gl_contentPane.createSequentialGroup()
							.addContainerGap()
							.addComponent(lblNewLabel_3, GroupLayout.DEFAULT_SIZE, 195, Short.MAX_VALUE))
						.addGroup(gl_contentPane.createSequentialGroup()
							.addContainerGap()
							.addGroup(gl_contentPane.createParallelGroup(Alignment.LEADING)
								.addGroup(gl_contentPane.createSequentialGroup()
									.addComponent(lblNewLabel)
									.addGap(132))
								.addComponent(lblNewLabel_1)
								.addComponent(txtX, GroupLayout.DEFAULT_SIZE, 195, Short.MAX_VALUE)
								.addComponent(passwordField, GroupLayout.DEFAULT_SIZE, 195, Short.MAX_VALUE)))
						.addGroup(gl_contentPane.createSequentialGroup()
							.addGap(29)
							.addComponent(lblNewLabel_2))
						.addGroup(gl_contentPane.createSequentialGroup()
							.addGap(79)
							.addComponent(btnNewButton)))
					.addContainerGap())
		);
		gl_contentPane.setVerticalGroup(
			gl_contentPane.createParallelGroup(Alignment.TRAILING)
				.addGroup(gl_contentPane.createSequentialGroup()
					.addContainerGap()
					.addComponent(lblNewLabel_3, GroupLayout.PREFERRED_SIZE, 185, GroupLayout.PREFERRED_SIZE)
					.addPreferredGap(ComponentPlacement.RELATED, 81, Short.MAX_VALUE)
					.addComponent(lblNewLabel)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(txtX, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
					.addGap(14)
					.addComponent(lblNewLabel_1)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(passwordField, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
					.addGap(45)
					.addComponent(lblNewLabel_2)
					.addGap(22)
					.addComponent(btnNewButton, GroupLayout.PREFERRED_SIZE, 34, GroupLayout.PREFERRED_SIZE)
					.addContainerGap())
		);

		contentPane.setLayout(gl_contentPane);
	}
	public void login()
	{String mysqlback_id = null, mysqlback_pas = null;

	try {
		Class.forName("com.mysql.jdbc.Driver");
		// ���Udriver

		// linux �ƾڮw
		Connection con = DriverManager.getConnection(

				"jdbc:mysql://"+"192.168.153.130" +"/messager?useUnicode=true&characterEncoding=UTF8"
				//"jdbc:mysql://192.168.153.130/messager?useUnicode=true&characterEncoding=UTF8"
				, "root",
		
				"x123456789");
		// ���oconnection
		Statement st = con.createStatement();

		st.execute("SELECT * FROM user where id='" + txtX.getText() + "' &&" + " password='"
				+ passwordField.getText() + "'");
		ResultSet rs = st.getResultSet();
		while (rs.next()) {
			mysqlback_id = rs.getString("id");
			mysqlback_pas = rs.getString("password");

		}

		if (mysqlback_id == null && mysqlback_pas == null) {
			JOptionPane.showMessageDialog(null, "�b���αK�X���~�Э��s����!");

		} else {
                                                 ///myComputer.getHostAddress()
			new main(mysqlback_id,mysqlback_pas,"192.168.153.130","192.168.153.1");
			dispose();
			con.close();
		}
	} catch (ClassNotFoundException e) {
		JOptionPane.showMessageDialog(null, "�P���A�����o��ƥ���!");
		System.out.println("DriverClassNotFound :" + e.toString());
	} // ���i��|����sqlexception
	catch (SQLException x) {

		System.out.println("Exception :" + x.toString());
	} 
}
}
```
