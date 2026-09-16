package oodv4;
import java.util.Date;

public class KnowledgeKingGame {
    public int currentQuestionIndex;
    public Date startTime;

    public Question getCurrentQuestion() { return null; }
    public boolean submitAnswer(String memberId, String answer) { return false; }
    public boolean isFinished() { return false; }
    public boolean isTimeout(Date currentTime) { return false; }
    public String getWinner() { return ""; }
}
