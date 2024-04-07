package discordbot;

import javax.security.auth.login.LoginException;

import net.dv8tion.jda.api.JDA;
import net.dv8tion.jda.api.JDABuilder;
import net.dv8tion.jda.api.interactions.commands.build.Commands;
import net.dv8tion.jda.api.requests.GatewayIntent;

public class DiscordApi {

    JDA jda;
    JDABuilder builder;
    String token;

    DiscordApi(String token) {
        this.token = token;
        this.builder = null;
        this.jda = null;
    }

    public void botStart()
        throws LoginException, InterruptedException {
        this.BuildApi();
        this.ConnectDiscordApi();
        this.setCommand();
    }

    public void BuildApi() {
		this.builder = JDABuilder.createDefault(token);
        // Read Channel Message
		builder.enableIntents(GatewayIntent.MESSAGE_CONTENT);
        // Connect CommandHandler
		builder.addEventListeners(new CommandHandler());
    }

    public void ConnectDiscordApi()
        throws LoginException, InterruptedException {
        this.jda = this.builder.build();
        System.out.println("Start the Bot.");
    }

    public void setCommand() {
		jda.upsertCommand(Commands.slash("hello", "Returns 'Hello World!'")).queue();
        System.out.println("Set Slash Command");
    }

}
