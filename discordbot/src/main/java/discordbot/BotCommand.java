package discordbot;

import net.dv8tion.jda.api.entities.MessageChannel;
import net.dv8tion.jda.api.events.message.MessageReceivedEvent;

public class BotCommand
{
    final String HELP = "help";
    final String USER_ADD = "gcadd";
    final String USER_DEL = "gcdel";

	private MessageReceivedEvent event;

    public BotCommand(MessageReceivedEvent event) {
        this.event = event;
    }


	public int botCommandContent(String msg) {
		if (msg.charAt(0) != '!') {
			return 0;
		}

		msg = msg.substring(1);

		switch(msg) {
			case HELP:
                help_command(msg);
				return 1;
			case USER_ADD:
				add_user();
				return 2;
			case USER_DEL:
				del_user();
				return 3;
		}

		return 0;
	}

    private void help_command(String msg)
    {
		String help_content = "help test";
		MessageChannel channel = event.getChannel();
		channel.sendMessage(help_content).queue();
    }

	private void add_user()
	{

	}

	private void del_user()
	{

	}

    public void cmdContent(MessageReceivedEvent event)
    {

    }
}