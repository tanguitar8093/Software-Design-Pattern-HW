package oodv4;

public class RecordCommand extends AbstractBotCommand {
    public int requiredQuota = 3;
    public Role requiredRole = Role.MEMBER;

    @Override
    protected boolean doExecute(Bot bot, Member member, Message message) { return false; }
}
