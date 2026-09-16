package oodv1_2_1;
import java.util.List;

public class Member extends Participant {
    public Role role;

    public void sendMessage(ChatRoom chatRoom, String content, List<String> tags) {}
    public void publishPost(Forum forum, String title, String content, List<String> tags) {}
    public void commentPost(Forum forum, String postId, String content, List<String> tags) {}
    public void startBroadcast(Broadcast broadcast) {}
    public void speak(Broadcast broadcast, String content) {}
    public void stopBroadcast(Broadcast broadcast) {}
}
