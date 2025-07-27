import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from pytube import YouTube


load_dotenv()
api_key = os.getenv("GITHUB_API_KEY")
base_url = os.getenv("AZURE_BASE_URL")

# res = llm.invoke("What's the capital of india?")
# print(res.content)


#STEP 1a : indexing (loading transcript of a youtube video)
#- -> get the video id from the url and not just the full id 
#--> if url is : https://www.youtube.com/watch?v=LPZh9BOjkQs&ab_channel=3Blue1Brown then id is : LPZh9BOjkQs

# video_id = "Gfr50f6ZBvo"



def get_video_transcript(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        # transcript_list = YouTubeTranscriptApi.get_transcript(video_id, language=["en"])
        transcript_list = ytt_api.fetch(video_id=video_id, languages=["en"])
        #converting transcript to plain text : 
        transcript = " ".join(t.text for t in transcript_list)
        #print(transcript)
        return transcript
    except TranscriptsDisabled:
        print("No captions available for video")
    except Exception as e:
        raise RuntimeError(f"Error fetching transcript: {e}")

#STEP 1b : chunking : 
def chunk_transcript(transcript:str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return splitter.create_documents([transcript])

# print(len(chunks))
# print(chunks[0].page_content)

#STEP 1c & 1d - embedding genrations from created chunks and storing in vector stores :
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key, base_url=base_url)
def create_vector_store(video_id, transcript):
    try:
        path = f"vectorstore/{video_id}"
        if os.path.exists(path):
            return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
        else:
            #creating vector store 
            chunks = chunk_transcript(transcript)
            store = FAISS.from_documents(chunks, embeddings)
            store.save_local(path)
            return store
            #print(vector_store.index_to_docstore_id)
    except Exception as e:
        print(f"An error occurred: {e}")


# for i,doc in enumerate(res):
#     print(f"\ndoc {i+1} :")
#     print(f"\n{doc.page_content}")


#STEP 3 - augmentation :prompt creation using query and retrieved docs 
def format_docs(docs):
    context_text = "\n\n".join(doc.page_content for doc in docs)
    return context_text



prompt = PromptTemplate(template="""
You are an helpful assistant.
Answer ONLY for the provided transcript context.
                        
{context}
                        
question : {question}
""",
input_variables=["context","question"]
)

#STEP 4 - generation :
parser = StrOutputParser()
llm = ChatOpenAI(
    model="gpt-4o",
    api_key=api_key,
    base_url=base_url,
)



def return_response(question, video_id):
    try:
        transcript = get_video_transcript(video_id)
        vector_store = create_vector_store(video_id, transcript)
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        parallel_chain = RunnableParallel({
            "context":retriever| format_docs, #retrieve related info and format docs into plain text
            "question":RunnablePassthrough() #do not do anything just pass it to prompt
        })
        main_chain = parallel_chain| prompt | llm | parser
        response = main_chain.invoke(question)
        return response
    except Exception as e:
        return f"An error occurred while processing your request: {e}"

#print("🤖 YT Chatbot is ready!Type 'exit' to end the conversation.")

# while True:
#     user_input = input("You: ")
#     if user_input.lower() == 'exit':
#         print("Chatbot: Goodbye! 👋")
#         break
#     if not user_input.strip():
#             continue
    
#     # Get the chatbot's response
#     try:        
#         response = main_chain.invoke(user_input)
#         print(f"Chatbot: {response}\n")

#     except Exception as e:
#         print(f"error : {e}")
    



