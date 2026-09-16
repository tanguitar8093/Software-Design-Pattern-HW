package oodv1_2_1;

public class MessageReceivedEvent extends CommunityEvent {
    public CommunityEventType type = CommunityEventType.MESSAGE_RECEIVED;
    public Message message;

    @Override
    public void dispatchTo(Bot bot) {
        bot.onMessageReceived(this.message);
    }
}
