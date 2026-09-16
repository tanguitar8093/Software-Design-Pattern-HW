package oodv4;

public class VoiceSpokenEvent extends CommunityEvent {
    public CommunityEventType type = CommunityEventType.VOICE_SPOKEN;
    public VoiceMessage voiceMessage;

    @Override
    public void dispatchTo(Bot bot) {
        bot.onVoiceSpoken(this.voiceMessage);
    }
}
