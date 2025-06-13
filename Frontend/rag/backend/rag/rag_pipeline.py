import os
from dotenv import load_dotenv
import re

# ✅ LangChain & Gemini
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate

# ✅ Load API key from .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ✅ Initialize Gemini Pro LLM and Embedding Model
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY
)

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GOOGLE_API_KEY
)

# ✅ Few-shot examples: Natural language to SQL pairs
examples = [

    # 🟦 Basic status queries
    ("Where is batch VDT-052025-A?",
     "SELECT status FROM batch_tracking JOIN batches ON batch_tracking.batch_id = batches.id WHERE batches.batch_code = 'VDT-052025-A' ORDER BY timestamp DESC LIMIT 1;"),

    ("What is the current status of batch PRG-052025-B?",
     "SELECT status FROM batch_tracking JOIN batches ON batch_tracking.batch_id = batches.id WHERE batches.batch_code = 'PRG-052025-B' ORDER BY timestamp DESC LIMIT 1;"),

    ("What are all the statuses for batch VDT-052025-A in order?",
     "SELECT status FROM batch_tracking JOIN batches ON batch_tracking.batch_id = batches.id WHERE batches.batch_code = 'VDT-052025-A' ORDER BY timestamp;"),

    # 🟦 Who did what
    ("Who delivered VDT-052025-A?",
     "SELECT employees.name FROM batch_tracking JOIN batches ON batch_tracking.batch_id = batches.id JOIN employees ON batch_tracking.employee_id = employees.id WHERE batches.batch_code = 'VDT-052025-A' AND batch_tracking.status = 'Dispatched';"),

    ("Who inspected batch CSY-052025-C?",
     "SELECT employees.name FROM batch_tracking JOIN batches ON batch_tracking.batch_id = batches.id JOIN employees ON batch_tracking.employee_id = employees.id WHERE batches.batch_code = 'CSY-052025-C' AND batch_tracking.status = 'Inspected';"),

    ("Which employee stored CSY-052025-C?",
     "SELECT employees.name FROM batch_tracking JOIN batches ON batch_tracking.batch_id = batches.id JOIN employees ON batch_tracking.employee_id = employees.id WHERE batches.batch_code = 'CSY-052025-C' AND batch_tracking.status = 'Stored';"),

    ("Which batches did John work on?",
     "SELECT DISTINCT batches.batch_code FROM batches JOIN batch_tracking ON batches.id = batch_tracking.batch_id JOIN employees ON batch_tracking.employee_id = employees.id WHERE employees.name = 'John';"),

    ("Which batches did Riya store?",
     "SELECT batches.batch_code FROM batches JOIN batch_tracking ON batches.id = batch_tracking.batch_id JOIN employees ON batch_tracking.employee_id = employees.id WHERE batch_tracking.status = 'Stored' AND employees.name = 'Riya';"),

    # 🟨 Department
    ("Which department handled PRG-052025-B?",
     "SELECT departments.name FROM batch_tracking JOIN batches ON batch_tracking.batch_id = batches.id JOIN departments ON batch_tracking.department_id = departments.id WHERE batches.batch_code = 'PRG-052025-B';"),

    ("Which department dispatched PRG-052025-B?",
     "SELECT departments.name FROM batch_tracking JOIN batches ON batch_tracking.batch_id = batches.id JOIN departments ON batch_tracking.department_id = departments.id WHERE batches.batch_code = 'PRG-052025-B' AND batch_tracking.status = 'Dispatched';"),

    ("Which departments were involved in VDT-052025-A?",
     "SELECT DISTINCT departments.name FROM batch_tracking JOIN batches ON batch_tracking.batch_id = batches.id JOIN departments ON batch_tracking.department_id = departments.id WHERE batches.batch_code = 'VDT-052025-A';"),

    ("Which department inspected VDT-052025-A?",
     "SELECT departments.name FROM batch_tracking JOIN batches ON batch_tracking.batch_id = batches.id JOIN departments ON batch_tracking.department_id = departments.id WHERE batches.batch_code = 'VDT-052025-A' AND batch_tracking.status = 'Inspected';"),

    # 🟪 Products
    ("What is the product for batch VDT-052025-A?",
     "SELECT products.name FROM batches JOIN products ON batches.product_id = products.id WHERE batches.batch_code = 'VDT-052025-A';"),

    ("What are all batches for Cough Syrup?",
     "SELECT batches.batch_code FROM batches JOIN products ON batches.product_id = products.id WHERE products.name = 'Cough Syrup';"),

    ("Which product did Anna dispatch?",
     "SELECT DISTINCT products.name FROM products JOIN batches ON products.id = batches.product_id JOIN batch_tracking ON batches.id = batch_tracking.batch_id JOIN employees ON batch_tracking.employee_id = employees.id WHERE batch_tracking.status = 'Dispatched' AND employees.name = 'Anna';"),

    # 🟩 Time and History
    ("When was batch CSY-052025-C dispatched?",
     "SELECT timestamp FROM batch_tracking JOIN batches ON batch_tracking.batch_id = batches.id WHERE batches.batch_code = 'CSY-052025-C' AND batch_tracking.status = 'Dispatched' ORDER BY timestamp DESC LIMIT 1;"),

    ("Show the full processing history of VDT-052025-A",
     "SELECT employees.name AS employee, departments.name AS department, batch_tracking.status, batch_tracking.timestamp FROM batch_tracking JOIN batches ON batch_tracking.batch_id = batches.id JOIN employees ON batch_tracking.employee_id = employees.id JOIN departments ON batch_tracking.department_id = departments.id WHERE batches.batch_code = 'VDT-052025-A' ORDER BY timestamp;"),

    # 🟥 Summary & Lists
    ("List all batches that were stored.",
     "SELECT DISTINCT batches.batch_code FROM batches JOIN batch_tracking ON batches.id = batch_tracking.batch_id WHERE batch_tracking.status = 'Stored';"),

    ("List all employees who handled Dispatched status.",
     "SELECT DISTINCT employees.name FROM employees JOIN batch_tracking ON employees.id = batch_tracking.employee_id WHERE batch_tracking.status = 'Dispatched';"),

    ("Which employees belong to the Storage department?",
     "SELECT employees.name FROM employees JOIN departments ON employees.department_id = departments.id WHERE departments.name = 'Storage';"),
]

