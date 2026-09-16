package oodv4_1;
import java.util.List;

public class FiniteStateMachine {
    private State currentState;
    private List<Transition> transitions;

    public boolean fire(Trigger trigger) {
        return false;
    }
}
