package oodv4;

public class StopRecordingCommand extends AbstractBotCommand {
    public int requiredQuota = 0;
    public Role requiredRole = Role.MEMBER;

    protected boolean checkPermission(Member member) { return false; }
    @Override
    protected boolean doExecute(Bot bot, Member member, Message message) { return false; }
}
