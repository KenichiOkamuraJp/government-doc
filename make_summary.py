import os
import re
import chromadb
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from common import config

f = open('apikey', 'r')
apikey = f.read()
f.close()
os.environ["OPENAI_API_KEY"] = apikey

def make_summary(name: str):

  # 会議名から読込対象テキスト/インデックス永続化対象フォルダ名を確定
  target_folder = config['folder']['target'] + '/' + name
  index_folder  = config['folder']['index']  + '/' + name

  # 会議名の存否チェック
  if not os.path.isdir(target_folder):
    return False, None, None, None
  
  # 入力データを指定／チャンクに分解 
  loader = TextLoader(target_folder + '/doc.txt', encoding='utf-8')
  documents = loader.load()
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=10)
  texts = text_splitter.split_documents(documents)

  # インデックスの作成
  embeddings = OpenAIEmbeddings()
  # settings for ChromaDB
  client_settings = chromadb.config.Settings(
    chroma_db_impl="duckdb+parquet", 
    persist_directory=index_folder, 
    anonymized_telemetry=False
  )
  db = Chroma(
    collection_name="langchain_store", 
    embedding_function=embeddings, 
    client_settings=client_settings, 
    persist_directory=index_folder
  )
  db.add_documents(documents=texts, embedding=embeddings)
  db.persist()

  # RetrievalQAの作成
  chroma_retriever = db.as_retriever()
  llm = ChatOpenAI(model_name='gpt-4')
  prompt_template = """
  Use the following pieces of context to answer the question at the end. 
  If you don't know the answer, just say that you don't know, don't try to make up an answer.

  {context}

  Question: {question}
  Answer in Japanese:"""
  PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
  chain_type_kwargs = {"prompt": PROMPT}
  qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=chroma_retriever, chain_type_kwargs=chain_type_kwargs)

  # 質疑応答
  # 概要の作成
  query1 = "What is talking about in this meeting?"
  llm_response1 = qa(query1)
  text1 = llm_response1["result"]

  # トピックの列挙
  query2 = "List up topics in bullet point, which are discussed in this meeting."
  llm_response2 = qa(query2)
  text2 = llm_response2["result"]
  
  # トピックの分解
  topic_words = str(text2).split('\n')
  new_topics = []
  for topic in topic_words:
    new_topic = re.sub(r'[0-9]*\.', '', topic)
    if new_topic != '':
      new_topics.append(new_topic)

  # トピックごとの詳細確認
  topics = []
  for t in new_topics:
    query3 = 'What and how is talking about "' + t + '" in this meeting?'
    llm_response3 = qa(query3)
    text3 = llm_response3["result"]

    topics.append({
      'topic' : t,
      'answer' : text3
    })

  return True, text1, text2, topics
