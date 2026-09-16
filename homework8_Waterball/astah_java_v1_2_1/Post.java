package oodv1_2_1;
import java.util.List;

public class Post {
    public String id;
    public String authorId;
    public String title;
    public String content;
    public List<String> tags;

    public void addComment(Comment comment) {}
}
