import sqlite3
import requests
import json

class SQLiteAnalyzer:
    def __init__(self, db_path, ollama_url='http://localhost:11434'):
        self.db_path = db_path
        self.ollama_url = ollama_url
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def get_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in cursor.fetchall()]

    def get_table_schema(self, table_name):
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return cursor.fetchall()

    def get_sample_data(self, table_name, limit=5):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        return cursor.fetchall()

    def get_table_stats(self, table_name):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        return {'row_count': count}

    def generate_database_description(self):
        tables = self.get_tables()
        description = f"数据库路径: {self.db_path}\n\n"
        description += "=== 数据库结构 ===\n\n"

        for table in tables:
            description += f"表名: {table}\n"
            schema = self.get_table_schema(table)
            description += "字段信息:\n"
            for col in schema:
                description += f"  - {col[1]} ({col[2]})\n"

            stats = self.get_table_stats(table)
            description += f"总行数: {stats['row_count']}\n"

            sample = self.get_sample_data(table, 3)
            description += f"示例数据 (前3条):\n"
            for row in sample:
                description += f"  {dict(row)}\n"
            description += "\n"

        return description

    def analyze_with_ai(self, question=None):
        description = self.generate_database_description()

        system_prompt = """You are a bilingual AI assistant (Chinese/English). When responding to user questions:

1. Use Chinese as the primary language for main explanations and analysis
2. Use English for technical terms, SQL code, table/column names, and data examples
3. Keep the response structured and professional
4. Provide clear, actionable insights
5. Use a natural mix: 70% Chinese + 30% English

Example format:
中文解释要点，technical term in English. Code snippet:
SELECT * FROM table_name
More Chinese explanation...

Please answer in this bilingual style."""

        if question:
            prompt = f"""Analyze the database and answer the user's question:

{description}

User Question: {question}

Please provide detailed bilingual analysis (Chinese + English) with insights and recommendations."""
        else:
            prompt = f"""Analyze the database and provide detailed insights:

{description}

Please provide:
1. Overall database overview (数据库整体概况)
2. Data characteristics of each table (各表的数据特点)
3. Potential business scenarios (可能的业务场景分析)
4. Data quality assessment (数据质量评估)
5. Improvement recommendations (改进建议)

Please answer in bilingual style (Chinese + English)."""

        response = requests.post(
            f'{self.ollama_url}/api/generate',
            json={
                'model': 'llama2',
                'prompt': prompt,
                'stream': False,
                'system': system_prompt
            },
            timeout=300
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('response', '分析失败 / Analysis failed')
        else:
            return f"调用 AI 失败 / AI call failed: {response.status_code} - {response.text}"

    def execute_query(self, query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return {'columns': columns, 'rows': [dict(row) for row in results]}
        except Exception as e:
            return {'error': str(e)}

    def interactive_mode(self):
        print("=== SQLite 数据库 AI 分析工具 ===")
        print(f"数据库: {self.db_path}")
        print(f"Ollama: {self.ollama_url}")
        print("\n命令:")
        print("  analyze - 使用 AI 分析整个数据库")
        print("  ask <问题> - 向 AI 提问关于数据库的问题")
        print("  tables - 查看所有表")
        print("  schema <表名> - 查看表结构")
        print("  query <SQL语句> - 执行 SQL 查询")
        print("  quit - 退出")

        while True:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'quit':
                break

            elif user_input.lower() == 'tables':
                tables = self.get_tables()
                print(f"\n数据库中的表: {', '.join(tables)}")

            elif user_input.lower().startswith('schema '):
                table_name = user_input[7:].strip()
                schema = self.get_table_schema(table_name)
                print(f"\n表 {table_name} 的结构:")
                for col in schema:
                    print(f"  {col[1]}: {col[2]}")

            elif user_input.lower().startswith('query '):
                query = user_input[7:].strip()
                result = self.execute_query(query)
                if 'error' in result:
                    print(f"\n错误: {result['error']}")
                else:
                    print(f"\n查询结果:")
                    for row in result['rows']:
                        print(f"  {row}")

            elif user_input.lower() == 'analyze':
                print("\n正在分析数据库 / Analyzing database，请稍候 / please wait...")
                result = self.analyze_with_ai()
                print(f"\n{result}")

            elif user_input.lower().startswith('ask '):
                question = user_input[4:].strip()
                print(f"\n正在回答问题 / Answering question: {question}")
                print("请稍候 / Please wait...")
                result = self.analyze_with_ai(question)
                print(f"\n{result}")

            else:
                print("未知命令。输入 'help' 查看可用命令")

def main():
    analyzer = SQLiteAnalyzer('example.db', 'http://localhost:11434')
    analyzer.connect()

    try:
        analyzer.interactive_mode()
    finally:
        analyzer.disconnect()

if __name__ == '__main__':
    main()
