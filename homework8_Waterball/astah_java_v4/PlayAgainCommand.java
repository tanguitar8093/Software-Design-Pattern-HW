package oodv4;

public class PlayAgainCommand extends AbstractBotCommand {
    public int requiredQuota = 5;
    public Role requiredRole = Role.MEMBER;

    @Override
    protected boolean doExecute(Bot bot, Member member, Message message) { return false; }
}
