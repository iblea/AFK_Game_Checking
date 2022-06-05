package discordbot;

import net.dv8tion.jda.api.entities.ChannelType;
import net.dv8tion.jda.api.events.message.MessageReceivedEvent;

public class BotEvent {

	private Status status;

	public BotEvent() {
		this.status = Status.OFFLINE;
	}

	// 메세지를 받을 때
	public void onMessageReceived(MessageReceivedEvent event) {
		if (event.isFromType(ChannelType.PRIVATE)) {
			System.out.printf("[PM] %s %s\n", event.getAuthor().getName(),
					event.getMessage().getContentDisplay());

		} else {
			System.out.printf("[%s][%s] %s: %s\n", event.getGuild().getName(),
					event.getTextChannel().getName(), event.getMember().getEffectiveName(),
					event.getMessage().getContentDisplay());

		}
	}

	public void setOffline() {
		this.status = Status.OFFLINE;
	}

	public void setOnline() {
		this.status = Status.ONLINE;
	}

	public void printStatus() {
		this.status.print();
	}

	private enum Status {
		OFFLINE(0, "offline"),
		ONLINE(1, "online");

		private final int code;
		private final String msg;

		Status(int code, String msg) {
			this.code = code;
			this.msg = msg;
		}

        public void print() {
            System.out.printf("Current Status is (%d) [%s]", this.code, this.msg);
        }

	}
    
}
