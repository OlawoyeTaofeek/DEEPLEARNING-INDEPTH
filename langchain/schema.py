from pydantic import BaseModel, Field
from typing import Literal, List
from abc import abstractmethod, ABC

class BaseMessage_(BaseModel):
    role: str 
    content: str

    def __str__(self):
        return f"{self.role.upper()}: {self.content}"

    def __repr__(self):
        return f"{self.__class__.__name__}(content={self.content!r})"
    
    @property
    def type(self):
        return self.role
    
    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content
        }

class HumanMessage(BaseMessage_):
    role: Literal['user'] = Field(default="user", frozen=True)

# 🔹 AI message
class AIMessage(BaseMessage_):
    role: Literal["assistant"] = Field(default="assistant", frozen=True)


# 🔹 System message
class SystemMessage(BaseMessage_):
    role: Literal["system"] = Field(default="system", frozen=True)

class BaseChatMessageHistory_(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def add_user_message(self, message: str):
        pass  

    @abstractmethod
    def add_ai_message(self, message: str):
        pass  

    @abstractmethod
    def clear(self):
        pass 
    
    @abstractmethod
    def get_messages(self) -> List[BaseMessage_]:
        pass

store = {}

def get_by_session_id(session_id: str) -> BaseChatMessageHistory_:
            if session_id not in store:
                store[session_id] = ChatMessageHistory_()
            return store[session_id]

class ChatMessageHistory_(BaseChatMessageHistory_, BaseModel):
    """In memory implementation of chat message history.
    Stores messages in a memory list.
    """
        # self._messages: List[BaseMessage_] = messages if messages is not None else []
    messages: list[BaseMessage_] = Field(default_factory=list)

    def add_user_message(self, message: str):
        self._messages.append(HumanMessage(content=message))

    def add_ai_message(self, message: str):
        self._messages.append(AIMessage(content=message))

    def clear(self):
        self._messages = []
    
    def get_messages(self) -> List[BaseMessage_]:
        return self._messages
    
    @property
    def messages(self) -> List[BaseMessage_]:
        return self._messages
    
history = ChatMessageHistory_()

history.add_user_message("Hi, my name is Taofeek")
history.add_ai_message("Nice to meet you!")
print(history.messages)


    
    

    