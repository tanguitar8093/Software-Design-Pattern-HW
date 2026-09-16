package oodv4;

public class KingCommand extends AbstractBotCommand {
    public int requiredQuota = 5;
    public Role requiredRole = Role.ADMIN;

    @Override
    protected boolean doExecute(Bot bot, Member member, Message message) { return false; }
}
