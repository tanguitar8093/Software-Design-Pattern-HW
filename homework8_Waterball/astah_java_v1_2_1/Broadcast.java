package oodv1_2_1;
import java.util.List;

public class Broadcast implements Observable {
    public String currentSpeakerId;
    private List<CommunityObserver> observers;

    public void start(String speakerId) {}
    public void speak(VoiceMessage voiceMessage) {}
    public void stop(String speakerId) {}
    public boolean isBroadcasting() { return false; }
    @Override public void register(CommunityObserver observer) {}
    @Override public void unregister(CommunityObserver observer) {}
    @Override public void notify(CommunityEvent event) {}
}
