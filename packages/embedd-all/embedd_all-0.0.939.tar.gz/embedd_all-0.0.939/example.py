from embedd_all.embedd.index import convert_files_to_context, modify_excel_for_embedding, process_pdf, pinecone_embeddings_with_voyage_ai, modify_csv_for_embedding
from embedd_all.embedd.rag_query import context_and_query_model, rag_and_query, context_and_query, rag_and_query_openai
import os

ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']
OPEN_AI_API_KEY = os.environ['OPEN_AI_API_KEY']
PINECONE_KEY = os.environ['PINECONE_KEY']
VOYAGE_API_KEY = os.environ['VOYAGE_API_KEY']

paths = ['/Users/arnabbhattachargya/Downloads']

def create_rag_for_pdfs_excels_csvs():
    # paths = ['/Users/arnabbhattachargya/Desktop/flamingo_english_book.pdf', '/Users/arnabbhattachargya/Desktop/Data_Train.xlsx', '/Users/arnabbhattachargya/Downloads/flamingo book.docx']
    paths = ['/Users/arnabbhattachargya/Downloads/RPD+Internal+FAQ.doc', '/Users/arnabbhattachargya/Downloads/flamingo book.docx', '/Users/arnabbhattachargya/Desktop/flamingo_english_book.pdf', '/Users/arnabbhattachargya/Desktop/Data_Train.xlsx']
    vector_db_name = 'arnab-test'
    voyage_embed_model = 'voyage-2'
    # dimensions of embed model
    embed_dimension=1024
    pinecone_embeddings_with_voyage_ai(paths, PINECONE_KEY, VOYAGE_API_KEY, vector_db_name, voyage_embed_model, embed_dimension)

def query_with_context():
    CLAUDE_MODEL = "claude-3-5-sonnet-20240620"
    SYSTEM_PROMPT = "You are a world-class medicine expert. Respond only with detailed information"
    TEMPERATURE = 0
    MAX_TOKENS = 4000
    QUERY = 'what medications to take when we feel sick'
    CONTEXT = """
       Medicine related context
    """
    answer = context_and_query(ANTHROPIC_API_KEY, SYSTEM_PROMPT, CLAUDE_MODEL, QUERY, MAX_TOKENS, TEMPERATURE, CONTEXT)
    print(answer)

def query_with_context_file():
    paths = ["/Users/arnabbhattachargya/Downloads/Framekode API v1.pdf"]
    file_context = convert_files_to_context(paths)
    MODEL = "gpt-4o-mini"
    SYSTEM_PROMPT = """
        You are a world-class CRUD API expert. 
        You will be given an API doc a you have to verify and separate fetch, payment, validate and token or auth requests in the form of an array.
        "data": [
            {
                "id": 0,
                "request_type": "POST" this can be GET, POST, PUT, DELETE etc,
                "base_url": "",
                "params": "",
                "headers": JSON Type,
                "payload": JSON Type,
                "proof_of_truth": string type // What part of the given context was used to generate this object,
                "curl": request curl
                ""
            },
            {
                "id": 1,
                "request_type": "POST" this can be GET, POST, PUT, DELETE etc,
                "base_url": "",
                "params": "",
                "headers": JSON Type,
                "payload": JSON Type,
                "proof_of_truth": string type // What part of the given context was used to generate this object,
                "curl": request curl
                ""
            }
        ]

    """
    TEMPERATURE = 0
    MAX_TOKENS = 2000
    QUERY = """
         Here is the API doc that may contain fetch payment validate and token APIs. 
        Output JSON in this format
        "data": [
            {
                "id": 0,
                "request_type": "POST" this can be GET, POST, PUT, DELETE etc,
                "base_url": "",
                "params": "",
                "headers": JSON Type,
                "payload": JSON Type,
                "proof_of_truth": string type // What part of the given context was used to generate this object,
                "curl": request curl
                ""
            },
            {
                "id": 1,
                "request_type": "POST" this can be GET, POST, PUT, DELETE etc,
                "base_url": "",
                "params": "",
                "headers": JSON Type,
                "payload": JSON Type,
                "proof_of_truth": string type // What part of the given context was used to generate this object,
                "curl": request curl
                ""
            }
        ]
    """
    CONTEXT = """
    """
    CONTEXT = CONTEXT + file_context
    api_key = OPEN_AI_API_KEY
    answer = context_and_query_model(
        api_key=api_key, 
        ai="OPENAI", 
        system_prompt=SYSTEM_PROMPT, 
        model=MODEL, 
        query=QUERY, 
        max_tokens=MAX_TOKENS, 
        temperature=TEMPERATURE, 
        context=CONTEXT
    )
    print(answer)



def rag_query():
    CLAUDE_MODEL = "claude-3-5-sonnet-20240620"
    #inddex name for pine_cone vector db
    INDEX_NAME = 'arnab-test'
    TEMPERATURE = 0
    MAX_TOKENS = 4000
    QUERY = 'what all fuel types are there is cars?'
    SYSTEM_PROMPT = "You are a world-class document writer. Respond only with detailed description and implementation. Use bullet points if neccessary"
    VOYAGE_EMBED_MODEL = 'voyage-2'

    resp = rag_and_query(
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        anthropic_api_key=ANTHROPIC_API_KEY,
        claude_model=CLAUDE_MODEL, 
        index_name=INDEX_NAME, 
        pinecone_key=PINECONE_KEY, 
        query=QUERY, 
        system_prompt=SYSTEM_PROMPT,
        voyage_api_key=VOYAGE_API_KEY,
        voyage_embed_model=VOYAGE_EMBED_MODEL
        )
    
    # print("resp: ", resp["text"])

    for text_block in resp:
        print(text_block.text)


if __name__ == '__main__':
    # Example usage
    # file_path = '/Users/arnabbhattachargya/Downloads/currency.csv'
    # context = "data"
    # dfs = modify_excel_for_embedding(file_path=file_path, context=context)
    # print(dfs[0][0])

    # texts = process_pdf(file_path)
    # print("Text Length: ", len(texts))
    # print("Text process: ", texts)
    # rag_query()
    # dfs = modify_csv_for_embedding(file_path, context)
    # texts = [text for df in dfs for text in df]
    # print("Length: ", len(texts))
    # print(df[0][0])
    # create_rag_for_pdfs_excels_csvs()
    query_with_context_file()
    # create_rag_for_pdfs()
    # query_with_context()