docs = [Document(page_content=f"{q.strip()} => {s.strip()}") for q, s in examples]

# ✅ Schema Metadata for FAISS
schema_metadata = [
    Document(page_content="Table: departments - Stores department info"),
    Document(page_content="Column: departments.id - Unique department ID"),
    Document(page_content="Column: departments.name - Department name"),

    Document(page_content="Table: employees - Stores employee records"),
    Document(page_content="Column: employees.id - Employee ID"),
    Document(page_content="Column: employees.name - Name of employee"),
    Document(page_content="Column: employees.department_id - FK to departments"),

    Document(page_content="Table: products - Product details"),
    Document(page_content="Column: products.id - Product ID"),
    Document(page_content="Column: products.name - Product name"),
    Document(page_content="Column: products.code - Product code"),

    Document(page_content="Table: batches - Contains batch data"),
    Document(page_content="Column: batches.id - Batch ID"),
    Document(page_content="Column: batches.batch_code - Batch code"),
    Document(page_content="Column: batches.product_id - FK to product"),

    Document(page_content="Table: batch_tracking - Tracks batch status"),
    Document(page_content="Column: batch_tracking.id - Tracking ID"),
    Document(page_content="Column: batch_tracking.batch_id - FK to batch"),
    Document(page_content="Column: batch_tracking.status - Stage like Packed, Dispatched"),
    Document(page_content="Column: batch_tracking.department_id - FK to department"),
    Document(page_content="Column: batch_tracking.employee_id - FK to employee"),
    Document(page_content="Column: batch_tracking.timestamp - Time of update"),
]

# ✅ FAISS: Load if exists, else build and save
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
index_path = "faiss_index"

if os.path.exists(index_path):
    vectorstore = FAISS.load_local(index_path, embedding_model, allow_dangerous_deserialization=True)
else:
    texts = text_splitter.split_documents(docs + schema_metadata)
    vectorstore = FAISS.from_documents(texts, embedding_model)
    vectorstore.save_local(index_path)

# ✅ Helper to clean LLM output
def clean_sql_response(response_text: str) -> str:
    code_blocks = re.findall(r"```sql(.*?)```", response_text, re.DOTALL)
    if code_blocks:
        return code_blocks[0].strip()

    lines = response_text.strip().splitlines()
    sql_lines = [line for line in lines if any(keyword in line.upper() for keyword in ["SELECT", "INSERT", "UPDATE", "DELETE", "JOIN", "FROM", "WHERE", "ORDER", "GROUP", "LIMIT"])]
    
    sql_only = []
    for line in sql_lines:
        sql_only.append(line.strip())
        if ";" in line:
            break

    return " ".join(sql_only) if sql_only else "-- No valid SQL found"

# ✅ Main callable used by FastAPI route
def get_sql_from_question(question: str) -> str:
    relevant_docs = vectorstore.similarity_search(question)
    context = "\n".join([doc.page_content.strip() for doc in relevant_docs])

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are an expert SQL assistant. Use only the column and table names provided in the examples and schema.

Examples:
{context}

Question:
{question}

Only write valid SQL using exact column and table names. Do not guess.

SQL Query:
"""

    )

    final_prompt = prompt.format(context=context, question=question)

    try:
        response = llm.invoke(final_prompt)
        sql_query = response.content
        return clean_sql_response(sql_query)
    except Exception as e:
        return f"-- ERROR: LLM failed to respond\n-- Reason: {str(e)}"
#Only respond with a valid SQL query. If no question is asked, respond with:
#-- ERROR: Missing valid user question

