# Astah 類別規格清單：oodv1-1-4 vs oodv1-2-1

本文件依據 [astah_spec_prompt.md](astah_spec_prompt.md) 規範生成，以核心設計圖 [oodv1-1-4.mmd](oodv1-1-4.mmd) 的類別為白名單，比對全圖設計 [oodv1-2-1.mmd](oodv1-2-1.mmd) 提取最完整之屬性型別、預設值、操作方法簽名與關係。方便直接複製貼入 Astah。

---

### 類別: Observable

- **Stereotype**: interface, Subject
- **屬性**: none
- **操作方法**:
  - +register(observer: CommunityObserver): void
  - +unregister(observer: CommunityObserver): void
  - +notify(event: CommunityEvent): void
- **被誰指**:
  - ChatRoom (Realization)
  - Forum (Realization)
  - Broadcast (Realization)
  - WaterballCommunity (Realization)
- **指向誰**:
  - CommunityObserver (Aggregation: 1 o-- 0..\* observers)
  - CommunityEvent (Dependency: notify(event))

---

### 類別: CommunityObserver

- **Stereotype**: interface, Observer
- **屬性**: none
- **操作方法**:
  - +update(event: CommunityEvent): void
- **被誰指**:
  - Observable (Aggregation: 1 o-- 0..\* observers)
  - Bot (Realization)
- **指向誰**:
  - CommunityEvent (Dependency: update(event))

---

### 類別: CommunityEventType

- **Stereotype**: enumeration
- **屬性**:
  - MESSAGE_RECEIVED
  - POST_PUBLISHED
  - BROADCAST_STARTED
  - VOICE_SPOKEN
  - BROADCAST_STOPPED
  - TIME_ELAPSED
- **操作方法**: none
- **被誰指**:
  - CommunityEvent (Association: fixed type)
- **指向誰**: none

---

### 類別: CommunityEvent

- **Stereotype**: abstract
- **屬性**:
  - +type: CommunityEventType
- **操作方法**:
  - +dispatchTo(bot: Bot): void
- **被誰指**:
  - Observable (Dependency: notify(event))
  - CommunityObserver (Dependency: update(event))
  - MessageReceivedEvent (Generalization)
  - PostPublishedEvent (Generalization)
  - BroadcastStartedEvent (Generalization)
  - VoiceSpokenEvent (Generalization)
  - BroadcastStoppedEvent (Generalization)
  - TimeElapsedEvent (Generalization)
- **指向誰**:
  - CommunityEventType (Association: type)
  - Bot (Dependency: dispatchTo(bot))

---

### 類別: MessageReceivedEvent

- **Stereotype**: none
- **屬性**:
  - +type: CommunityEventType = MESSAGE_RECEIVED
  - +message: Message
- **操作方法**:
  - +dispatchTo(bot: Bot): void
- **被誰指**: none
- **指向誰**:
  - CommunityEvent (Generalization)
  - Message (Association)

---

### 類別: PostPublishedEvent

- **Stereotype**: none
- **屬性**:
  - +type: CommunityEventType = POST_PUBLISHED
  - +post: Post
- **操作方法**:
  - +dispatchTo(bot: Bot): void
- **被誰指**: none
- **指向誰**:
  - CommunityEvent (Generalization)
  - Post (Association)

---

### 類別: BroadcastStartedEvent

- **Stereotype**: none
- **屬性**:
  - +type: CommunityEventType = BROADCAST_STARTED
  - +speakerId: String
- **操作方法**:
  - +dispatchTo(bot: Bot): void
- **被誰指**: none
- **指向誰**:
  - CommunityEvent (Generalization)

---

### 類別: VoiceSpokenEvent

- **Stereotype**: none
- **屬性**:
  - +type: CommunityEventType = VOICE_SPOKEN
  - +voiceMessage: VoiceMessage
- **操作方法**:
  - +dispatchTo(bot: Bot): void
