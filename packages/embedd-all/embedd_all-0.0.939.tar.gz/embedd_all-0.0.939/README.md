# embedd-all

`embedd-all` is a Python package designed to convert various document formats into a format that can be used to create an embedding vector using embedding models. The package extracts text from PDFs, summarizes data from Excel files, and now includes functionality to create RAG (Retrieval-Augmented Generation) for documents using Voyage AI embedding models and Pinecone vector database. It supports file formats including xlsx, csv, pdf, doc, and docx.

## Features

- **Multi-format Support**: Supports PDF, Excel (xlsx, csv), and Word (doc, docx) file processing.
- **PDF Processing**: Extracts text from each page of a PDF and returns it as an array.
- **Excel Processing**: Summarizes the data in each sheet by concatenating column names and their respective values, creating a new column `df["summarized"]`. If the Excel file contains multiple sheets, it processes each sheet and returns all summaries.
- **RAG Creation**: Creates RAG for documents (all supported formats) using Voyage AI embedding models and stores them in a Pinecone vector database.

## Installation

Install the package via pip:

```bash
pip install embedd-all
```

## Usage

### Import the package

```python
from embedd_all.index import modify_excel_for_embedding, process_pdf, pinecone_embeddings_with_voyage_ai, rag_query
```

### Example Usage

#### Processing an Excel File

The `modify_excel_for_embedding` function processes an Excel file, summarizes each row, and returns the summaries.

```python
import pandas as pd
from embedd_all.embedd.index import modify_excel_for_embedding

if __name__ == '__main__':
    # Path to the Excel file
    file_path = '/path/to/your/data.xlsx'
    context = "data"

    # Process the Excel file
    dfs = modify_excel_for_embedding(file_path=file_path, context=context)

    # Display the summarized data from the second sheet (if exists)
    if len(dfs) > 1:
        logger.info(dfs[1].head(3))
```

#### Processing a PDF File

The `process_pdf` function extracts text from each page of a PDF file and returns it as an array.

```python
from embedd_all.embedd.index import process_pdf

if __name__ == '__main__':
    # Path to the PDF file
    file_path = '/path/to/your/document.pdf'

    # Process the PDF file
    texts = process_pdf(file_path)

    # Display the processed text
    logger.info("Number of pages processed: ", len(texts))
    logger.info("Sample text from the first page: ", texts[0])
```

#### Creating RAG for Documents

The `pinecone_embeddings_with_voyage_ai` function creates RAG for documents using Voyage AI embedding models and stores them in a Pinecone vector database. This function supports multiple file formats including xlsx, csv, pdf, doc, and docx.

```python
from embedd_all.embedd.index import pinecone_embeddings_with_voyage_ai

def create_rag_for_documents():
    paths = [
        '/Users/arnabbhattachargya/Desktop/flamingo_english_book.pdf',
        '/Users/arnabbhattachargya/Desktop/Data_Train.xlsx'
    ]
    vector_db_name = 'arnab-test'
    voyage_embed_model = 'voyage-2'
    embed_dimension = 1024
    pinecone_embeddings_with_voyage_ai(paths, PINECONE_KEY, VOYAGE_API_KEY, vector_db_name, voyage_embed_model, embed_dimension)

if __name__ == '__main__':
    create_rag_for_documents()
```

#### Querying with RAG

The `rag_query` function performs context-based querying using RAG (Retrieval-Augmented Generation).

```python
from embedd_all.embedd.index import rag_query

def execute_rag_query():
    CLAUDE_MODEL = "claude-3-5-sonnet-20240620"
    INDEX_NAME = 'arnab-test'
    TEMPERATURE = 0
    MAX_TOKENS = 4000
    QUERY = 'what all fuel types are there in cars?'
    SYSTEM_PROMPT = "You are a world-class document writer. Respond only with detailed descriptions and implementations. Use bullet points if necessary."
    VOYAGE_EMBED_MODEL = 'voyage-2'

    resp = rag_query(
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

    for text_block in resp:
        print(text_block.text)

if __name__ == '__main__':
    execute_rag_query()
```

## Functions

### `modify_excel_for_embedding(file_path: str, context: str) -> list`

Processes an Excel file and summarizes the data in each sheet.

- **Parameters:**
  - `file_path` (str): Path to the Excel file.
  - `context` (str): Additional context to be added to each summary.

- **Returns:**
  - `list`: A list of DataFrames, each containing the summarized data for each sheet.

### `process_pdf(file_path: str) -> list`

Extracts text from each page of a PDF file.

- **Parameters:**
  - `file_path` (str): Path to the PDF file.

- **Returns:**
  - `list`: A list of strings, each representing the text extracted from a page.

### `pinecone_embeddings_with_voyage_ai(paths: list, PINECONE_KEY: str, VOYAGE_API_KEY: str, vector_db_name: str, voyage_embed_model: str, embed_dimension: int)`

Creates RAG for documents using Voyage AI embedding models and stores them in a Pinecone vector database. Supports various document formats including xlsx, csv, pdf, doc, and docx.

- **Parameters:**
  - `paths` (list): List of paths to documents.
  - `PINECONE_KEY` (str): Pinecone API key.
  - `VOYAGE_API_KEY` (str): Voyage AI API key.
  - `vector_db_name` (str): Name of the Pinecone vector database.
  - `voyage_embed_model` (str): Name of the Voyage AI embedding model to use.
  - `embed_dimension` (int): Dimension of the embedding vectors.

### `rag_query()`

Performs context-based querying using RAG (Retrieval-Augmented Generation).

- **Parameters:**
  - `temperature` (float): Sampling temperature.
  - `max_tokens` (int): Maximum number of tokens in the response.
  - `anthropic_api_key` (str): Anthropic API key.
  - `claude_model` (str): Name of the Claude model to use.
  - `index_name` (str): Name of the Pinecone index.
  - `pinecone_key` (str): Pinecone API key.
  - `query` (str): The query to perform.
  - `system_prompt` (str): The system prompt for guiding the model's response.
  - `voyage_api_key` (str): Voyage AI API key.
  - `voyage_embed_model` (str): Name of the Voyage AI embedding model to use.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Arnab28122000/embed-all/blob/main/LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

If you have any questions or suggestions, please open an issue or contact the maintainer.

---

Happy embedding with `embedd-all`!