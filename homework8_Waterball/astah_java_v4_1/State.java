package oodv4_1;

// 依需求純 Class，不使用 interface
public abstract class State {
    public String id;
    public abstract boolean handle(TransitionContext context);
}
