package oodv1_2_1;

public class RecordState implements State {
    private RecordingSession session;

    @Override public void onEnter(Bot bot) {}
    @Override public void onExit(Bot bot) {}
    @Override public void onMessageReceived(Bot bot, Message message) {}
    @Override public void onPostPublished(Bot bot, Post post) {}
    @Override public void onBroadcastStarted(Bot bot, String speakerId) {}
    @Override public void onVoiceSpoken(Bot bot, VoiceMessage voiceMessage) {}
    @Override public void onBroadcastStopped(Bot bot, String speakerId) {}
    @Override public void onTimeElapsed(Bot bot, int seconds) {}
}
