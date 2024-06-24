import importlib.metadata
import pathlib

import anywidget
import traitlets

from langchain_core.messages import AIMessage, HumanMessage

try:
    __version__ = importlib.metadata.version("ipylang")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"


class ChatUIWidget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "widget.js"
    _css = pathlib.Path(__file__).parent / "static" / "widget.css"
    human_msg = traitlets.Unicode(sync=True)
    ai_msg = traitlets.Unicode(sync=True)

    def __init__(self, chain, **kwargs):
        super().__init__(**kwargs)

        self.chain = chain
        self.chat_history = []

        def handle_user_question(change):
            self.chat_history.extend(
                [
                    HumanMessage(content=self.human_msg),
                    AIMessage(content=self.ai_msg),
                ]
            )
            result = chain.invoke({
                "input": change.new,
                "chat_history": self.chat_history
            })
            self.ai_msg = result["answer"]

        self.observe(handle_user_question, names=["human_msg"])
