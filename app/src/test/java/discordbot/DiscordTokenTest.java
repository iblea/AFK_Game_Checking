package discordbot;

import org.junit.jupiter.api.Test;

import java.io.IOException;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatIOException;


public class DiscordTokenTest {
    private final String path = "./src/test/resources/token.txt";

    @Test
    void isNotExistTokenFile() throws IOException {
        assertThatIOException()
                .isThrownBy(() -> new DiscordToken("xxx"));
    }

    @Test
    void isExistTokenFile() throws IOException {
        new DiscordToken(path);
    }

    @Test
    void getToken() throws IOException {
        DiscordToken discordToken = new DiscordToken(path);

        assertThat(discordToken).isEqualTo(new DiscordToken(path));
    }
}
