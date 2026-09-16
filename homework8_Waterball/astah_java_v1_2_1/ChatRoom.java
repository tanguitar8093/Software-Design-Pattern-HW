package oodv1_2_1;
import java.util.List;

public class ChatRoom implements Observable {
    private List<CommunityObserver> observers;

    public void postMessage(Message message) {}
    @Override public void register(CommunityObserver observer) {}
    @Override public void unregister(CommunityObserver observer) {}
    @Override public void notify(CommunityEvent event) {}
}
