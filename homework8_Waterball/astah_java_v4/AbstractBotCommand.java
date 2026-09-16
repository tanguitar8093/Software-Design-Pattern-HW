package oodv4;

public abstract class AbstractBotCommand extends BotCommand {
    public int requiredQuota;
    public Role requiredRole;

    @Override
    public boolean execute(Bot bot, Member member, Message message) { return false; }
    protected boolean checkQuota(Bot bot) { return false; }
    protected boolean checkPermission(Member member) { return false; }
    protected void deductQuota(Bot bot) {}
    protected abstract boolean doExecute(Bot bot, Member member, Message message);
}
