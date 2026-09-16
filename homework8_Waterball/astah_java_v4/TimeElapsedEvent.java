package oodv4;

public class TimeElapsedEvent extends CommunityEvent {
    public CommunityEventType type = CommunityEventType.TIME_ELAPSED;
    public int seconds;

    @Override
    public void dispatchTo(Bot bot) {
        bot.onTimeElapsed(this.seconds);
    }
}
