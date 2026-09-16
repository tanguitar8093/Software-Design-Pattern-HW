package oodv4_1;

// 依需求純 Class，不使用 interface
public abstract class BotCommand {
    public abstract boolean execute(Bot bot, Member member, Message message);
}
