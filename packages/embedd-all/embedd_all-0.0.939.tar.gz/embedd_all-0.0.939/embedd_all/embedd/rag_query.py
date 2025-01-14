import voyageai
import anthropic
import time
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI


def rag_and_query(pinecone_key: str, voyage_api_key: str, voyage_embed_model: str, index_name: str, anthropic_api_key: str, system_prompt: str, claude_model: str, query: str, max_tokens: int, temperature: float) -> str:
    
    pinecone_key = pinecone_key
    voyage_api_key = voyage_api_key
    VOYAGE_EMBED_MODEL = voyage_embed_model

    vo = voyageai.Client(api_key=voyage_api_key)

    query = query

    prompt = query

    result = vo.embed(texts=[query], model=VOYAGE_EMBED_MODEL, input_type="document")

    index_name = index_name

    pc = Pinecone(api_key=pinecone_key)

    cloud = 'aws'
    region = 'us-east-1'

    spec = ServerlessSpec(cloud=cloud, region=region)

    if index_name not in pc.list_indexes().names():
    # if does not exist, create index
        pc.create_index(
            index_name,
            dimension=1024,
            metric='cosine',
            spec=spec
    )
    # wait for index to be initialized
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)
    
    # connect to index
    index = pc.Index(index_name)
        # view index stats
    index.describe_index_stats()

    # query converted to embedding
    xq = result.embeddings[0]

    res = index.query(vector=xq, top_k=13,  include_metadata=True)

    limit = 100000

    contexts = [
        x['metadata']['content'] for x in res['matches']
    ]

    ANTHROPIC_API_KEY= anthropic_api_key

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # build our prompt with the retrieved contexts included
    prompt_start = (
        "Answer the question based on the context below.\n\n"+
        "Context:\n"
    )
    prompt_end = (
        f"\n\nQuestion: {query}\nAnswer:"
    )
    # append contexts until hitting limit
    for i in range(1, len(contexts)):
        if len("\n\n---\n\n".join(contexts[:i])) >= limit:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts[:i-1]) +
                prompt_end
            )
            break
        elif i == len(contexts)-1:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts) +
                prompt_end
            )

    message = client.messages.create(
        model=claude_model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }   
                ]
            }
        ]
    )
    return message.content

def rag_and_query_openai(
    pinecone_key: str, 
    openai_api_key: str, 
    openai_embed_model: str,
    openai_chat_model: str,
    index_name: str, 
    system_prompt: str, 
    query: str, 
    max_tokens: int, 
    temperature: float,
    embed_dimension: int = 1536  # Default for text-embedding-3-small
) -> str:
    """
    Perform RAG query using OpenAI's embedding and chat completion models
    
    Args:
        pinecone_key: Pinecone API key
        openai_api_key: OpenAI API key
        openai_embed_model: OpenAI embedding model name
        openai_chat_model: OpenAI chat completion model name
        index_name: Pinecone index name
        system_prompt: System prompt for chat completion
        query: User query
        max_tokens: Maximum tokens for response
        temperature: Temperature for response generation
        embed_dimension: Embedding dimension (depends on model)
    """
    from openai import OpenAI
    
    # Initialize OpenAI client
    client = OpenAI(api_key=openai_api_key)
    
    # Create embedding for query
    result = client.embeddings.create(
        model=openai_embed_model,
        input=[query],
        encoding_format="float"
    )
    query_embedding = result.data[0].embedding

    # Initialize Pinecone
    pc = Pinecone(api_key=pinecone_key)
    
    # Connect to index
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            index_name,
            dimension=embed_dimension,
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
    
    index = pc.Index(index_name)
    
    # Query Pinecone
    res = index.query(
        vector=query_embedding,
        top_k=5,
        include_metadata=True
    )

    # Extract contexts
    contexts = [x['metadata']['content'] for x in res['matches']]
    
    # Build prompt
    prompt = (
        "Answer the question based on the context below.\n\n"
        "Context:\n" +
        "\n\n---\n\n".join(contexts) +
        f"\n\nQuestion: {query}\nAnswer:"
    )

    # Get completion from OpenAI
    completion = client.chat.completions.create(
        model=openai_chat_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )

    return completion.choices[0].message.content


def context_and_query(anthropic_api_key: str, system_prompt: str, claude_model: str, query: str, max_tokens: int, temperature: float, context: str) -> str:
    query = query

    ANTHROPIC_API_KEY= anthropic_api_key

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = "Question: " + query + " \n Context: " + context + '\n Note: Make sure that if Question is not relevant to the given Context do not answer. Say this question is out of scope'

    message = client.messages.create(
        model=claude_model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }   
                ]
            }
        ]
    )
    return message.content

def context_and_query_model(api_key: str, ai: str, system_prompt: str, model: str, query: str, max_tokens: int, temperature: float, context: str) -> str:
    query = query

    API_KEY= api_key
    output = ""

    prompt = "QUESTION: " + query + " \n CONTEXT: " + context
    # + '\n Note: Make sure that if Question is not relevant to the given Context do not answer. Say this question is out of scope'


    print(prompt)



    if ai == "ANTHROPIC":
        client = anthropic.Anthropic(api_key=API_KEY)
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }   
                    ]
                }
            ]
        )
        output = message.content
    elif ai == "OPENAI":
        client = OpenAI(api_key=API_KEY)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={ "type": "json_object" }
        )

        output = completion.choices[0].message.content

    return output