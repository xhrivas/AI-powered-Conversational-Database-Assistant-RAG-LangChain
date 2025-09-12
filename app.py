
# Importing Google's Generative AI SDK  for Gemini model )
import google.generativeai as genai

# Importing MySQL connector for Python to establish database connections
import mysql.connector

# Importing Streamlit to create the web-based UI for the application
import streamlit as st

# Configure Google Generative AI with your API key
genai.configure(api_key="your_API_KEY")


# Load the Gemini 1.5 Flash model from Google's Generative AI
model = genai.GenerativeModel("models/gemini-1.5-flash")



# Streamlit UI configuration: set page title, icon, and layout
st.set_page_config(
    page_icon="🛢️",

    page_title="Database Query App",

    layout = "centered"
)

# Main header of the app
st.header("🤖 Chat with MYSQL DB")


# Sidebar section for database connection input

with st.sidebar:
    st.subheader("🛢️Connect Database Here")  # Sidebar title


    # Text input fields to collect database connection details
    host=st.text_input("Host", key="H", value="localhost")
    port=st.text_input("Port", key="P")
    Username=st.text_input("Username", key="U")
    password=st.text_input("Password", type="password", key="PA")
    database=st.text_input("Database", key="D")

# Connect button
    connectBtn = st.button(" 🌐 Connect to Database")
    


# Function to connect to the MySQL database
def connectDatabase(host, port, Username, password, database):

        st.session_state.db = mysql.connector.connect(
        host=host,
        port=port,
        user=Username,
        password=password,
        database=database
    )

# When the connect button is clicked
if connectBtn:
   # Validate that all required fields are filled in
    if all(k in st.session_state and st.session_state[k] for k in ("H", "P", "U", "PA", "D")):
        try:
            connectDatabase(
                host=st.session_state.H,
                port=int(st.session_state.P), # Convert port to integer
                Username=st.session_state.U,
                password=st.session_state.PA,
                database=st.session_state.D,
            )
            # show success message
            st.success("Database connected!")
        except Exception as e:
             # Display error message if connection fails
            st.write(f"Connection failed: {e}")
    else:
        # Warn user if any field is empty
        st.warning("Please fill in all fields.")




        #Show success message when connected
        st.success("Database connected")


# Chat input field for user to enter a natural language question
question = st.chat_input('Chat with your mysql database')

# Function to run raw SQL queries
def runQuery(query):
    # Check if DB is connected
    if not st.session_state.db:
        return "please connect to database"
      # Run query
    cursor = st.session_state.db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result




# Function to get schema of all tables in the connected database
def getDatabaseSchema():
    cursor = st.session_state.db.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    schema = []
    for (table_name,) in tables:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        schema.append((table_name, columns))
    return schema



# Function to generate SQL query using Gemini and schema context
def Generate_SQL_Query(question,schema):
    prompt = f"""
     below is the schema of mySql database,please answer user's quesion in the from of SQL query by looking into the schema for best query 

    {schema}
    
    question:
    SQL query :
    please only provide the SQL query and nothing else

    for example :
    question : how many albums we have in database
    SQL query: SELECT COUNT(DISTINCT student_roll_no) AS total_students FROM marks;
    \"\"\"
    {question}
    \"\"\"
    """
    
    response = model.generate_content(prompt)
    return response.text





# Function to convert SQL result into a natural language explanation
def Convert_Natural_lang(result1):
    prompt = f"""
    You are a professional data analyst assistant. Your job is to convert raw SQL query results into clear and polished natural language explanations for non-technical users.

    Here is an example:

    SQL Result:
    [('Mathematics',), ('English',), ('Science',), ('History',)]
    formate : convet proper formate like a tabel
    Expected Output:
    In the database, a total of 4 subjects are present.
      Their names are:,
        1: Mathematics, 
        2: English,
        3: Science,
        4: History.

    Now use the same format and tone to convert the following SQL result into natural language:

    \"\"\"
    {result1}
    \"\"\"
    """
    
    response1 = model.generate_content(prompt)
    return response1.text


# Core function to handle the full question-to-answer workflow
def Generate_Output(Question,host, port, Username, password,  database):

    # Clean SQL formatting if LLM wraps in ```sql blocks
    def clean_sql(query):
        return query.replace("```sql", "").replace("```", "").strip()



   # Step 1: Connect to DB

    connectDatabase(host, port, Username, password,  database)

      # Step 2: Generate SQL query using LLM
    ans = Generate_SQL_Query(question=Question, schema=getDatabaseSchema())
    sql_query = clean_sql(ans)

    # Step 3: Execute SQL query
    result = runQuery(sql_query)




#   Step 4: Convert SQL result to natural language
    var1=((Convert_Natural_lang(result1=result)))

    
    # Step 5: Display the response
    st.subheader(var1)


#  Run the app only if user asks a question
if question :
        # Make sure DB is connected first
    if "db" not in st.session_state:
        st.error('please connect database first.')
    else:
         # Show user's question in chat
        st.chat_message('user').markdown(question)
        (Generate_Output(question,host, port, Username, password,  database))
        # st.chat_message("assistant").markdown(question)
    
