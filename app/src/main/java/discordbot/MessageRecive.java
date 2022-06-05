package discordbot;

import net.dv8tion.jda.api.entities.Message;
import net.dv8tion.jda.api.entities.MessageChannel;
import net.dv8tion.jda.api.events.message.MessageReceivedEvent;

public class MessageRecive {
	private static final String MESSAGE_PONG = "Pong!";
	private static final String PING_COMMAND = "!ping";

	private MessageReceivedEvent event;

	public MessageRecive(MessageReceivedEvent event) {
		this.event = event;
	}

	public boolean messageReceive() {
		Message msg = event.getMessage();

		if (isPingCommand(msg)) {
			sendPingMsg(MESSAGE_PONG);
			return true;
		}

		return false;
	}

	private boolean isPingCommand(Message msg) {
		// TODO: 대소문자 구분, 뒤에 공백은 어떻게?
		return msg.getContentRaw()
				.equals(PING_COMMAND);
	}

	private void sendPingMsg(String msg) {
		MessageChannel channel = event.getChannel();
		long time = System.currentTimeMillis();
		channel.sendMessage(msg) /* => RestAction<Message> */
				.queue(response /* => Message */ -> {
					response.editMessageFormat("Pong: %d ms", System.currentTimeMillis() - time)
							.queue();
				});
	}
}
