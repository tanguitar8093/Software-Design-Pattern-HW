package oodv1_2_1;

public interface Observable {
    void register(CommunityObserver observer);
    void unregister(CommunityObserver observer);
    void notify(CommunityEvent event);
}
