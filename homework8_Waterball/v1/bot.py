from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from homework8_Waterball.v1.community import (
    CommunityEvent,
    CommunityObserver,
    Message,
    Participant,
    Post,
    Role,
    VoiceMessage,
    WaterballCommunity,
)
from homework8_Waterball.v1.fsm import FiniteStateMachine, Trigger

if TYPE_CHECKING:
    from homework8_Waterball.v1.commands import BotCommand


class Bot(Participant, CommunityObserver):
    """
    社群機器人 (Invoker / Observer / Subsystem Product)
    - quota: 機器人共用額度
    - replyCycleIndex: 輪播回覆索引
    - rootFsm: 通用有限狀態機
    - commands: 指令註冊表
    """
    def __init__(self, quota: int = 10):
        super().__init__("bot")
        self.quota: int = quota
        self.replyCycleIndex: int = 0
        self._rootFsm: Optional[FiniteStateMachine] = None
        self._commands: Dict[str, BotCommand] = {}
        self._community: Optional[WaterballCommunity] = None

    def setFsm(self, fsm: FiniteStateMachine) -> None:
        self._rootFsm = fsm
        self._rootFsm.setTarget(self)

    def setCommunity(self, community: WaterballCommunity) -> None:
        self._community = community

    def getCommunity(self) -> Optional[WaterballCommunity]:
        return self._community

    def registerCommand(self, name: str, cmd: BotCommand) -> None:
        self._commands[name] = cmd

    def executeCommand(self, name: str, member: Any, msg: Message) -> bool:
        cmd = self._commands.get(name)
        if cmd is not None:
            return cmd.execute(self, member, msg)
        return False

    def update(self, event: CommunityEvent) -> None:
        event.dispatchTo(self)

    def onMessageReceived(self, message: Message) -> None:
        # 忽略機器人自己的發言通知，避免自我循環
        if message.authorId == "bot":
            return

        # 1. 優先處理常態訊息（委派 FSM 當前狀態 handle：如輪播回覆）
        trigger = Trigger("message", {"message": message})
        if self._rootFsm is not None:
            self._rootFsm.fire(trigger)

        # 2. 判定是否為指令（標記 bot，且指令名稱存在於 commands）
        # README:「當社群成員傳送訊息並標記機器人時，若該訊息符合狀態下的合法指令格式與權限條件，
        # 機器人仍會先依據當前狀態處理該訊息，之後再執行指令，如：切換狀態。」
        if "bot" in message.tags:
            cmd_name = message.content.strip()
            if cmd_name in self._commands and self._community is not None:
                member = self._community.getMember(message.authorId)
                if member is not None:
                    self.executeCommand(cmd_name, member, message)

    def onPostPublished(self, post: Post) -> None:
        trigger = Trigger("post", {"post": post})
        if self._rootFsm is not None:
            self._rootFsm.fire(trigger)

    def onVoiceSpoken(self, voiceMessage: VoiceMessage) -> None:
        trigger = Trigger("voice", {"voiceMessage": voiceMessage})
        if self._rootFsm is not None:
            self._rootFsm.fire(trigger)

    def onBroadcastStarted(self, speakerId: str) -> None:
        trigger = Trigger("broadcast_started", {"speakerId": speakerId})
        if self._rootFsm is not None:
            self._rootFsm.fire(trigger)

    def onBroadcastStopped(self, speakerId: str) -> None:
        trigger = Trigger("broadcast_stopped", {"speakerId": speakerId})
        if self._rootFsm is not None:
            self._rootFsm.fire(trigger)

    def onTimeElapsed(self, seconds: int) -> None:
        trigger = Trigger("time_elapsed", {"seconds": seconds})
        if self._rootFsm is not None:
            self._rootFsm.fire(trigger)

    def onOnlineChanged(self, onlineCount: int) -> None:
        trigger = Trigger("online_changed", {"onlineCount": onlineCount})
        if self._rootFsm is not None:
            self._rootFsm.fire(trigger)

    def replyChatMessage(self, content: str, tags: Optional[List[str]] = None) -> None:
        if self._community is not None:
            msg = Message("bot", content, tags)
            self._community.chatRoom.postMessage(msg)

    def commentPost(self, postId: str, content: str, tags: Optional[List[str]] = None) -> None:
        if self._community is not None:
            from homework8_Waterball.v1.community import Comment
            comment = Comment("bot", content, tags)
            self._community.forum.addComment(postId, comment)

    def broadcastVoice(self, content: str) -> None:
        if self._community is not None:
            self._community.broadcast.start("bot")
            self._community.broadcast.speak(VoiceMessage("bot", content))
            self._community.broadcast.stop("bot")

    def resetReplyCycle(self) -> None:
        self.replyCycleIndex = 0

    def getNextReplyMessage(self) -> str:
        # DefaultConversation 輪播 3 則：
        # 1. good to hear, 2. thank you, 3. How are you
        messages = ["good to hear", "thank you", "How are you"]
        msg = messages[self.replyCycleIndex % len(messages)]
        self.replyCycleIndex += 1
        return msg

    def getNextInteractingMessage(self) -> str:
        # Interacting 輪播 2 則：
        # 1. Hi hi😁, 2. I like your idea!
        messages = ["Hi hi😁", "I like your idea!"]
        msg = messages[self.replyCycleIndex % len(messages)]
        self.replyCycleIndex += 1
        return msg
