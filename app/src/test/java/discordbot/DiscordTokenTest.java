package discordbot;

import static org.junit.jupiter.api.Assertions.assertThrows;
import java.io.IOException;
import org.junit.jupiter.api.Test;


public class DiscordTokenTest {

	@Test
	void isExistTokenFile() throws IOException {
		String path = "";

		assertThrows(IOException.class, () -> {
			DiscordToken tokentest = new DiscordToken(path);
		});
    }

}
