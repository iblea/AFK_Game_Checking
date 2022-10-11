package discordbot;

import java.util.Arrays;

import net.dv8tion.jda.api.entities.MessageChannel;
import net.dv8tion.jda.api.events.message.MessageReceivedEvent;

public class BotCommand {

	private MessageReceivedEvent event;

	public BotCommand(MessageReceivedEvent event) {
		this.event = event;
	}

	public int botCommandContent(String msg) {
		// msg를 아예 받지 못함
		if (msg.length() < 1) {
			return -1;
		}

		if (msg.charAt(0) != '!') {
			return 0;
		}

		msg = msg.substring(1);
		System.out.println(msg);

		return COMMAND_TYPE.calculate(msg, this.event);
	}

	public void cmdContent(MessageReceivedEvent event) {

	}

	public enum COMMAND_TYPE {
		HELP("help") {
			@Override
			public int apply(String msg, MessageReceivedEvent event) {
				String help_content = "help command test";
				MessageChannel channel = event.getChannel();
				channel.sendMessage(help_content).queue();
				return 1;
			}
		},
		USER_ADD("gcadd") {
			@Override
			public int apply(String msg, MessageReceivedEvent event) {

				return 2;
			}
		},
		USER_DEL("gcdel") {
			@Override
			public int apply(String msg, MessageReceivedEvent event) {

				return 3;
			}
		},

		;

		private final String command_text;

		private COMMAND_TYPE(String command_text) {
			this.command_text = command_text;
		}

		public abstract int apply(String msg, MessageReceivedEvent event);

		public static int calculate(String msg, MessageReceivedEvent event) {
			COMMAND_TYPE cmd_type = Arrays.stream(values())
					.filter(v -> v.command_text.equals(msg))
					.findFirst()
					.orElseThrow(IllegalArgumentException::new);

			return cmd_type.apply(msg, event);
		}
	}

}
