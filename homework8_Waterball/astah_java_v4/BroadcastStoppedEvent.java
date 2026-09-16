package oodv4;

public class BroadcastStoppedEvent extends CommunityEvent {
    public CommunityEventType type = CommunityEventType.BROADCAST_STOPPED;
    public String speakerId;

    @Override
    public void dispatchTo(Bot bot) {
        bot.onBroadcastStopped(this.speakerId);
    }
}
