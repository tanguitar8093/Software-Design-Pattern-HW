package oodv4;
import java.util.Date;
import java.util.List;

public class WaterballCommunity extends Observable {
    public Date currentTime;
    private List<CommunityObserver> observers;

    public void login(Participant participant) {}
    public void logout(String participantId) {}
    public void elapseTime(int amount, String unit) {}
    public List<Participant> getOnlineParticipants() { return null; }
    public int getOnlineCount() { return 0; }
    @Override public void register(CommunityObserver observer) {}
    @Override public void unregister(CommunityObserver observer) {}
    @Override public void notify(CommunityEvent event) {}
}
