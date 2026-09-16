package oodv4;

public class OnlineCountGuard extends Guard {
    public int threshold;

    @Override
    public boolean isSatisfied(TransitionContext context) { return false; }
}
