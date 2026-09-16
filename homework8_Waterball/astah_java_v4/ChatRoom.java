package oodv4;
import java.util.List;

public class ChatRoom extends Observable {
    private List<CommunityObserver> observers;

    public void postMessage(Message message) {}
    @Override public void register(CommunityObserver observer) {}
    @Override public void unregister(CommunityObserver observer) {}
    @Override public void notify(CommunityEvent event) {}
}
