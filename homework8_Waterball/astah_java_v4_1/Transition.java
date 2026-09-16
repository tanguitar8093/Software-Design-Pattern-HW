package oodv4_1;

public class Transition {
    public State fromState;
    public State toState;
    public String triggerName;
    private Guard guard;
    private Action action;
}
