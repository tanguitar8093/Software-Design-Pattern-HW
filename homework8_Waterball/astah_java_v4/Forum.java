package oodv4;
import java.util.List;

public class Forum extends Observable {
    private List<CommunityObserver> observers;

    public void createPost(Post post) {}
    public void addComment(String postId, Comment comment) {}
    @Override public void register(CommunityObserver observer) {}
    @Override public void unregister(CommunityObserver observer) {}
    @Override public void notify(CommunityEvent event) {}
}
