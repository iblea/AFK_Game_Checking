package discordbot;

import org.junit.jupiter.api.Test;

import java.io.IOException;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatIOException;


public class DiscordTokenTest {
	private final String path = "./src/test/resources/token.txt";

	@Test
	void isNotExistTokenFile() {
		assertThatIOException()
				.isThrownBy(() -> new DiscordToken("xxx"));
	}

	@Test
	void isExistTokenFile() throws IOException {
		String curpath = System.getProperty("user.dir");
		System.out.println("Working Directory = " + curpath);
		new DiscordToken(path);
	}

	@Test
	void getToken() throws IOException {
		DiscordToken discordToken = new DiscordToken(path);

		assertThat(discordToken).isEqualTo(new DiscordToken(path));
	}

	@Test
	void check_CR_chr() throws IOException {
		DiscordToken discordToken = new DiscordToken(path);
		assertThat(discordToken.getBotToken().contains("\r")).isFalse();
	}

	@Test
	void check_LF_chr() throws IOException {
		DiscordToken discordToken = new DiscordToken(path);
		assertThat(discordToken.getBotToken().contains("\n")).isFalse();
	}

}
