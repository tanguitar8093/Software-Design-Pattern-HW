package oodv5.astah;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/*
 * Astah reverse-engineering source generated from OODv5-1.mmd.
 *
 * This is a UML import skeleton, not the executable v3 implementation.
 * Import source root: homework8_Waterball/astah-java/src
 *
 * The package-private top-level declarations are intentional: Java permits
 * all model types in one source file, while Astah can still reverse-engineer
 * their fields, operations, inheritance, implementation, and typed links.
 */

// ============================================================================
// Application layer
// ============================================================================

class Client {
    private List<String> outputSink;
    private WaterballCommunity community;
    private Bot bot;

    public List<String> run(List<String> inputLines) { return null; }
    public void executeLine(String rawLine) { }
    private void handleStarted(Map<String, Object> payload) { }
    private void handleLogin(Map<String, Object> payload) { }
    private void handleLogout(Map<String, Object> payload) { }
    private void handleElapsed(int amount, TimeUnit unit) { }
    private void handleNewMessage(Map<String, Object> payload) { }
    private void handleNewPost(Map<String, Object> payload) { }
    private void handleGoBroadcasting(Map<String, Object> payload) { }
    private void handleSpeak(Map<String, Object> payload) { }
    private void handleStopBroadcasting(Map<String, Object> payload) { }
}

class TimeUnit {
    public static final TimeUnit SECONDS = new TimeUnit();
    public static final TimeUnit MINUTES = new TimeUnit();
    public static final TimeUnit HOURS = new TimeUnit();
}

// ============================================================================
// Bot module: Facade and Command
// ============================================================================

class BotFacade {
    public static Bot createDefaultBot(WaterballCommunity community, int quota) { return null; }
    public static Bot createBot(WaterballCommunity community, BotDefinition definition, int quota) { return null; }
}

class BotDefinition {
    private State rootState;
    private List<Transition> rootTransitions = new ArrayList<>();
    private Map<String, BotCommand> commands = new HashMap<>();
    private List<FsmPlugin> plugins = new ArrayList<>();

    public BotDefinition setInitialState(State state) { return this; }
    public BotDefinition addTransition(Transition transition) { return this; }
    public BotDefinition addCommand(String name, BotCommand command) { return this; }
    public BotDefinition installPlugin(FsmPlugin plugin) { return this; }
    public FiniteStateMachine buildFsm(Object target) { return null; }
}

class Bot extends Participant {
    public String id = "bot";
    public int quota;
    private int replyCycleIndex;
    private FiniteStateMachine rootFsm;
    private Map<String, BotCommand> commands = new HashMap<>();
    private WaterballCommunity community;

    public Bot() { super("bot"); }
    public void setFsm(FiniteStateMachine fsm) { }
    public void setCommunity(WaterballCommunity community) { }
    public WaterballCommunity getCommunity() { return null; }
    public void registerCommand(String name, BotCommand command) { }
    public boolean executeCommand(String name, Member member, Message message) { return false; }
    public void update(CommunityEvent event) { }
    public void onMessageReceived(Message message) { }
    public void onPostPublished(Post post) { }
    public void onBroadcastStarted(String speakerId) { }
    public void onVoiceSpoken(VoiceMessage voiceMessage) { }
    public void onBroadcastStopped(String speakerId) { }
    public void onTimeElapsed(int seconds) { }
    public void onOnlineChanged(int onlineCount) { }
    public void replyChatMessage(String content, List<String> tags) { }
    public void commentPost(String postId, String content, List<String> tags) { }
    public void broadcastVoice(String content) { }
    public void resetReplyCycle() { }
    public String getNextReplyMessage() { return null; }
    public String getNextInteractingMessage() { return null; }
}

class BotCommand {
    public boolean canExecute(Bot bot, Member member, Message message) { return false; }
    public boolean execute(Bot bot, Member member, Message message) { return false; }
}

class AbstractBotCommand extends BotCommand {
    public int requiredQuota;
    public Role requiredRole;

    @Override public boolean canExecute(Bot bot, Member member, Message message) { return false; }
    public boolean checkQuota(Bot bot) { return false; }
    public boolean checkPermission(Member member) { return false; }
    @Override public boolean execute(Bot bot, Member member, Message message) { return false; }
    public boolean doExecute(Bot bot, Member member, Message message) { return false; }
    public void deductQuota(Bot bot) { }
}

class KingCommand extends AbstractBotCommand {
    public int requiredQuota = 5;
    public Role requiredRole = Role.ADMIN;
    @Override public boolean doExecute(Bot bot, Member member, Message message) { return false; }
}

