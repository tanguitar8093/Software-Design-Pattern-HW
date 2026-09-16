package oodv4;

public class CompositeState extends State {
    private FiniteStateMachine innerFsm;

    @Override
    public boolean handle(TransitionContext context) { return false; }
}
