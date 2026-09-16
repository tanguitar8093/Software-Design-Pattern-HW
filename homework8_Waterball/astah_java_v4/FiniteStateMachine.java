package oodv4;
import java.util.List;

public class FiniteStateMachine {
    private State currentState;
    private List<Transition> transitions;

    public boolean fire(Trigger trigger) { return false; }
    public State getCurrentState() { return currentState; }
    public void changeState(State nextState) {}
}
