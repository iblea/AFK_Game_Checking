package discordbot;

import java.util.Arrays;
import java.util.List;

import net.dv8tion.jda.api.entities.*;
import net.dv8tion.jda.api.events.message.MessageReceivedEvent;
import net.dv8tion.jda.internal.entities.UserById;

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
				String help_content = help_command_string();
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
		GAME_TEST("test") {
			@Override
			public int apply(String msg, MessageReceivedEvent event) {
				// Snowflakeid
				long idVar = Long.parseLong(event.getAuthor().getId());
				System.out.println("user_id: " + idVar);
				Member member = event.getMember();
				if (member == null) {
					System.out.println("member is null");
					return 4;
				}
				Activity activity = getPlaying(member);
				if (activity == null) {
					System.out.println("activity is null");
					return 4;
				}
				/* 동일 member 클래스로는 playing a game 업데이트 안됨 */
				while (activity != null) {
					System.out.println("activity: " + activity.getName());
					activity = getPlaying(member);
				}
				return 4;
			}
		}
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

	public static String help_command_string()
	{
		return """
웹사이트에서 설정을 진행할 수 있습니다.
!add - https://gc.iasdf.com
				""";
	}

	public static Activity getPlaying(Member discordMember)
	{
		List<Activity> activities =  discordMember.getActivities();
		if (activities.size() > 0) {
			return activities.get(0);
		}
		return null;
	}

}