class RecordCommand extends AbstractBotCommand {
    public int requiredQuota = 3;
    public Role requiredRole = Role.MEMBER;
    @Override public boolean doExecute(Bot bot, Member member, Message message) { return false; }
}

class StopRecordingCommand extends AbstractBotCommand {
    public int requiredQuota = 0;
    @Override public boolean canExecute(Bot bot, Member member, Message message) { return false; }
    @Override public boolean doExecute(Bot bot, Member member, Message message) { return false; }
}

class KingStopCommand extends AbstractBotCommand {
    public int requiredQuota = 0;
    public Role requiredRole = Role.ADMIN;
    @Override public boolean doExecute(Bot bot, Member member, Message message) { return false; }
}

class PlayAgainCommand extends AbstractBotCommand {
    public int requiredQuota = 5;
    public Role requiredRole = Role.MEMBER;
    @Override public boolean doExecute(Bot bot, Member member, Message message) { return false; }
}

// ============================================================================
// FSM core
// ============================================================================

class FiniteStateMachine {
    private State currentState;
    private List<Transition> transitions = new ArrayList<>();
    private List<FsmPlugin> plugins = new ArrayList<>();
    private Object target;

    public FiniteStateMachine(State initialState, Object target) { }
    public void setTarget(Object target) { }
    public Object getTarget() { return null; }
    public void addTransition(Transition transition) { }
    public void installPlugin(FsmPlugin plugin) { }
    public void uninstallPlugin(FsmPlugin plugin) { }
    public State getCurrentState() { return null; }
    public void changeState(State nextState, TransitionContext context) { }
    public boolean fire(Trigger trigger) { return false; }
}

class State {
    public String id;
    public void onEnter(TransitionContext context) { }
    public void onExit(TransitionContext context) { }
    public boolean handle(TransitionContext context) { return false; }
}

class AtomicState extends State {
    @Override public void onEnter(TransitionContext context) { }
    @Override public void onExit(TransitionContext context) { }
    @Override public boolean handle(TransitionContext context) { return false; }
}

class Transition {
    public State fromState;
    public State toState;
    public String triggerName;
    private Guard guard;
    private Action action;

    public Transition(State fromState, State toState, String triggerName, Guard guard, Action action) { }
    public boolean isTriggeredBy(State currentState, Trigger trigger) { return false; }
    public boolean isAllowed(TransitionContext context) { return false; }
    public void executeAction(TransitionContext context) { }
}

class Trigger {
    public String name;
    public Map<String, Object> payload = new HashMap<>();
    public Trigger(String name, Map<String, Object> payload) { }
}

class TransitionContext {
    public Trigger trigger;
    public FiniteStateMachine fsm;
    public Object target;
    public TransitionContext(Trigger trigger, FiniteStateMachine fsm, Object target) { }
}

class Guard {
    public boolean isSatisfied(TransitionContext context) { return false; }
}

class Action {
    public void execute(TransitionContext context) { }
}

class FsmPlugin {
    public boolean beforeStateHandle(FiniteStateMachine fsm, TransitionContext context) { return false; }
    public void afterStateChanged(FiniteStateMachine fsm, State oldState, State newState, TransitionContext context) { }
}

// ============================================================================
// Optional sub-state machine plugin
// ============================================================================

class SubStateMachinePlugin extends FsmPlugin {
    @Override public boolean beforeStateHandle(FiniteStateMachine fsm, TransitionContext context) { return false; }
    @Override public void afterStateChanged(FiniteStateMachine fsm, State oldState, State newState, TransitionContext context) { }
}

class CompositeState extends State {
    private FiniteStateMachine innerFsm;
    public CompositeState(String id, FiniteStateMachine innerFsm) { }
    public FiniteStateMachine getInnerFsm() { return null; }
    @Override public void onEnter(TransitionContext context) { }
    @Override public void onExit(TransitionContext context) { }
    @Override public boolean handle(TransitionContext context) { return false; }
}

// ============================================================================
// Waterball Bot states, guards, and actions
// ============================================================================

class NormalState extends CompositeState {
    public NormalState(FiniteStateMachine innerFsm) { super("NORMAL", innerFsm); }
}

class RecordState extends CompositeState {
    private RecordingSession session;
    public RecordState(FiniteStateMachine innerFsm) { super("RECORD", innerFsm); }
    @Override public void onEnter(TransitionContext context) { }
    public RecordingSession getSession() { return null; }
}

class KnowledgeKingState extends CompositeState {
    private KnowledgeKingGame game;
    public KnowledgeKingState(FiniteStateMachine innerFsm) { super("KNOWLEDGE_KING", innerFsm); }
    @Override public void onEnter(TransitionContext context) { }
    public KnowledgeKingGame getGame() { return null; }
}

