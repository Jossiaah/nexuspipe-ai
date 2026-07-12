import os
import time
import sqlite3
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 1. Initialize environment configurations and developer clients
load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Paths configuration
WATCH_DIRECTORY = "./input_logs"
OUTPUT_DIRECTORY = "."
DB_FILE = "pipeline_metrics.db"

# 2. Initialize the SQL Database and Create Tables
def init_database():
    """Establishes the relational database connection and creates tracking tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create a metrics log table to track multi-client transactions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT,
            openai_tokens_used INTEGER,
            anthropic_tokens_used INTEGER,
            status TEXT,
            error_message TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("🗄️  SQL Database layer initialized and listening...")

def log_pipeline_transaction(source_file, o_tokens, a_tokens, status, error_msg=""):
    """Inserts an immutable execution record into the SQL metrics ledger."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO job_metrics (source_file, openai_tokens_used, anthropic_tokens_used, status, error_message)
        VALUES (?, ?, ?, ?, ?)
    """, (source_file, o_tokens, a_tokens, status, error_msg))
    conn.commit()
    conn.close()
    print("💾 Execution metrics successfully committed to SQL database.")

def process_ai_pipeline(file_path):
    """Reads the newly dropped file, executes the AI agents, and logs stats to SQL."""
    filename = os.path.basename(file_path)
    o_tokens, a_tokens = 0, 0 # Initialize token counters for auditing
    
    try:
        print(f"\n📂 New file detected: {file_path}")
        time.sleep(1) 
        
        with open(file_path, "r") as f:
            raw_log_content = f.read().strip()
            
        if not raw_log_content:
            print("⚠️ File is empty. Skipping process.")
            log_pipeline_transaction(filename, 0, 0, "SKIPPED", "Empty file payload.")
            return

        # Agent 1 Call (OpenAI)
        print("🤖 Agent 1 (OpenAI) is triaging the raw log data...")
        openai_response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a data validation agent. Extract the core error and timestamp. Be brief."},
                {"role": "user", "content": raw_log_content}
            ]
        )
        structured_summary = openai_response.choices[0].message.content
        
        # Audit OpenAI token usage metrics
        o_tokens = openai_response.usage.total_tokens
        print(f"✅ Agent 1 Output [Tokens: {o_tokens}]: {structured_summary}")
        
        # Agent 2 Call (Anthropic)
        print("🤖 Agent 2 (Anthropic) is generating the root-cause markdown report...")
        anthropic_response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            temperature=0.3,
            system="You are an expert systems engineer. Draft a professional Markdown incident report based on this summary.",
            messages=[{"role": "user", "content": f"Create a report for: {structured_summary}"}]
        )
        
        final_report = anthropic_response.content[0].text
        
        # Audit Anthropic token usage metrics safely
        a_tokens = anthropic_response.usage.input_tokens + anthropic_response.usage.output_tokens
        print(f"✅ Agent 2 Output [Tokens: {a_tokens}]")
        
        # Save output markdown asset
        output_filename = f"incident_report_{int(time.time())}.md"
        output_path = os.path.join(OUTPUT_DIRECTORY, output_filename)
        with open(output_path, "w") as f:
            f.write(final_report)
            
        print(f"🎉 Success! Automated report saved to: {output_path}")
        
        # Log successful transaction into SQL ledger
        log_pipeline_transaction(filename, o_tokens, a_tokens, "SUCCESS")
        
    except Exception as e:
        print(f"❌ Automation Pipeline Failed: {e}")
        # Log systemic failures into SQL ledger for dashboard visibility
        log_pipeline_transaction(filename, o_tokens, a_tokens, "FAILED", str(e))

# 3. Set up the automated folder watching event loop
class LogFolderHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and not event.src_path.endswith(".DS_Store"):
            process_ai_pipeline(event.src_path)

if __name__ == "__main__":
    # Ensure folder and database exist before starting execution loops
    if not os.path.exists(WATCH_DIRECTORY):
        os.makedirs(WATCH_DIRECTORY)
        
    init_database()
    print(f"👁️  AI Watcher active. Monitoring folder '{WATCH_DIRECTORY}' for incoming files...")
    
    event_handler = LogFolderHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_DIRECTORY, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping AI Folder Watcher...")
        observer.stop()
    observer.join()
