package oodv1_2_1;

public class VoiceSpokenEvent extends CommunityEvent {
    public CommunityEventType type = CommunityEventType.VOICE_SPOKEN;
    public VoiceMessage voiceMessage;

    @Override
    public void dispatchTo(Bot bot) {
        bot.onVoiceSpoken(this.voiceMessage);
    }
}
