package oodv4_1;
import java.util.Map;

public class Bot {
    public int quota;
    private FiniteStateMachine rootFsm;
    private Map<String, BotCommand> commands;

    public void registerCommand(String name, BotCommand cmd) {}
    public boolean executeCommand(String name, Member member, Message msg) { return false; }
    public void onMessageReceived(Message message) {}
}
