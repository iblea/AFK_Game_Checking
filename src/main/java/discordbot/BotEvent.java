package discordbot;

import net.dv8tion.jda.api.events.message.MessageReceivedEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;

public class BotEvent extends ListenerAdapter
{
	public BotEvent() {
	}

	/*
	@Override
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
	*/

	// 메세지를 받을 때
	@Override
	public void onMessageReceived(MessageReceivedEvent event) {
		if (event.getAuthor().isBot()) {
			return;
		}
		String msg = event.getMessage().getContentRaw();

		BotCommand botCommand = new BotCommand(event);
		int status = botCommand.botCommandContent(msg);

		if (status <= 0) {
			System.out.println("잘못된 명령어입니다.");
		}
	}

}
