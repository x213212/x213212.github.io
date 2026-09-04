---
title: "Java_battole tetris"
date: "2018-06-24T06:57:00.001+08:00"
updated: "2019-09-13T08:56:04.469+08:00"
permalink: "/2018/06/javabattole-tetris.html"
original_url: "https://x8795278.blogspot.com/2018/06/javabattole-tetris.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6738876518808295097"
tags: ["GameMaker", "Java", "Tutorial", "Projects"]
layout: post
---

## 又是一次課堂專題

在看到了fb小遊戲，因為課堂專題需要所以來做個小練習 可以單人和雙人對打喔!為什麼沒計分系統? 自己寫拉

[![](https://i.imgur.com/flqaKvh.png)](https://i.imgur.com/flqaKvh.png)

[![](https://i.imgur.com/XsuRUSd.png)](https://i.imgur.com/XsuRUSd.png)

單人

[![](https://i.imgur.com/yrjcb81.png)](https://i.imgur.com/yrjcb81.png)

雙人

## battole tetris.code

##

**`SocketClient.java`**

```java
package ti;

import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketException;
import java.io.BufferedOutputStream;

public class SocketClient {
	public String address = "127.0.0.1";// �s�u��ip
	public int port = 1234;// �s�u��port
	Socket client = new Socket();

	public SocketClient(String address, int port, String mes) {

		InetSocketAddress isa = new InetSocketAddress(address, port);
		try {
			client.connect(isa, 80);
			BufferedOutputStream out = new BufferedOutputStream(client.getOutputStream());
			// �e�X�r��
			try {
				client.setTcpNoDelay(true);
				client.setReceiveBufferSize(16);
				client.setSendBufferSize(23);
				client.setKeepAlive(true);
				client.setPerformancePreferences(1, 2, 0);

			} catch (SocketException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}
			out.write(mes.getBytes());
			out.flush();
			out.close();
			out = null;
			client.close();
			client = null;

		} catch (java.io.IOException e) {
			System.out.println("Socket�s�u�����D !");
			System.out.println("IOException :" + e.toString());
		}
	}

	public void set_ipport(String ADDRESS, int port) {
		this.address = ADDRESS;
		this.port = port;

	}

}
```

**`SocketServer.java`**

```java
package ti;

import java.awt.EventQueue;
import java.io.BufferedOutputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;

public class SocketServer extends Thread {
	private boolean running = false;
	private boolean OutServer = false;
	private ServerSocket server;
	private static int ServerPort = 1234;// �n�ʱ���port
	public static String test;
	public static String test2;
	public static String Client_ip = null;

	Thread serverThread;

	public SocketServer() {
		try {

			server = new ServerSocket(ServerPort);

		} catch (java.io.IOException e) {
			System.out.println("Socket�Ұʦ����D !");
			System.out.println("IOException :" + e.toString());
		}
	}

	public void stop_thread() {

		OutServer = false;

	}

	public void run() {
		Socket socket;
		running = false;
		java.io.BufferedInputStream in;

		System.out.println("���A���w�Ұ� !");
		while (!OutServer) {
			System.out.println(ServerPort);
			socket = null;
			try {
				synchronized (server) {

					socket = server.accept();
				}
				try {
					socket.setTcpNoDelay(true);
					socket.setReceiveBufferSize(23);
					socket.setSendBufferSize(16);
					socket.setKeepAlive(true);
					socket.setPerformancePreferences(1, 2, 0);
				} catch (SocketException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				// TimeOut�ɶ�
				socket.setSoTimeout(10000);
				Client_ip = null;
				Client_ip = socket.getInetAddress().getHostAddress();// ����o�e��ip
                //��Ʀ�y�����r��
				System.out.println("���o�s�u : InetAddress = " + socket.getInetAddress().getHostAddress());
				in = new java.io.BufferedInputStream(socket.getInputStream());
				byte[] b = new byte[256];
				String data = "";
				int length;
				while ((length = in.read(b)) > 0)// <=0���ܴN�O�����F
				{
					data += new String(b, 0, length);

				}

				test = (data);

				in.close();
				in = null;
				socket.close();

			} catch (java.io.IOException e) {
				System.out.println("Socket�s�u�����D !");
				System.out.println("IOException :" + e.toString());

			}

		}

	}

	public String getstring() {
		return test;
	}

	public String getstring2() {
		return test2;
	}

	public boolean isRunning() {
		return running;
	}
}
```

**`game.java`**

```java
package ti;

import java.lang.Thread;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.io.IOException;

import javax.swing.*;

import ti.SocketClient;
import ti.SocketServer;

public class game extends JFrame implements MouseListener {
	public final int WIDTH = 800, HEIGHT = 500;
	public JButton button = new JButton("button");
	public static String client_ip = "127.0.0.1";
	public static int server_port = 1234; // server port
	public static int client_port = 1234; // client port
	public SocketServer server;
	public SocketClient client;
	public boolean online = false;
	public boolean isserver = false;
	public static boolean first_data = false;
	public static boolean changeing = false;
	public static boolean single = false;
	public static game tmp;

	public final JMenuItem[] gm = new JMenuItem[5];// ���1
	GamePanel panel = new GamePanel();
	ImageIcon image = new ImageIcon("TetrisImg/single.png");
	ImageIcon image2 = new ImageIcon("TetrisImg/double.png");
	JLabel l1 = new JLabel(image);
	JLabel l2 = new JLabel(image2);
	JPanel mainpanel = new JPanel();
	public static game gui;
	private Component add;

	public game() {
		///
		this.setTitle("Game Test");
		this.setSize(WIDTH, HEIGHT);
		this.setLayout(null);
		this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

		mainpanel.setLayout(new GridLayout(2, 1));

		mainpanel.setSize(250, 130);
		this.setResizable(false);
		this.setLocationRelativeTo(null);
		mainpanel.add(l1);
		mainpanel.add(l2);

		this.add(mainpanel);
		mainpanel.setLocation((WIDTH / 2) - 125, (HEIGHT / 2) - 130);

		l1.addMouseListener(this);
		l2.addMouseListener(this);

		JMenuBar jmb = new JMenuBar();
		gm[0] = new JMenuItem("���A�����e");
		gm[1] = new JMenuItem("�s�u");
		gm[2] = new JMenuItem("�C�����");
		gm[3] = new JMenuItem("�Ȱ�");
		gm[4] = new JMenuItem("�~��");
		JMenu game = new JMenu("�C���ﶵ");
		gm[2].setEnabled(false);
		game.add(gm[0]);
		game.add(gm[1]);
		game.add(gm[2]);
		game.add(gm[3]);
		game.add(gm[4]);
		server = new SocketServer();
		server.start();
		gm[0].addActionListener(new ActionListener() {
			// �ƥ�B�z
			@Override
			public void actionPerformed(ActionEvent e) {

				// server_thread t1 = new server_thread();

				// t1.start();
				try {
					JOptionPane.showMessageDialog(game.this,
							"�z��ip�ثe�O : " + InetAddress.getLocalHost().getHostAddress() + "\n" + "���b���ݹ��s���C\n");
				} catch (HeadlessException | UnknownHostException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}

			}
		});
		gm[1].addActionListener(new ActionListener() {
			// �ƥ�B�z
			@Override

			public void actionPerformed(ActionEvent e) {
				int mType = JOptionPane.INFORMATION_MESSAGE;
				String tmp = JOptionPane.showInputDialog(game.this, "�п�J�n�s�u��ip", "��J", mType);
				JOptionPane.showMessageDialog(game.this, "�z��J���O : " + tmp);
				if (tmp != null)

					client_ip = tmp;
				/*
				 * tmp = JOptionPane.showInputDialog(game.this, "�п�J�n�s�u���ݤf",
				 * "��J", mType); JOptionPane.showMessageDialog(game.this,
				 * "�z��J���O : " + tmp); if (tmp != null) client_port =
				 * Integer.valueOf(tmp);
				 */
				server.Client_ip = client_ip;
				gm[2].setEnabled(true);
				online = true;
				// client_thread t2 = new client_thread();
				// t2.start();*/
			}

		});
		gm[2].addActionListener(new ActionListener() {
			// �ƥ�B�z
			@Override
			public void actionPerformed(ActionEvent e) {
				mainpanel.setVisible(true);
				panel.requestFocus();
				gui.panel.timer.stop();
				gui.panel.timer2.stop();
				gui.panel.setVisible(false);

				setSize(800, 500);

			}
		});
		gm[3].addActionListener(new ActionListener() {
			// �ƥ�B�z
			@Override
			public void actionPerformed(ActionEvent e) {

				gui.panel.timer.stop();
				gui.panel.timer2.stop();

			}
		});
		gm[4].addActionListener(new ActionListener() {
			// �ƥ�B�z
			@Override
			public void actionPerformed(ActionEvent e) {

				gui.panel.timer.start();
				gui.panel.timer2.start();

			}
		});
		jmb.add(game);
		// jmb.add(about);
		this.setJMenuBar(jmb);

		panel.setBounds(0, 0, 800, 500);
		addKeyListener(panel);
		// add(panel);

		////////////////

	}

	public static void main(String[] args) {
		gui = new game();

		gui.setVisible(true);

	}

	public void focus() {
		mainpanel.setVisible(false);
		requestFocus();

		add(panel);
	}

	@Override
	public void mouseClicked(MouseEvent arg0) {
		// TODO Auto-generated method stub
		JLabel sel = (JLabel) arg0.getSource();
		if (sel == l1) {
			this.setSize(400, 500);
			focus();
			panel.setBounds(0, 0, 400, 500);
			single = true;
			gm[2].setEnabled(true);
			gui.panel.setVisible(true);
			isserver = false;
			gui.panel.set_zero();
			gui.panel.timer.start();
			gui.panel.timer2.start();
			focus();
		} else if (sel == l2) {
			this.setSize(800, 500);
			panel.setBounds(0, 0, 800, 500);
			single = false;
			gm[2].setEnabled(true);
			gui.panel.setVisible(true);
			isserver = true;
			gui.panel.set_zero();
			gui.panel.timer.start();
			gui.panel.timer2.start();

			focus();
		}
	}

	@Override
	public void mouseEntered(MouseEvent arg0) {
		// TODO Auto-generated method stub

	}

	@Override
	public void mouseExited(MouseEvent arg0) {
		// TODO Auto-generated method stub

	}

	@Override
	public void mousePressed(MouseEvent arg0) {
		// TODO Auto-generated method stub

	}

	@Override
	public void mouseReleased(MouseEvent arg0) {
		// TODO Auto-generated method stub

	}
	/*
	 * public class server_thread extends Thread {
	 * 
	 * public void run() { // server = new SocketServer(server_port);
	 * 
	 * } }
	 * 
	 * public class client_thread extends Thread {
	 * 
	 * public void run() {
	 * 
	 * client = new SocketClient(client_ip, client_port, null);
	 * 
	 * } }
	 */

	class GamePanel extends JPanel implements KeyListener {

		public int[][] map = new int[10][20];
		public int[][] map2 = new int[10][20];
		private int shapes1[][][] = new int[8][5][18];
		private int shapes2[][][] = new int[8][5][18];

		private int blockType;
		private int turnState;
		private int blockType2;
		private int turnState2;
		private int now_playx = 0;
		private int now_playy = 0;
		private int now_play2x = -100;
		private int now_play2y = -100;
		private int tmpplay2x = -100;
		private int tmpplay2y = -100;
		private int x, y, hold, next, change;
		private int flag = 0;
		public Timer timer = new Timer(500, new TimerListener());
		public Timer timer2 = new Timer(50, new ping());
		private boolean get_alldata = false;
		private Image b1, b2;
		private Image[] color = new Image[7];

		public void set_zero() {
			now_playx = 0;
			now_playy = 0;
			now_play2x = -100;
			now_play2y = -100;
			tmpplay2x = -100;
			tmpplay2y = -100;
			x = 3;
			y = 0;
			for (int i = 0; i < 10; i++)
				for (int j = 0; j < 20; j++) {
					map[i][j] = 0;
					map2[i][j] = 0;
				}

			shapes1 = new int[][][] {
					// I

					{ { 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0 },
							{ 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0 } },
					// s
					{ { 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0 },
							{ 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0 } },
					// z
					{ { 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0 } },
					// j
					{ { 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0 },
							{ 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 } },
					// o
					{ { 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 } },
					// l
					{ { 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0 },
							{ 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 } },
					// t
					{ { 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0 } } };
			shapes2 = new int[][][] {
					// I

					{ { 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0 },
							{ 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0 } },
					// s
					{ { 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0 },
							{ 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0 } },
					// z
					{ { 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0 } },
					// j
					{ { 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0 },
							{ 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 } },
					// o
					{ { 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 } },
					// l
					{ { 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0 },
							{ 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 } },
					// t
					{ { 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0 },
							{ 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
							{ 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0 } } };
		}

		public GamePanel() {

			this.setLayout(null);
			this.setBackground(Color.BLACK);
			b1 = Toolkit.getDefaultToolkit().getImage("TetrisImg/background1.png");
			b2 = Toolkit.getDefaultToolkit().getImage("TetrisImg/background2.png");
			color[0] = Toolkit.getDefaultToolkit().getImage("TetrisImg/blue.png");
			color[1] = Toolkit.getDefaultToolkit().getImage("TetrisImg/green.png");
			color[2] = Toolkit.getDefaultToolkit().getImage("TetrisImg/red.png");
			color[3] = Toolkit.getDefaultToolkit().getImage("TetrisImg/deepblue.png");
			color[4] = Toolkit.getDefaultToolkit().getImage("TetrisImg/yellow.png");
			color[5] = Toolkit.getDefaultToolkit().getImage("TetrisImg/orange.png");
			color[6] = Toolkit.getDefaultToolkit().getImage("TetrisImg/pink.png");
			JLabel NEXT = new JLabel("NEXT");
			NEXT.setFont(new Font("", Font.BOLD, 25));
			NEXT.setBounds(200, 0, 100, 100);
			NEXT.setForeground(Color.white);
			add(NEXT);
			JLabel HOLD = new JLabel("HOLD");
			HOLD.setFont(new Font("", Font.BOLD, 25));
			HOLD.setBounds(300, 0, 100, 100);
			HOLD.setForeground(Color.white);
			add(HOLD);
			initMap();
			newBlock();
			hold = -1;
			next = (int) (Math.random() * 7);

			timer.start();
			timer2.start();
		}

		public void newBlock() {
			flag = 0;

			blockType = next;
			change = 1;
			next = (int) (Math.random() * 7);
			turnState = 0;
			x = 3;
			y = 0;
			if (gameOver(x, y) == 1) {
				initMap();
				// JOptionPane.showMessageDialog(null, "GAME OVER");
			}
			repaint();
		}

		public void setBlock(int x, int y, int type, int state) {
			flag = 1;
			first_data = true;
			for (int i = 0; i < 16; i++) {
				if (shapes1[type][state][i] == 1) {
					map[x + i % 4][y + i / 4] = type + 1;
					System.out.println("shape[" + type + "][" + state + "][" + i + "]");
					System.out.println("map[" + x + i % 4 + "][" + y + i / 4 + "]=" + type + 1);
				}
			}
		}

		public int gameOver(int x, int y) {
			if (blow(x, y, blockType, turnState) == 0)
				return 1;
			return 0;
		}

		public int blow(int x, int y, int type, int state) {
			for (int i = 0; i < 16; i++) {
				if (shapes1[type][state][i] == 1) {
					if (x + i % 4 >= 10 || y + i / 4 >= 20 || x + i % 4 < 0 || y + i / 4 < 0)
						return 0;
					if (map[x + i % 4][y + i / 4] != 0)
						return 0;
				}
			}
			return 1;
		}

		public void rotate() {
			int tmpState = this.turnState;
			tmpState = (tmpState + 1) % 4;
			if (blow(x, y, this.blockType, tmpState) == 1) {
				this.turnState = tmpState;
			}
			repaint();
		}

		public int r_shift() {
			int canShift = 0;
			if (blow(x + 1, y, blockType, turnState) == 1) {
				x++;
				canShift = 1;
			}
			repaint();
			return canShift;
		}

		public void l_shift() {
			if (blow(x - 1, y, blockType, turnState) == 1) {
				x--;
			}
			repaint();
		}

		public int down_shift() {
			int canDown = 0;
			if (blow(x, y + 1, blockType, turnState) == 1) {
				y++;
				canDown = 1;
			}
			repaint();
			if (blow(x, y + 1, blockType, turnState) == 0) {
				// Sleep(500);
				setBlock(x, y, blockType, turnState);
				newBlock();
				delLine();
				canDown = 0;
			}
			return canDown;
		}

		void delLine() {
			int idx = 19, access = 0;
			for (int i = 19; i >= 0; i--) {
				int cnt = 0;
				for (int j = 0; j < 10; j++) {
					if (map[j][i] != 0)
						cnt++;
				}
				if (cnt == 10) {
					access = 1;
					for (int j = 0; j < 10; j++) {
						map[j][i] = 0;
					}
				} else {
					for (int j = 0; j < 10; j++) {
						map[j][idx] = map[j][i];
					}
					idx--;
				}
			}
			/*
			 * if(access == 1) Sleep(500);
			 */
		}

		void initMap() {
			for (int i = 0; i < 10; i++)
				for (int j = 0; j < 20; j++)
					map[i][j] = 0;
		}

		public void paintComponent(Graphics g) {
			super.paintComponent(g);
			if (single == false)
				paintComponent2(g);

			for (int i = 0; i < 10; i++) {
				for (int j = 0; j < 20; j++) {
					if (map[i][j] == 0) {
						if ((i + j) % 2 == 0)
							g.drawImage(b1, i * 15 + 3 * (i + 1) + 0, j * 15 + 3 * (j + 1), null);
						else
							g.drawImage(b2, 0, 0, null);
					} else
						g.drawImage(color[map[i][j] - 1], i * 15 + 3 * (i + 1) + 0, j * 15 + 3 * (j + 1), null);
				}
			}
			if (flag == 0) {
				for (int i = 0; i < 16; i++) {

					if (shapes1[blockType][turnState][i] == 1) {
						g.drawImage(color[blockType], (i % 4 + x) * 18 + 3 + 0, (i / 4 + y) * 18 + 3, null);
						now_playx = x;
						now_playy = y;
					}
				}
			}
			if (hold >= 0) {
				for (int i = 0; i < 16; i++) {
					if (shapes1[hold][0][i] == 1) {
						g.drawImage(color[hold], (i % 4) * 18 + 200, (i / 4) * 18 + 3 + 80, null);
					}
				}
			}
			for (int i = 0; i < 16; i++) {
				if (shapes1[next][0][i] == 1) {

					g.drawImage(color[next], (i % 4) * 18 + 300, (i / 4) * 18 + 3 + 80, null);
				}
			}
		}

		public void paintComponent2(Graphics g) {

			for (int i = 0; i < 10; i++) {
				for (int j = 0; j < 20; j++) {
					if (map2[i][j] == 0) {
						if ((i + j) % 2 == 0)
							g.drawImage(b1, i * 15 + 3 * (i + 1) + 450, j * 15 + 3 * (j + 1), null);
						else
							g.drawImage(b2, 0, 0, null);
					} else
						g.drawImage(color[map2[i][j] - 1], i * 15 + 3 * (i + 1) + 450, j * 15 + 3 * (j + 1), null);
				}
			}
			if (flag == 0) {
				for (int i = 0; i < 16; i++) {
					if (shapes2[blockType2][turnState2][i] == 1) {

						g.drawImage(color[blockType2], (i % 4 + now_play2x) * 18 + 3 + 450,
								(i / 4 + now_play2y) * 18 + 3, null);
					}
				}

			}

		}

		public void keyReleased(KeyEvent e) {
		}

		public void keyTyped(KeyEvent e) {
		}

		public void keyPressed(KeyEvent e) {
			switch (e.getKeyCode()) {
			case KeyEvent.VK_DOWN:
				down_shift();
				break;
			case KeyEvent.VK_UP:
				rotate();
				break;
			case KeyEvent.VK_RIGHT:
				r_shift();
				break;
			case KeyEvent.VK_LEFT:
				l_shift();
				break;
			case KeyEvent.VK_SPACE:
				while (down_shift() == 1)
					;
				break;
			case KeyEvent.VK_SHIFT:
				if (hold >= 0 && change == 1) {
					int tmp;
					tmp = hold;
					hold = blockType;
					blockType = tmp;
					x = 3;
					y = 0;
					change = 0;
				} else if (change == 1) {
					hold = blockType;
					newBlock();

				}
				break;
			}
		}

		void Sleep(int milliseconds) {
			try {
				Thread.sleep(milliseconds);
			} catch (InterruptedException e) {
				System.out.println("Unexcepted interrupt");
				System.exit(0);
			}
		}

		class ping implements ActionListener {

			public void actionPerformed(ActionEvent e) {

				String tmp = "";
				// �۩w�q����ƩM�榡
				if (first_data == true) {
					tmp += "0,";
					for (int i = 0; i < 10; i++)
						for (int j = 0; j < 20; j++)
							tmp += map[i][j] + ",";

					first_data = false;
					// 0,0,0,0,0,0,0,0.....�a�W��
				} else {
					tmp += "1,";
					tmp += blockType + "," + turnState + ",";
					tmp += now_playx + "," + now_playy + ",";
				
					for (int i = 0; i < 16; i++)
						tmp += shapes1[blockType][turnState][i] + ",";

				}
				// 1,0,0,0,0,0,0,0.....�ѤW��
				// �ˬdserver �O�_����ƶǤJ
				// �����ܧ�����ip
				String change_ip = null;
				if (server.Client_ip != null)
					// �o�@��N�O�qserver socket���ip
					change_ip = server.Client_ip;
				else
					change_ip = null;
				//
                //�p�G�����o��ip����
				if (change_ip != null) {
					System.out.println(tmp);
                //client socket ���server��client_ip �@���ڭn�o�e���ؼ�ip�]�N�Ochange_ip 
			    // tmp �O�n�o�e�����
					client = new SocketClient(change_ip, client_port, tmp);

					
			//server������ư��ѽX
					System.out.println(server.getstring());
					if (server.getstring() != null && server.getstring() != "") {

						String[] tokens = server.getstring().split(",");
						int x = 0, count = 0;
						int change = -1;
					
						for (String token : tokens) {
							if (change == -1)
								change = Integer.valueOf(token);
							else if (change == 0) {
								map2[x][count] = Integer.valueOf(token);
								if (count == 19) {
									count = 0;
									x++;

								} else
									count++;
							} else if (change == 1) {
								if (x == 0)
									blockType2 = Integer.valueOf(token);
								else if (x == 1)
									turnState2 = Integer.valueOf(token);
								else if (x == 2)
									now_play2x = Integer.valueOf(token);
								else if (x == 3)
									now_play2y = Integer.valueOf(token);

								else if (x >= 4) {
									shapes2[blockType2][turnState2][count] = Integer.valueOf(token);
									count++;
								}

								x++;
							}

						}
						repaint();

					}
				}
		
			}
		}

		class TimerListener implements ActionListener {
			public void actionPerformed(ActionEvent e) {
				repaint();
				down_shift();
				// System.out.println(server.get_data);

			}
		}
	}

}
```
