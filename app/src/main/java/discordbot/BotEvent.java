package discordbot;

import net.dv8tion.jda.api.entities.ChannelType;
import net.dv8tion.jda.api.entities.Message;
import net.dv8tion.jda.api.entities.MessageChannel;
import net.dv8tion.jda.api.events.message.MessageReceivedEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;

public class BotEvent extends ListenerAdapter
{
	public BotEvent() {
	}

	/*
	@Override
	public void onMessageReceived(MessageReceivedEvent event) {
		if (event.getAuthor().isBot()) {
			return;
		}
        Message message = event.getMessage();
        String content = message.getContentRaw(); 
        // getContentRaw() is an atomic getter
        // getContentDisplay() is a lazy getter which modifies the content for e.g. console view (strip discord formatting)
        if (content.equals("!ping"))
        {
            MessageChannel channel = event.getChannel();
            channel.sendMessage("Pong!").queue(); // Important to call .queue() on the RestAction returned by sendMessage(...)
        }
		if (event.isFromType(ChannelType.PRIVATE)) {
			System.out.printf("[PM] %s: %s\n", event.getAuthor().getName(),
					event.getMessage().getContentDisplay());
			System.out.println(event.getMessage().getContentRaw());

			String help_content = "help test";
			MessageChannel channel = event.getChannel();
			channel.sendMessage(help_content).queue();

		} else {
			System.out.printf("[%s][%s] %s: %s\n", event.getGuild().getName(),
					event.getTextChannel().getName(), event.getMember().getEffectiveName(),
					event.getMessage().getContentDisplay());
			System.out.println(event.getMessage().getContentRaw());

			String help_content = "help test";
			MessageChannel channel = event.getChannel();
			channel.sendMessage(help_content).queue();

		}
	}
	*/

	// 메세지를 받을 때
	@Override
	public void onMessageReceived(MessageReceivedEvent event) {
		if (event.getAuthor().isBot()) {
			return;
		}
		// String msg = event.getMessage().getContentRaw();
		String msg = event.getMessage().getContentRaw();

		BotCommand botCommand = new BotCommand(event);
		int status = botCommand.botCommandContent(msg);

		if (status < 0) {
			System.out.println("Bot Error");
			// String help_content = "**Bot Error!**\nPlease contact the Bot developer.";
			// MessageChannel channel = event.getChannel();
			// channel.sendMessage(help_content).queue();

			// return;
		}

		if (status == 0) {
			System.out.println("Wrong Command");
			// String help_content = "Wrong Command";
			// MessageChannel channel = event.getChannel();
			// channel.sendMessage(help_content).queue();

			// return;
		}
	}

}
