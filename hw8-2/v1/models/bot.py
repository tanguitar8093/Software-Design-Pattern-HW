from datetime import timedelta
from typing import List, Optional

from .broadcast import Broadcast, VoiceMessage
from .chat_room import ChatRoom, Message
from .enums import BotState, Role
from .forum import Comment, Forum, Post
from .knowledge_king_game import KnowledgeKingGame
from .participant import Participant
from .recording_session import RecordingSession


class Bot(Participant):
    """對應 OOA-Clean.mmd Bot：v1 尚未抽出 BotState/EventPublisher，狀態邏輯直接寫在本類別內。"""

    DEFAULT_REPLIES = ["good to hear", "thank you", "How are you"]
    INTERACTING_REPLIES = ["Hi hi😁", "I like your idea!"]

    def __init__(self, quota: int, community) -> None:
        super().__init__("bot")
        self.quota = quota
        self.community = community
        self.chat_room: Optional[ChatRoom] = None
        self.forum: Optional[Forum] = None
        self.broadcast: Optional[Broadcast] = None

        self.state = BotState.NORMAL_DEFAULT
        self.reply_cycle_index = 0
        self.recorder_id: Optional[str] = None
        self.recording_session: Optional[RecordingSession] = None
        self.game: Optional[KnowledgeKingGame] = None
        self.thanks_entered_at = None

    def bind_channels(self, chat_room: ChatRoom, forum: Forum, broadcast: Broadcast) -> None:
        self.chat_room = chat_room
        self.forum = forum
        self.broadcast = broadcast

    # ------------------------------------------------------------------
    # 被動接收事件：先依當前狀態做預設反應，再檢查是否觸發指令
    # ------------------------------------------------------------------
    def on_message_received(self, message: Message) -> None:
        tagged = "bot" in message.tags
        if self.state in (BotState.NORMAL_DEFAULT, BotState.NORMAL_INTERACTING):
            self._reply_cycle(message.author_id)
        elif self.state == BotState.KING_QUESTIONING and tagged:
            self._handle_answer(message)
        self._handle_command(message, tagged)

    def on_post_published(self, post: Post) -> None:
        if self.state == BotState.NORMAL_DEFAULT:
            self.comment_post(post.id, "Nice post", [post.author_id])
        elif self.state == BotState.NORMAL_INTERACTING:
            tags = ["bot"] + self.community.get_online_member_ids()
            self.comment_post(post.id, "How do you guys think about it?", tags)
        # RECORD / KING 狀態下不主動回覆貼文

    def on_voice_spoken(self, voice_message: VoiceMessage) -> None:
        if self.state == BotState.RECORD_RECORDING:
            self.recording_session.add_voice(voice_message)

    def on_broadcast_started(self, speaker_id: str) -> None:
        if self.state == BotState.RECORD_WAITING:
            self.state = BotState.RECORD_RECORDING

    def on_broadcast_stopped(self, speaker_id: str) -> None:
        if self.state == BotState.RECORD_RECORDING:
            replay = self.recording_session.generate_replay()
            self.reply_chat_message(replay, [self.recorder_id])
            self.state = BotState.RECORD_WAITING

    def on_time_elapsed(self, seconds: int) -> None:
        if self.state == BotState.KING_QUESTIONING and self.game.is_timeout(self.community.current_time):
            self._enter_thanks_for_joining()
        elif self.state == BotState.KING_THANKS:
            if self.community.current_time - self.thanks_entered_at >= timedelta(seconds=20):
                self._enter_normal_state()

    def on_participant_logged_in(self) -> None:
        if self.state == BotState.NORMAL_DEFAULT and self.community.get_online_count() >= 10:
            self.reply_cycle_index = 0
            self.state = BotState.NORMAL_INTERACTING

    def on_participant_logged_out(self) -> None:
        if self.state == BotState.NORMAL_INTERACTING and self.community.get_online_count() < 10:
            self.reply_cycle_index = 0
            self.state = BotState.NORMAL_DEFAULT

    # ------------------------------------------------------------------
    # 主動操作
    # ------------------------------------------------------------------
    def reply_chat_message(self, content: str, tags: List[str]) -> None:
        self.chat_room.post_message(Message("bot", content, tags))

    def comment_post(self, post_id: str, content: str, tags: List[str]) -> None:
        self.forum.add_comment(post_id, Comment("bot", content, tags))

    def broadcast_voice(self, content: str) -> None:
        self.broadcast.start("bot")
        self.broadcast.speak(VoiceMessage("bot", content))
        self.broadcast.stop("bot")

    # ------------------------------------------------------------------
    # 內部行為 (狀態相依的 if-else，v2 將以 State/Observer Pattern 萃取)
    # ------------------------------------------------------------------
    def _reply_cycle(self, author_id: str) -> None:
        replies = self.DEFAULT_REPLIES if self.state == BotState.NORMAL_DEFAULT else self.INTERACTING_REPLIES
        reply = replies[self.reply_cycle_index % len(replies)]
        self.reply_cycle_index += 1
        self.reply_chat_message(reply, [author_id])

    def _handle_answer(self, message: Message) -> None:
        if not self.game.submit_answer(message.author_id, message.content):
            return
        self.reply_chat_message("Congrats! you got the answer!", [message.author_id])
        if self.game.is_finished():
            self._enter_thanks_for_joining()
        else:
            self._announce_current_question()

    def _handle_command(self, message: Message, tagged: bool) -> None:
        if not tagged:
            return
        content, author = message.content, message.author_id
        if self.state in (BotState.NORMAL_DEFAULT, BotState.NORMAL_INTERACTING):
            if content == "king":
                self._execute_command(self._is_admin(author), 5, self._start_knowledge_king)
            elif content == "record":
                self._execute_command(True, 3, lambda: self._start_record(author))
        elif self.state in (BotState.RECORD_WAITING, BotState.RECORD_RECORDING):
            if content == "stop-recording":
                self._execute_command(author == self.recorder_id, 0, self._stop_recording)
        elif self.state in (BotState.KING_QUESTIONING, BotState.KING_THANKS):
            if content == "king-stop":
                self._execute_command(self._is_admin(author), 0, self._enter_normal_state)
            elif content == "play again":
                self._execute_command(True, 5, self._restart_knowledge_king)

    def _execute_command(self, permitted: bool, cost: int, effect) -> None:
        if not permitted or self.quota < cost:
            return
        self.quota -= cost
        effect()

    def _is_admin(self, member_id: str) -> bool:
        member = self.community.get_member(member_id)
        return member is not None and member.role == Role.ADMIN

    def _start_knowledge_king(self) -> None:
        self.game = KnowledgeKingGame(self.community.current_time)
        self.state = BotState.KING_QUESTIONING
        self.reply_chat_message("KnowledgeKing is started!", [])
        self._announce_current_question()

    def _restart_knowledge_king(self) -> None:
        self.game = KnowledgeKingGame(self.community.current_time)
        self.state = BotState.KING_QUESTIONING
        self.reply_chat_message("KnowledgeKing is gonna start again!", [])
        self._announce_current_question()

    def _announce_current_question(self) -> None:
        question = self.game.get_current_question()
        lines = [f"{question.number}. {question.description}"] + question.options
        self.reply_chat_message("\n".join(lines), [])

    def _enter_thanks_for_joining(self) -> None:
        self.state = BotState.KING_THANKS
        self.thanks_entered_at = self.community.current_time
        winner = self.game.get_winner()
        result_text = "Tie!" if winner is None else f"The winner is {winner}"
        if self.broadcast.is_broadcasting():
            self.reply_chat_message(result_text, [])
        else:
            self.broadcast_voice(result_text)

    def _start_record(self, recorder_id: str) -> None:
        self.recorder_id = recorder_id
        self.recording_session = RecordingSession(recorder_id)
        self.state = BotState.RECORD_RECORDING if self.broadcast.is_broadcasting() else BotState.RECORD_WAITING

    def _stop_recording(self) -> None:
        if self.state == BotState.RECORD_RECORDING:
            replay = self.recording_session.generate_replay()
            self.reply_chat_message(replay, [self.recorder_id])
        self.recorder_id = None
        self.recording_session = None
        self._enter_normal_state()

    def _enter_normal_state(self) -> None:
        self.game = None
        self.reply_cycle_index = 0
        self.state = BotState.NORMAL_INTERACTING if self.community.get_online_count() >= 10 else BotState.NORMAL_DEFAULT