class DefaultConversationState extends AtomicState {
    public DefaultConversationState() { }
    @Override public void onEnter(TransitionContext context) { }
    @Override public void onExit(TransitionContext context) { }
    @Override public boolean handle(TransitionContext context) { return false; }
}

class InteractingState extends AtomicState {
    public InteractingState() { }
    @Override public void onEnter(TransitionContext context) { }
    @Override public void onExit(TransitionContext context) { }
    @Override public boolean handle(TransitionContext context) { return false; }
}

class WaitingState extends AtomicState {
    public WaitingState() { }
    @Override public void onEnter(TransitionContext context) { }
    @Override public void onExit(TransitionContext context) { }
    @Override public boolean handle(TransitionContext context) { return false; }
}

class RecordingState extends AtomicState {
    public RecordingState() { }
    @Override public void onEnter(TransitionContext context) { }
    @Override public void onExit(TransitionContext context) { }
    @Override public boolean handle(TransitionContext context) { return false; }
}

class QuestioningState extends AtomicState {
    private int elapsedSeconds;
    public QuestioningState() { }
    @Override public void onEnter(TransitionContext context) { }
    @Override public void onExit(TransitionContext context) { }
    @Override public boolean handle(TransitionContext context) { return false; }
}

class ThanksForJoiningState extends AtomicState {
    private int elapsedSeconds;
    public ThanksForJoiningState() { }
    @Override public void onEnter(TransitionContext context) { }
    @Override public void onExit(TransitionContext context) { }
    @Override public boolean handle(TransitionContext context) { return false; }
}

class OnlineCountGuard extends Guard {
    private int threshold;
    private boolean greaterOrEqual;
    public OnlineCountGuard(int threshold, boolean greaterOrEqual) { }
    @Override public boolean isSatisfied(TransitionContext context) { return false; }
}

class IsBroadcastingGuard extends Guard {
    private boolean expected;
    public IsBroadcastingGuard(boolean expected) { }
    @Override public boolean isSatisfied(TransitionContext context) { return false; }
}

class IsRecorderGuard extends Guard {
    private RecordState recordState;
    public IsRecorderGuard(RecordState recordState) { }
    @Override public boolean isSatisfied(TransitionContext context) { return false; }
}

class ResetReplyCycleAction extends Action {
    @Override public void execute(TransitionContext context) { }
}

class FlushReplayAction extends Action {
    private RecordState recordState;
    public FlushReplayAction(RecordState recordState) { }
    @Override public void execute(TransitionContext context) { }
}

class ResetGameAction extends Action {
    private KnowledgeKingState knowledgeKingState;
    public ResetGameAction(KnowledgeKingState knowledgeKingState) { }
    @Override public void execute(TransitionContext context) { }
}

class SelectRecordSubStateAction extends Action {
    private RecordState recordState;
    private State waitingState;
    private State recordingState;
    public SelectRecordSubStateAction(RecordState recordState, State waitingState, State recordingState) { }
    @Override public void execute(TransitionContext context) { }
}

class StopRecordAction extends Action {
    private RecordState recordState;
    private State recordingState;
    public StopRecordAction(RecordState recordState, State recordingState) { }
    @Override public void execute(TransitionContext context) { }
}

// ============================================================================
// Community domain and Observer
// ============================================================================

class WaterballCommunity extends Observable {
    public LocalDateTime currentTime;
    private List<Participant> onlineParticipants = new ArrayList<>();
    private Map<String, Member> membersById = new HashMap<>();
    private ChatRoom chatRoom;
    private Forum forum;
    private Broadcast broadcast;

    public WaterballCommunity(LocalDateTime initialTime) { }
    public void login(Participant participant) { }
    public void logout(String participantId) { }
    public void elapseTime(int amount, TimeUnit unit) { }
    public List<Participant> getOnlineParticipants() { return null; }
    public int getOnlineCount() { return 0; }
    public Member getMember(String memberId) { return null; }
}

class Participant {
    public String id;
    public Participant(String id) { }
}

class Member extends Participant {
    public Role role;
    public Member(String id, Role role) { super(id); }
    public void sendMessage(ChatRoom chatRoom, String content, List<String> tags) { }
    public void publishPost(Forum forum, String title, String content, List<String> tags) { }
    public void commentPost(Forum forum, String postId, String content, List<String> tags) { }
    public void startBroadcast(Broadcast broadcast) { }
    public void speak(Broadcast broadcast, String content) { }
    public void stopBroadcast(Broadcast broadcast) { }
}

class Role {
    public static final Role ADMIN = new Role();
    public static final Role MEMBER = new Role();
}

