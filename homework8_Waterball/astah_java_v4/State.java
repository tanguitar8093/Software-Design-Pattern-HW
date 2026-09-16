package oodv4;

public abstract class State {
    public String id;
    public void onEnter(TransitionContext context) {}
    public void onExit(TransitionContext context) {}
    public abstract boolean handle(TransitionContext context);
}