- **被誰指**: none
- **指向誰**:
  - CommunityEvent (Generalization)
  - VoiceMessage (Association)

---

### 類別: BroadcastStoppedEvent

- **Stereotype**: none
- **屬性**:
  - +type: CommunityEventType = BROADCAST_STOPPED
  - +speakerId: String
- **操作方法**:
  - +dispatchTo(bot: Bot): void
- **被誰指**: none
- **指向誰**:
  - CommunityEvent (Generalization)

---

### 類別: TimeElapsedEvent

- **Stereotype**: none
- **屬性**:
  - +type: CommunityEventType = TIME_ELAPSED
  - +seconds: int
- **操作方法**:
  - +dispatchTo(bot: Bot): void
- **被誰指**: none
- **指向誰**:
  - CommunityEvent (Generalization)

---

### 類別: ChatRoom

- **Stereotype**: none (Concrete Subject)
- **屬性**:
  - -observers: List~CommunityObserver~
- **操作方法**:
  - +postMessage(message: Message): void
  - +register(observer: CommunityObserver): void
  - +unregister(observer: CommunityObserver): void
  - +notify(event: CommunityEvent): void
- **被誰指**: none
- **指向誰**:
  - Observable (Realization)

---

### 類別: Forum

- **Stereotype**: none (Concrete Subject)
- **屬性**:
  - -observers: List~CommunityObserver~
- **操作方法**:
  - +createPost(post: Post): void
  - +addComment(postId: String, comment: Comment): void
  - +register(observer: CommunityObserver): void
  - +unregister(observer: CommunityObserver): void
  - +notify(event: CommunityEvent): void
- **被誰指**: none
- **指向誰**:
  - Observable (Realization)

---

### 類別: Broadcast

- **Stereotype**: none (Concrete Subject)
- **屬性**:
  - +currentSpeakerId: String
  - -observers: List~CommunityObserver~
- **操作方法**:
  - +start(speakerId: String): void
  - +speak(voiceMessage: VoiceMessage): void
  - +stop(speakerId: String): void
  - +isBroadcasting(): bool
  - +register(observer: CommunityObserver): void
  - +unregister(observer: CommunityObserver): void
  - +notify(event: CommunityEvent): void
- **被誰指**: none
- **指向誰**:
  - Observable (Realization)

---

### 類別: WaterballCommunity

- **Stereotype**: none (Concrete Subject + Query Provider)
- **屬性**:
  - +currentTime: DateTime
  - -observers: List~CommunityObserver~
- **操作方法**:
  - +login(participant: Participant): void
  - +logout(participantId: String): void
  - +elapseTime(amount: int, unit: String): void
  - +getOnlineParticipants(): List~Participant~
  - +getOnlineCount(): int
  - +register(observer: CommunityObserver): void
  - +unregister(observer: CommunityObserver): void
  - +notify(event: CommunityEvent): void
- **被誰指**: none
- **指向誰**:
  - Observable (Realization)

---

### 類別: Bot

- **Stereotype**: Concrete Observer + State Context
- **屬性**:
  - +id: String = "bot"
  - +quota: int
  - +replyCycleIndex: int
  - -currentState: State
- **操作方法**:
  - +update(event: CommunityEvent): void
  - +changeState(nextState: State): void
  - +onMessageReceived(message: Message): void
  - +onPostPublished(post: Post): void
  - +onVoiceSpoken(voiceMessage: VoiceMessage): void
  - +onBroadcastStarted(speakerId: String): void
  - +onBroadcastStopped(speakerId: String): void
  - +onTimeElapsed(seconds: int): void
  - +replyChatMessage(content: String, tags: List~String~): void
  - +commentPost(postId: String, content: String, tags: List~String~): void
  - +broadcastVoice(content: String): void
  - +resetReplyCycle(): void
  - +getNextReplyMessage(): String
- **被誰指**:
  - CommunityEvent (Dependency: dispatchTo(bot))
