package oodv4;

public class IsBroadcastingGuard extends Guard {
    @Override
    public boolean isSatisfied(TransitionContext context) { return false; }
}