class Observable {
    private List<CommunityObserver> observers = new ArrayList<>();
    public void register(CommunityObserver observer) { }
    public void unregister(CommunityObserver observer) { }
    public void notify(CommunityEvent event) { }
}

class CommunityObserver {
    public void update(CommunityEvent event) { }
}

class ChatRoom extends Observable {
    public void postMessage(Message message) { }
}

class Forum extends Observable {
    private List<Post> posts = new ArrayList<>();
    public void createPost(Post post) { }
    public void addComment(String postId, Comment comment) { }
}

class Broadcast extends Observable {
    private String currentSpeakerId;
    public boolean isBroadcasting() { return false; }
    public void start(String speakerId) { }
    public void speak(VoiceMessage voiceMessage) { }
    public void stop(String speakerId) { }
}

class Message {
    public String authorId;
    public String content;
    public List<String> tags = new ArrayList<>();
    public Message(String authorId, String content, List<String> tags) { }
}

class Post {
    public String id;
    public String authorId;
    public String title;
    public String content;
    public List<String> tags = new ArrayList<>();
    private List<Comment> comments = new ArrayList<>();
    public Post(String id, String authorId, String title, String content, List<String> tags) { }
    public void addComment(Comment comment) { }
}

class Comment {
    public String authorId;
    public String content;
    public List<String> tags = new ArrayList<>();
    public Comment(String authorId, String content, List<String> tags) { }
}

class VoiceMessage {
    public String speakerId;
    public String content;
    public VoiceMessage(String speakerId, String content) { }
}

// ============================================================================
// Strongly typed community events
// ============================================================================

class CommunityEvent {
    public CommunityEventType type;
    public void dispatchTo(Bot bot) { }
}

class CommunityEventType {
    public static final CommunityEventType MESSAGE_RECEIVED = new CommunityEventType();
    public static final CommunityEventType POST_PUBLISHED = new CommunityEventType();
    public static final CommunityEventType BROADCAST_STARTED = new CommunityEventType();
    public static final CommunityEventType VOICE_SPOKEN = new CommunityEventType();
    public static final CommunityEventType BROADCAST_STOPPED = new CommunityEventType();
    public static final CommunityEventType TIME_ELAPSED = new CommunityEventType();
    public static final CommunityEventType ONLINE_CHANGED = new CommunityEventType();
}

class MessageReceivedEvent extends CommunityEvent {
    public Message message;
    public MessageReceivedEvent(Message message) { }
    @Override public void dispatchTo(Bot bot) { }
}

class PostPublishedEvent extends CommunityEvent {
    public Post post;
    public PostPublishedEvent(Post post) { }
    @Override public void dispatchTo(Bot bot) { }
}

class BroadcastStartedEvent extends CommunityEvent {
    public String speakerId;
    public BroadcastStartedEvent(String speakerId) { }
    @Override public void dispatchTo(Bot bot) { }
}

class VoiceSpokenEvent extends CommunityEvent {
    public VoiceMessage voiceMessage;
    public VoiceSpokenEvent(VoiceMessage voiceMessage) { }
    @Override public void dispatchTo(Bot bot) { }
}

class BroadcastStoppedEvent extends CommunityEvent {
    public String speakerId;
    public BroadcastStoppedEvent(String speakerId) { }
    @Override public void dispatchTo(Bot bot) { }
}

class TimeElapsedEvent extends CommunityEvent {
    public int seconds;
    public TimeElapsedEvent(int seconds) { }
    @Override public void dispatchTo(Bot bot) { }
}

class OnlineChangedEvent extends CommunityEvent {
    public int onlineCount;
    public OnlineChangedEvent(int onlineCount) { }
    @Override public void dispatchTo(Bot bot) { }
}

// ============================================================================
// Activities
// ============================================================================

class RecordingSession {
    public String recorderId;
    private List<VoiceMessage> voices = new ArrayList<>();
    public RecordingSession(String recorderId) { }
    public void addVoice(VoiceMessage message) { }
    public boolean hasRecordedVoice() { return false; }
    public String generateReplay() { return null; }
    public void clear() { }
}

class KnowledgeKingGame {
    public int currentQuestionIndex;
    private Map<String, Integer> scores = new HashMap<>();
    private List<Question> questions = new ArrayList<>();
    public KnowledgeKingGame() { }
    public Question getCurrentQuestion() { return null; }
    public boolean submitAnswer(String memberId, String answer) { return false; }
    public boolean isFinished() { return false; }
    public String getWinner() { return null; }
}

class Question {
    public int number;
    public String description;
    public List<String> options = new ArrayList<>();
    public String correctAnswer;
    public Question(int number, String description, List<String> options, String correctAnswer) { }
    public boolean isCorrect(String answer) { return false; }
}
