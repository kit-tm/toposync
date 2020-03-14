import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.Date;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class PeriodicUDP {
	private static int maxCount;
	private static int count = 0;
	private static DatagramSocket sock;
	private static DatagramPacket packet;
	private static volatile boolean finished = false;

	private static byte[] longToBytes(long l) {
		byte[] result = new byte[Long.BYTES];
		for (int i = 7; i >= 0; i--) {
			result[i] = (byte) (l & 0xFF);
			l >>= Byte.SIZE;
		}
		return result;
	}

	/**
	 * 
	 * @param args 0: sip, 1: dip, 2: message size, 3: amount of packets, 4: packets per second
	 * @throws SocketException
	 * @throws UnknownHostException
	 */
	public static void main(String[] args) throws SocketException, UnknownHostException {
		InetAddress source = InetAddress.getByName(args[0]);
		InetAddress destination = InetAddress.getByName(args[1]);
		// byte[] message = new byte[Integer.valueOf(args[2])];
		sock = new DatagramSocket(6667, source);

		maxCount = Integer.valueOf(args[3]);
		double packetsPerMilliSecond = (double)Integer.valueOf(args[4]) / 1000;
		long periodInMs = (long) ((float)1 / packetsPerMilliSecond);
		System.out.println("sending packet every: " + periodInMs + " ms.");

		ScheduledExecutorService schedule = Executors.newScheduledThreadPool(1);
		System.out.println("started");
		schedule.scheduleAtFixedRate(new Runnable() {
			@Override
			public void run() {
				if (count < maxCount) {
					try {
						long time = System.currentTimeMillis();
						byte[] message = longToBytes(time);
						packet = new DatagramPacket(message, message.length, destination, 6666);
						sock.send(packet);
						count++;
					} catch (IOException e) {
						e.printStackTrace();
					}
				} else {
					finished = true;
				}
			}
		}, 0, periodInMs, TimeUnit.MILLISECONDS);

		while(!finished) {

		}

		schedule.shutdown();

		sock.close();

		System.out.println("done sending");

	}
}
