package oodv4;
import java.util.List;
import java.util.Map;

public class Bot extends Participant {
    public String id = "bot";
    public int quota;
    public int replyCycleIndex;
    private FiniteStateMachine rootFsm;
    private Map<String, BotCommand> commands;

    public void registerCommand(String name, BotCommand cmd) {}
    public boolean executeCommand(String name, Member member, Message msg) { return false; }
    public void update(CommunityEvent event) {}
    public void onMessageReceived(Message message) {}
    public void onPostPublished(Post post) {}
    public void onVoiceSpoken(VoiceMessage voiceMessage) {}
    public void onBroadcastStarted(String speakerId) {}
    public void onBroadcastStopped(String speakerId) {}
    public void onTimeElapsed(int seconds) {}
    public void replyChatMessage(String content, List<String> tags) {}
    public void commentPost(String postId, String content, List<String> tags) {}
    public void broadcastVoice(String content) {}
    public void resetReplyCycle() {}
    public String getNextReplyMessage() { return ""; }
}
