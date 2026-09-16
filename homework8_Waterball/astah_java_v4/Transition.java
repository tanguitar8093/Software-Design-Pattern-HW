package oodv4;

public class Transition {
    public State fromState;
    public State toState;
    public String triggerName;
    private Guard guard;
    private Action action;

    public boolean tryHandle(TransitionContext context) { return false; }
}
