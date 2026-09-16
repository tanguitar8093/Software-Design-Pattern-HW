package oodv4;

public class BroadcastStartedEvent extends CommunityEvent {
    public CommunityEventType type = CommunityEventType.BROADCAST_STARTED;
    public String speakerId;

    @Override
    public void dispatchTo(Bot bot) {
        bot.onBroadcastStarted(this.speakerId);
    }
}