- **指向誰**:
  - CommunityObserver (Realization)
  - State (Association: 1 --> 1 currentState / delegate)

---

### 類別: State

- **Stereotype**: interface
- **屬性**: none
- **操作方法**:
  - +onEnter(bot: Bot): void
  - +onExit(bot: Bot): void
  - +onMessageReceived(bot: Bot, message: Message): void
  - +onPostPublished(bot: Bot, post: Post): void
  - +onBroadcastStarted(bot: Bot, speakerId: String): void
  - +onVoiceSpoken(bot: Bot, voiceMessage: VoiceMessage): void
  - +onBroadcastStopped(bot: Bot, speakerId: String): void
  - +onTimeElapsed(bot: Bot, seconds: int): void
- **被誰指**:
  - Bot (Association: 1 --> 1 currentState)
  - NormalState (Realization)
  - RecordState (Realization)
  - KnowledgeKingState (Realization)
- **指向誰**: none

---

### 類別: NormalState

- **Stereotype**: Concrete State
- **屬性**: none
- **操作方法**:
  - +onEnter(bot: Bot): void
  - +onExit(bot: Bot): void
  - +onMessageReceived(bot: Bot, message: Message): void
  - +onPostPublished(bot: Bot, post: Post): void
  - +onBroadcastStarted(bot: Bot, speakerId: String): void
  - +onVoiceSpoken(bot: Bot, voiceMessage: VoiceMessage): void
  - +onBroadcastStopped(bot: Bot, speakerId: String): void
  - +onTimeElapsed(bot: Bot, seconds: int): void
- **被誰指**: none
- **指向誰**:
  - State (Realization)

---

### 類別: RecordState

- **Stereotype**: Concrete State
- **屬性**:
  - -session: RecordingSession
- **操作方法**:
  - +onEnter(bot: Bot): void
  - +onExit(bot: Bot): void
  - +onMessageReceived(bot: Bot, message: Message): void
  - +onPostPublished(bot: Bot, post: Post): void
  - +onBroadcastStarted(bot: Bot, speakerId: String): void
  - +onVoiceSpoken(bot: Bot, voiceMessage: VoiceMessage): void
  - +onBroadcastStopped(bot: Bot, speakerId: String): void
  - +onTimeElapsed(bot: Bot, seconds: int): void
- **被誰指**: none
- **指向誰**:
  - State (Realization)

---

### 類別: KnowledgeKingState

- **Stereotype**: Concrete State
- **屬性**:
  - -game: KnowledgeKingGame
- **操作方法**:
  - +onEnter(bot: Bot): void
  - +onExit(bot: Bot): void
  - +onMessageReceived(bot: Bot, message: Message): void
  - +onPostPublished(bot: Bot, post: Post): void
  - +onBroadcastStarted(bot: Bot, speakerId: String): void
  - +onVoiceSpoken(bot: Bot, voiceMessage: VoiceMessage): void
  - +onBroadcastStopped(bot: Bot, speakerId: String): void
  - +onTimeElapsed(bot: Bot, seconds: int): void
- **被誰指**: none
- **指向誰**:
  - State (Realization)

---

### 參照實體類別（被事件關聯）

#### 類別: Message

- **Stereotype**: none
- **屬性**:
  - +authorId: String
  - +content: String
  - +tags: List~String~
- **操作方法**: none
- **被誰指**:
  - MessageReceivedEvent (Association)
- **指向誰**: none

#### 類別: Post

- **Stereotype**: none
- **屬性**:
  - +id: String
  - +authorId: String
  - +title: String
  - +content: String
  - +tags: List~String~
- **操作方法**:
  - +addComment(comment: Comment): void
- **被誰指**:
  - PostPublishedEvent (Association)
- **指向誰**: none

#### 類別: VoiceMessage

- **Stereotype**: none
- **屬性**:
  - +speakerId: String
  - +content: String
- **操作方法**: none
- **被誰指**:
  - VoiceSpokenEvent (Association)
- **指向誰**: none
