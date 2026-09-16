package oodv4;

public abstract class AtomicState extends State {
    @Override
    public boolean handle(TransitionContext context) { return false; }
}
