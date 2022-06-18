package discordbot;

import lombok.EqualsAndHashCode;
import lombok.Getter;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

@EqualsAndHashCode
public class DiscordToken {

	@Getter
	private final String botToken;

	public DiscordToken(String path) throws IOException {
		this.botToken = readToken(path);
	}

	/**
	 * @param path token이 들어있는 path 경로
	 * @return String
	 * @brief Path argument를 통해 파일에서 토큰을 추출해오는 함수
	 */
	private String readToken(String path) throws IOException {
		return Files.readString(Paths.get(path));
	}
}
