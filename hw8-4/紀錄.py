紀錄
1. fire() / onEnter() / onExit() 具體邏輯怎麼寫
class State implements StateNode:
    enter: Action
    exit: Action

    def onEnter(event):
        self.enter.execute(event)

    def onExit(event):
        self.exit.execute(event)

    def fire(event):
        return False   # 單純狀態沒有自己的 Transition[]，永遠交給外層處理


class FiniteStateMachine implements StateNode:
    currentState: StateNode
    transitions: List[Transition]

    def onEnter(event):
        self.currentState.onEnter(event)   # 委派給目前的子節點

    def onExit(event):
        self.currentState.onExit(event)    # 委派給目前的子節點

    def fire(event):
        # 1) 先讓目前子節點自己嘗試處理（可能是 State，也可能是巢狀的 FiniteStateMachine）
        if self.currentState.fire(event):
            return True

        # 2) 子節點沒吃掉這個事件，才輪到自己比對 Transition[]
        for t in self.transitions:
            if t.isApplicable(self.currentState, event):
                self.currentState.onExit(event)
                if t.action: t.action.execute(event)
                self.currentState = t.to
                self.currentState.onEnter(event)
                return True
        return False