package oodv4;
import java.util.List;

public class Question {
    public int number;
    public String description;
    public List<String> options;
    public String correctAnswer;

    public boolean isCorrect(String answer) { return false; }
}
