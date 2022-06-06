package discordbot;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class BotEventTest {

	@Test
	void setOffline() {
		BotEvent botEvent = new BotEvent(BotEvent.Status.ONLINE);

		botEvent.setOffline();

		assertThat(botEvent).isEqualTo(new BotEvent(BotEvent.Status.OFFLINE));
	}

	@Test
	void setOnline() {
		BotEvent botEvent = new BotEvent(BotEvent.Status.OFFLINE);

		botEvent.setOnline();

		assertThat(botEvent).isEqualTo(new BotEvent(BotEvent.Status.ONLINE));
	}
}
