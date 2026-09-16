package oodv4;
import java.util.List;

public abstract class Observable {
    public abstract void register(CommunityObserver observer);
    public abstract void unregister(CommunityObserver observer);
    public abstract void notify(CommunityEvent event);
}
