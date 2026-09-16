package oodv1_2_1;

public class PostPublishedEvent extends CommunityEvent {
    public CommunityEventType type = CommunityEventType.POST_PUBLISHED;
    public Post post;

    @Override
    public void dispatchTo(Bot bot) {
        bot.onPostPublished(this.post);
    }
}
