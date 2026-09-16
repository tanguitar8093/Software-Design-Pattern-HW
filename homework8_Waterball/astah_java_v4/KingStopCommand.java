package oodv4;

public class KingStopCommand extends AbstractBotCommand {
    public int requiredQuota = 0;
    public Role requiredRole = Role.ADMIN;

    @Override
    protected boolean doExecute(Bot bot, Member member, Message message) { return false; }
}
