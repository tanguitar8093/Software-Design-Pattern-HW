package oodv1_2_1;

public abstract class CommunityEvent {
    public CommunityEventType type;

    public abstract void dispatchTo(Bot bot);
}
