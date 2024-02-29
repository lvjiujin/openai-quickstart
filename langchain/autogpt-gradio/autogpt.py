# search tool serp
from langchain_community.utilities import SerpAPIWrapper
from langchain.agents import Tool
from langchain.tools.file_management.write import WriteFileTool
from langchain.tools.file_management.read import ReadFileTool
from langchain_openai import OpenAIEmbeddings

# vectorstore 
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore import InMemoryDocstore

# AutoGPT
from langchain_experimental.autonomous_agents import AutoGPT
from langchain_openai import ChatOpenAI

import os
import sys
import gradio as gr

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def ask_and_answer(text):
    # 构造 AutoGPT 的工具集
    search = SerpAPIWrapper()
    tools = [
        Tool(
            name="search",
            func=search.run,
            description="useful for when you need to answer questions about current events. You should ask targeted questions",
        ),
        WriteFileTool(),
        ReadFileTool(),
    ]

    # OpenAI Embedding 模型
    embeddings_model = OpenAIEmbeddings()

    embedding_size = 1536  # OpenAI Embedding 向量维数
    # 使用 Faiss 的 IndexFlatL2 索引
    index = faiss.IndexFlatL2(embedding_size)
    # 实例化 Faiss 向量数据库
    vectorstore = FAISS(embeddings_model, index, InMemoryDocstore({}), {})

    # 实例化自主智能体 Auto-GPT
    global agent
    agent = AutoGPT.from_llm_and_tools(   
        ai_name="Jarvis",
        ai_role="Assistant",
        tools=tools,
        llm=ChatOpenAI(model_name="gpt-4", temperature=0, verbose=True),
        memory=vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": 0.8}),# 实例化 Faiss 的 VectorStoreRetriever
    )

    # 打印 Auto-GPT 内部的 chain 日志  
    agent.chain.verbose = True

    # agent.run(["乔布斯和马斯克各自的贡献是什么？分别产生了哪些影响？"])
    # result = agent.run(["袁世凯是什么时候当选为中华民国大总统的？"])
    # result = agent.run(["华盛顿和乾隆各自对时代产生了什么影响？","后人如何看待他们各自的政治作为？"])
    # print("result = ", result)
    # 这里就用result返回给gradio的输出
    # s = "人工智能科学家西蒙是哪一年获得图灵奖的？"
    query_lst = []
    query_lst.append(text)
    result = agent.run(query_lst)
    print("result = ", result)
    return result

def launch_gradio():

    iface = gr.Interface(
        fn=ask_and_answer,
        title="AutoGPT",
        inputs=[
            gr.Textbox(label="input", placeholder="input", value="input your question"),
        ],
        outputs=[
            gr.Textbox(label="output", placeholder="result", value="result")
        ],
        allow_flagging="never"
    )

    iface.launch(share=True, server_name="0.0.0.0")

if __name__ == "__main__":
    
    # 启动 Gradio 服务
    launch_gradio()