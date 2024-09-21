import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from llama_index.core.objects import SQLTableSchema, SQLTableNodeMapping, ObjectIndex
from llama_index.core import SQLDatabase, VectorStoreIndex
from llama_index.core.bridge.pydantic import BaseModel
from llama_index.llms.openai import OpenAI
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.core.indices.struct_store.sql_query import (
    SQLTableRetrieverQueryEngine,
)
from src.database.run import engine, get_db_context
from src.prompt import REFINE_PROMPT
from src.settings import MessageRole, Settings

load_dotenv()


class Message(BaseModel):
    role: str
    content: str


class SQLAgent:
    def __init__(self, setting: Settings):
        prompt = (
            "This table give information about transaction result.\n"
            "It has columns: id, day, month, year, amount, description, code_id.\n"
            "\n"
            "Some example rows:\n"
            f"{get_db_context()}"
        )

        self.setting = setting

        self.sql_database = SQLDatabase(engine, include_tables=["transactionresult"])
        self.table_node_mapping = SQLTableNodeMapping(self.sql_database)
        self.table_schema_objs = [
            (SQLTableSchema(table_name="transactionresult", context_str=prompt))
        ]
        self.obj_index = ObjectIndex.from_objects(
            self.table_schema_objs,
            self.table_node_mapping,
            VectorStoreIndex,
        )

        self.history: list[Message] = []

        self.system_prompt = """The currency of the amount is VND."""

        llm = self.load_model(
            self.setting.type, self.setting.llm, self.system_prompt.strip("\n")
        )
        self.refine_llm = self.load_model(
            self.setting.type,
            self.setting.llm,
            REFINE_PROMPT.format(num=setting.number_of_msgs),
        )

        self.query_engine = SQLTableRetrieverQueryEngine(
            self.sql_database,
            self.obj_index.as_retriever(similarity_top_k=1),
            llm=llm,
            streaming=True,
        )

    def add_message(self, role: str, content: str):
        if role == MessageRole.system:  # noqa
            return
        self.history.append(Message(role=role, content=content))

    def get_history(self, num_history: int):
        history = self.history[-num_history:]
        return "\n".join([f"- {msg.role}: {msg.content}" for msg in history])

    def load_model(
        self, model_type: str, model_name: str, system: str = ""
    ) -> FunctionCallingLLM:
        if model_type == "openai":
            return OpenAI(model_name, system_prompt=system)
        else:
            raise ValueError("Model type not supported")

    def refine_question(self, question: str):
        prompt = f"History: {self.get_history(self.setting.number_of_msgs)}\nQuestion: {question}\nYour refined question: "
        response = self.refine_llm.complete(prompt)
        return response.text

    def query(self, question: str) -> str:
        prompt = self.refine_question(question)
        print(prompt)
        response = self.query_engine.query(prompt)
        return response
