import asyncio
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

        def on_user_msg(change):
            self.chat_history.extend(
                [
                    HumanMessage(content=self.user_msg),
                    AIMessage(content=self.ai_msg),
                ]
            )
            self.send({"type": "create"})
            for chunk in chain.stream(
                {"input": change.new, "chat_history": self.chat_history}
            ):
                if "answer" in chunk:
                    self.send({"type": "append", "text": chunk["answer"]})
            self.send({"type": "finish"})

        self.observe(on_user_msg, names=["user_msg"])


class AsyncChatUIWidget(anywidget.AnyWidget):
    """
    Chat UI widget that uses an event loop to process astream events.

    Notes
    -----
    There doesn't seem to be a vetted solution for running a separate event
    loop in Jupyter, since Jupyter is already running in its own event loop.

    https://github.com/python/cpython/issues/66435

    The workaround is to use the `nest_asyncio` package, which monkeypatches
    asyncio to allow nested event loops but it is no longer maintained.

    ```
    import nest_asyncio
    nest_asyncio.apply()
    ```
    """
    _esm = pathlib.Path(__file__).parent / "static" / "widget.js"
    _css = pathlib.Path(__file__).parent / "static" / "widget.css"
    user_msg = traitlets.Unicode(sync=True)
    ai_msg = traitlets.Unicode(sync=True)

    def __init__(self, chain, version="v1", event_loop=None, **kwargs):
        super().__init__(**kwargs)

        self.chain = chain
        self.chat_history = []
        self.version = version
        if event_loop is None:
            self.event_loop = asyncio.get_event_loop()
        else:
            self.event_loop = event_loop

        async def process_user_input(user_input):
            async for event in chain.astream_events(
                {"input": user_input, "chat_history": self.chat_history},
                version=self.version,
            ):
                if (
                    event["event"] == "on_chat_model_stream"
                    and "seq:step:3" in event["tags"]  # TODO: find another way to filter for the output chat model
                ):
                    chunk = event["data"]["chunk"]
                    self.send({"type": "append", "text": f"{chunk.content}"})

        def on_user_msg(change):
            self.chat_history.extend(
                [
                    HumanMessage(content=self.user_msg),
                    AIMessage(content=self.ai_msg),
                ]
            )
            self.send({"type": "create"})
            self.event_loop.run_until_complete(process_user_input(change.new))
            self.send({"type": "finish"})

        self.observe(on_user_msg, names=["user_msg"])
