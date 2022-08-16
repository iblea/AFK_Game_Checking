package discordbot;

import java.io.File;
import java.io.IOException;

import java.sql.Connection;
import java.sql.Statement;
import java.sql.DriverManager;
import java.sql.DatabaseMetaData;
import java.sql.SQLException;

import java.util.Hashtable;

public class Sqlite {
    final String SQLITE_PATH = "app/src/main/resources/users.sqlite";

    Hashtable<String, Integer> users;
    Connection conn;

    public Sqlite() {
        this.users = new Hashtable<String, Integer>();
        this.conn = null;
    }

    private boolean isExist() {
        File file = new File(this.SQLITE_PATH);

        if (file.exists()) {
            if (file.isFile()) {
                return true;
            }
        }

        return false;
    }

    private void createFile() throws IOException {
        File file = new File(this.SQLITE_PATH);
        file.createNewFile();
    }

    private boolean commitSQL(String SQL) throws SQLException {
        // 참조 : https://heodolf.tistory.com/144?category=887835
        Statement stat = this.conn.createStatement();
        try{
            stat.execute(SQL);
            this.conn.commit();
        } catch (SQLException e) {
            System.out.println(e.getMessage());
            if (this.conn != null) {
                this.conn.rollback();
            }
            stat.close();
            return false;
        }
        stat.close();
        return true;
    }

    private void createUserTable() throws SQLException {
        final String SQL = "CREATE TABLE IF NOT EXISTS GC_USERS (" + "\n" +
                "NAME   TEXT        NOT NULL," + "\n" +
                "STAT   INTEGER     DEFAULT 0," + "\n" +
                "PRIMARY KEY (NAME)" +
                ");";
        if (commitSQL(SQL) == false) {
            // Table 생성 실패하였으므로 에러 출력 후 종료시킨다.
            throw new SQLException("createUserTable failed");
        }
    }

    public void init() throws IOException, SQLException {

        // 이미 연결되어 있는 상태라면 return
        if (this.conn != null) {
            return;
        }

        if (isExist() == false) {
            createFile();
    		this.conn = DriverManager.getConnection("jdbc:sqlite:" + this.SQLITE_PATH);
            this.conn.setAutoCommit(false);
            createUserTable();
            System.out.println("init table");
            return;
        }

		this.conn = DriverManager.getConnection("jdbc:sqlite:" + this.SQLITE_PATH);
        this.conn.setAutoCommit(false);
    }


    public void close() throws SQLException {
        if (this.conn == null) {
            return;
        }
        this.conn.close();
        this.conn = null;
    }
}
