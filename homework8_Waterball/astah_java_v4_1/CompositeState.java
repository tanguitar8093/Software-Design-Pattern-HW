package oodv4_1;

public class CompositeState extends State {
    private FiniteStateMachine innerFsm;

    @Override
    public boolean handle(TransitionContext context) {
        return false;
    }
}
