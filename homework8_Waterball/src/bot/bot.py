from typing import Dict, Any
from ..fsm.core import Event
from .context import BotContext
from .fsm_builder import FluentFSMBuilder

def print_message(bot_msg: str, tags: list[str] = None):
    tag_str = ""
    if tags:
        tag_str = " " + ", ".join([f"@{t}" for t in tags])
    print(f"🤖: {bot_msg}{tag_str}")
    
def print_comment(post_id: str, msg: str, tags: list[str] = None):
    tag_str = ""
    if tags:
        tag_str = " " + ", ".join([f"@{t}" for t in tags])
    print(f"🤖 comment in post {post_id}: {msg}{tag_str}")


def b_normal_entry(event: Event, ctx: BotContext):
    pass
    
def b_normal_default_conv_entry(event: Event, ctx: BotContext):
    ctx.default_conv_idx = 0

def b_normal_interacting_entry(event: Event, ctx: BotContext):
    ctx.interacting_idx = 0
    

def handle_default_conv_message(event: Event, ctx: BotContext):
    author_id = event.payload['authorId']
    msg = ctx.default_conversation_messages[ctx.default_conv_idx]
    ctx.default_conv_idx = (ctx.default_conv_idx + 1) % len(ctx.default_conversation_messages)
    print_message(msg, [author_id])

def handle_default_conv_post(event: Event, ctx: BotContext):
    author_id = event.payload['authorId']
    post_id = event.payload['id']
    print_comment(post_id, "Nice post", [author_id])
    
def check_interaction_condition_login(event: Event, ctx: BotContext):
    ctx.add_online_user(type('obj', (object,), {'id': event.payload['userId']}))
    return ctx.get_online_count() >= 10

def handle_interacting_message(event: Event, ctx: BotContext):
    author_id = event.payload['authorId']
    msg = ctx.interacting_messages[ctx.interacting_idx]
    ctx.interacting_idx = (ctx.interacting_idx + 1) % len(ctx.interacting_messages)
    print_message(msg, [author_id])
    
def handle_interacting_post(event: Event, ctx: BotContext):
    # order: @bot, then list
    post_id = event.payload['id']
    tags = ["bot"] + list(ctx.members.keys()) # this list order should be ordered based on login
    # Need to fix ctx online user to ordered
    
class WaterballBot:
    def __init__(self):
        self.context = BotContext()
        self.fsm = self._build_fsm()
        self.fsm.set_context(self.context)
        self.fsm.start()

    def _build_fsm(self):
        # 1. Normal State Machine
        normal_fsm = FluentFSMBuilder("DefaultConversation") \
            .state("DefaultConversation", on_entry=b_normal_default_conv_entry) \
            .state("Interacting", on_entry=b_normal_interacting_entry) \
            .transition("DefaultConversation", "new message", "DefaultConversation", action=handle_default_conv_message) \
            .transition("DefaultConversation", "new post", "DefaultConversation", action=handle_default_conv_post) \
            .transition("DefaultConversation", "login", "Interacting", guard=check_interaction_condition_login) \
            .build()
        
        # Main FSM
        main_builder = FluentFSMBuilder("Normal") \
             .state("Normal", sub_machine=normal_fsm) \
             .state("Record") \
             .state("KnowledgeKing")
        
        return main_builder.build()

    def process_event(self, name: str, payload: Dict[str, Any]):
        event = Event(name, payload)
        
        # Pre hooks (like time elapsed prints)
        if "elapsed" in name:
            print(f"🕑 {name.replace('elapsed', 'elapsed...')} ")
        
        handled = self.fsm.dispatch(event)
        
        if not handled:
             # handle unhandled events globally depending on the instructions
             pass
