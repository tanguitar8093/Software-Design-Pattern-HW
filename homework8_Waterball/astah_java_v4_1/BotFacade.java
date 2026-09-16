package oodv4_1;

public class BotFacade {
    private Bot bot;
    private Object rootFsmBuilder;
    private CompositeState currentCompositeState;

    public static BotFacade create() { return new BotFacade(); }
    public BotFacade state(String name) { return this; }
    public BotFacade subState(String name, State state) { return this; }
    public BotFacade command(String name, BotCommand cmd) { return this; }
    public BotFacade transition(String from, String to, String trigger) { return this; }
    public BotFacade transitionWithGuard(String from, String to, String trigger, Guard guard) { return this; }
    public Bot build() { return bot; }
}
