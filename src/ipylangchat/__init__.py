import importlib.metadata
import pathlib

import anywidget
import traitlets

from langchain_core.messages import AIMessage, HumanMessage

try:
    __version__ = importlib.metadata.version("ipylangchat")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"


class ChatUIWidget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "widget.js"
    _css = pathlib.Path(__file__).parent / "static" / "widget.css"
    user_msg = traitlets.Unicode(sync=True)
    ai_msg = traitlets.Unicode(sync=True)

    def __init__(self, chain, **kwargs):
        super().__init__(**kwargs)

        self.chain = chain
        self.chat_history = []

        def handle_user_question(change):
            self.chat_history.extend(
                [
                    HumanMessage(content=self.user_msg),
                    AIMessage(content=self.ai_msg),
                ]
            )
            self.send({ "type": "create" })
            for chunk in chain.stream(
                {"input": change.new, "chat_history": self.chat_history}
            ):
                if "answer" in chunk:
                    self.send({"type": "append", "text": chunk["answer"]})
            self.send({ "type": "finish" })

        self.observe(handle_user_question, names=["user_msg"])
