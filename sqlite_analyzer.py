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

        system_prompt = """You are a database analysis assistant. Please follow these rules:

1. Answer entirely in Chinese (中文回答)
2. Keep technical terms that are hard to translate in English, such as:
   - SQL keywords: SELECT, WHERE, FROM, JOIN, etc.
   - Database terms: PRIMARY KEY, FOREIGN KEY, etc.
   - Table names and column names
   - Specific technology names: Ollama, llama2, etc.
3. Code examples and SQL queries should remain in English
4. Provide clear, detailed analysis in Chinese

请用中文回答，只保留不易翻译的英文术语。"""

        if question:
            prompt = f"""基于以下数据库信息，回答用户的问题：

{description}

用户问题: {question}

请用中文详细回答，提供相关的数据分析和见解。"""
        else:
            prompt = f"""请分析以下数据库，提供详细的数据分析和业务见解：

{description}

请提供：
1. 数据库整体概况
2. 各表的数据特点
3. 可能的业务场景分析
4. 数据质量评估
5. 改进建议

请用中文详细回答。"""

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
            return result.get('response', '分析失败')
        else:
            return f"调用 AI 失败: {response.status_code} - {response.text}"

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
                print("\n正在分析数据库，请稍候...")
                result = self.analyze_with_ai()
                print(f"\n{result}")

            elif user_input.lower().startswith('ask '):
                question = user_input[4:].strip()
                print(f"\n正在回答问题: {question}")
                print("请稍候...")
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
