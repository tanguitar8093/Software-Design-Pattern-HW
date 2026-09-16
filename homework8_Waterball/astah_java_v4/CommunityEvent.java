package oodv4;

public abstract class CommunityEvent {
    public CommunityEventType type;
    public abstract void dispatchTo(Bot bot);
}
