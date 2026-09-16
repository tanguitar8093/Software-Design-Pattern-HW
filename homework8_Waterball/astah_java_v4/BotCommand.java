package oodv4;

public abstract class BotCommand {
    public abstract boolean execute(Bot bot, Member member, Message message);
}
