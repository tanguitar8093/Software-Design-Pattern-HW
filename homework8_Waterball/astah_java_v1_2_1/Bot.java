package oodv1_2_1;
import java.util.List;

public class Bot extends Participant implements CommunityObserver {
    public String id = "bot";
    public int quota;
    public int replyCycleIndex;
    private State currentState;

    @Override
    public void update(CommunityEvent event) {
        event.dispatchTo(this);
    }

    public void changeState(State nextState) {
        this.currentState = nextState;
    }

    public void onMessageReceived(Message message) {
        currentState.onMessageReceived(this, message);
    }

    public void onPostPublished(Post post) {
        currentState.onPostPublished(this, post);
    }

    public void onVoiceSpoken(VoiceMessage voiceMessage) {
        currentState.onVoiceSpoken(this, voiceMessage);
    }

    public void onBroadcastStarted(String speakerId) {
        currentState.onBroadcastStarted(this, speakerId);
    }

    public void onBroadcastStopped(String speakerId) {
        currentState.onBroadcastStopped(this, speakerId);
    }

    public void onTimeElapsed(int seconds) {
        currentState.onTimeElapsed(this, seconds);
    }

    public void replyChatMessage(String content, List<String> tags) {}
    public void commentPost(String postId, String content, List<String> tags) {}
    public void broadcastVoice(String content) {}
    public void resetReplyCycle() {}
    public String getNextReplyMessage() { return ""; }
}
