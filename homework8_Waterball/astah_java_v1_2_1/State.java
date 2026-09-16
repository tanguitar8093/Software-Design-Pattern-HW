package oodv1_2_1;

public interface State {
    void onEnter(Bot bot);
    void onExit(Bot bot);
    void onMessageReceived(Bot bot, Message message);
    void onPostPublished(Bot bot, Post post);
    void onBroadcastStarted(Bot bot, String speakerId);
    void onVoiceSpoken(Bot bot, VoiceMessage voiceMessage);
    void onBroadcastStopped(Bot bot, String speakerId);
    void onTimeElapsed(Bot bot, int seconds);
}
