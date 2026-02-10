import sqlite3
import requests
import json
import os
import sys
import configparser
from collections import defaultdict

class SQLiteAnalyzer:
    def __init__(self, db_path, ai_provider='ollama', api_config=None):
        self.db_path = db_path
        self.ai_provider = ai_provider
        self.api_config = api_config or {}
        self.conn = None

        if ai_provider == 'ollama':
            self.ollama_url = api_config.get('url', 'http://localhost:11434') if api_config else 'http://localhost:11434'
        elif ai_provider == 'doubao':
            self.doubao_api_key = api_config.get('api_key') if api_config else ''
            self.doubao_model = api_config.get('model') if api_config else 'doubao-pro-32k'
            self.doubao_endpoint = api_config.get('endpoint') if api_config else 'https://ark.cn-beijing.volces.com/api/v3'

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

        system_prompt = """你是一个数据库分析助手。请按照以下规则进行分析：

1. 使用中文回答
2. 保留不易翻译的英文术语
3. 提供详细的数据分析和见解
4. 给出可操作的建议"""

        if question:
            user_message = f"""基于以下数据库信息，回答用户的问题：

{description}

用户问题: {question}

请用中文详细回答，提供相关的数据分析和见解。"""
        else:
            user_message = f"""请分析以下数据库，提供详细的数据分析和业务见解：

{description}

请提供：
1. 数据库整体概况
2. 各表的数据特点
3. 可能的业务场景分析
4. 数据质量评估
5. 改进建议

请用中文详细回答。"""

        if self.ai_provider == 'ollama':
            response = self._call_ollama(system_prompt, user_message)
        elif self.ai_provider == 'doubao':
            response = self._call_doubao(system_prompt, user_message)
        else:
            response = "不支持的 AI 提供商"

        return response

    def _call_ollama(self, system_prompt, user_message):
        """调用 Ollama API"""
        response = requests.post(
            f'{self.ollama_url}/api/generate',
            json={
                'model': 'llama2',
                'prompt': user_message,
                'stream': False,
                'system': system_prompt
            },
            timeout=300
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('response', '分析失败')
        else:
            return f"调用 Ollama 失败: {response.status_code} - {response.text}"

    def _call_doubao(self, system_prompt, user_message):
        """调用豆包 AI API"""
        headers = {
            'Authorization': f'Bearer {self.doubao_api_key}',
            'Content-Type': 'application/json'
        }

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ]

        data = {
            'model': self.doubao_model,
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 4096
        }

        response = requests.post(
            f'{self.doubao_endpoint}/chat/completions',
            headers=headers,
            json=data,
            timeout=300
        )

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"调用豆包 AI 失败: {response.status_code} - {response.text}"

    def execute_query(self, query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return {'columns': columns, 'rows': [dict(row) for row in results]}
        except Exception as e:
            return {'error': str(e)}

    def discover_foreign_keys(self):
        """发现数据库中的外键关系"""
        cursor = self.conn.cursor()
        tables = self.get_tables()
        foreign_keys = defaultdict(list)

        for table in tables:
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fk_list = cursor.fetchall()

            for fk in fk_list:
                id, seq, table_name, from_col, to_col, on_update, on_delete, match = fk
                foreign_keys[table].append({
                    'from_column': from_col,
                    'referenced_table': table_name,
                    'referenced_column': to_col,
                    'on_update': on_update,
                    'on_delete': on_delete
                })

        return dict(foreign_keys)

    def discover_data_relationships(self, similarity_threshold=0.7):
        """基于数据内容发现隐式关联"""
        cursor = self.conn.cursor()
        tables = self.get_tables()
        relationships = []

        for i, table1 in enumerate(tables):
            if table1.startswith('sqlite_'):
                continue

            schema1 = self.get_table_schema(table1)
            cols1 = [col[1] for col in schema1 if col[2] in ['INTEGER', 'TEXT']]

            for j, table2 in enumerate(tables):
                if i >= j or table2.startswith('sqlite_'):
                    continue

                schema2 = self.get_table_schema(table2)
                cols2 = [col[1] for col in schema2 if col[2] in ['INTEGER', 'TEXT']]

                for col1 in cols1:
                    for col2 in cols2:
                        if self._column_names_similar(col1, col2):
                            overlap_ratio = self._calculate_data_overlap(cursor, table1, col1, table2, col2)

                            if overlap_ratio >= similarity_threshold:
                                relationships.append({
                                    'type': 'data_overlap',
                                    'table1': table1,
                                    'column1': col1,
                                    'table2': table2,
                                    'column2': col2,
                                    'overlap_ratio': overlap_ratio,
                                    'confidence': 'high' if overlap_ratio > 0.9 else 'medium'
                                })

        return relationships

    def _column_names_similar(self, col1, col2):
        """判断列名是否相似"""
        col1_lower = col1.lower()
        col2_lower = col2.lower()

        if col1_lower == col2_lower:
            return True

        col_variations = {
            'id': ['id', '_id', 'pk', 'primary_key'],
            'name': ['name', 'title', 'label', 'display_name'],
            'user': ['user', 'user_id', 'uid', 'owner', 'owner_id'],
            'customer': ['customer', 'customer_id', 'cust_id'],
            'product': ['product', 'product_id', 'item_id'],
            'order': ['order', 'order_id', 'order_number'],
            'date': ['date', 'time', 'datetime', 'created_at', 'updated_at']
        }

        for key, variations in col_variations.items():
            if col1_lower in variations and col2_lower in variations:
                return True

        return False

    def _calculate_data_overlap(self, cursor, table1, col1, table2, col2, sample_size=100):
        """计算两个列的数据重叠率"""
        try:
            cursor.execute(f"SELECT DISTINCT {col1} FROM {table1} LIMIT {sample_size}")
            values1 = set([str(row[0]) for row in cursor.fetchall() if row[0] is not None])

            cursor.execute(f"SELECT DISTINCT {col2} FROM {table2} LIMIT {sample_size}")
            values2 = set([str(row[0]) for row in cursor.fetchall() if row[0] is not None])

            if not values1 or not values2:
                return 0

            intersection = len(values1 & values2)
            smaller_set = min(len(values1), len(values2))

            return intersection / smaller_set if smaller_set > 0 else 0

        except Exception:
            return 0

    def analyze_relationships(self):
        """综合分析表关系"""
        foreign_keys = self.discover_foreign_keys()
        data_relationships = self.discover_data_relationships()

        analysis = {
            'explicit_relationships': foreign_keys,
            'implicit_relationships': data_relationships,
            'summary': {
                'total_explicit': sum(len(rels) for rels in foreign_keys.values()),
                'total_implicit': len(data_relationships)
            }
        }

        return analysis

    def format_relationship_analysis(self, analysis):
        """格式化关系分析结果"""
        output = []
        output.append("=" * 60)
        output.append("数据库表关系分析 / Database Table Relationships Analysis")
        output.append("=" * 60)

        output.append(f"\n📊 关系摘要 / Relationship Summary:")
        output.append(f"  - 显式外键关系 / Explicit Foreign Keys: {analysis['summary']['total_explicit']}")
        output.append(f"  - 隐式数据关联 / Implicit Data Relationships: {analysis['summary']['total_implicit']}")

        if analysis['explicit_relationships']:
            output.append(f"\n🔗 显式外键关系 / Explicit Foreign Keys:")
            for table, fks in analysis['explicit_relationships'].items():
                for fk in fks:
                    output.append(f"\n  {table}.{fk['from_column']} -> {fk['referenced_table']}.{fk['referenced_column']}")
                    output.append(f"    ON UPDATE: {fk['on_update']}, ON DELETE: {fk['on_delete']}")

        if analysis['implicit_relationships']:
            output.append(f"\n🔍 隐式数据关联 / Implicit Data Relationships:")
            for rel in analysis['implicit_relationships']:
                output.append(f"\n  {rel['table1']}.{rel['column1']} <-> {rel['table2']}.{rel['column2']}")
                output.append(f"    数据重叠率 / Overlap Ratio: {rel['overlap_ratio']:.2%}")
                output.append(f"    置信度 / Confidence: {rel['confidence']}")

        output.append("\n" + "=" * 60)
        return "\n".join(output)

    def suggest_join_queries(self, table1, table2=None):
        """生成建议的 JOIN 查询"""
        analysis = self.analyze_relationships()
        suggestions = []

        for rel in analysis['implicit_relationships']:
            if table1 and rel['table1'] != table1 and rel['table2'] != table1:
                continue
            if table2 and rel['table1'] != table2 and rel['table2'] != table2:
                continue

            join_query = f"SELECT * FROM {rel['table1']} JOIN {rel['table2']} ON {rel['table1']}.{rel['column1']} = {rel['table2']}.{rel['column2']}"
            suggestions.append({
                'relationship': f"{rel['table1']}.{rel['column1']} <-> {rel['table2']}.{rel['column2']}",
                'confidence': rel['confidence'],
                'query': join_query
            })

        return suggestions

    def interactive_mode(self):
        print("=== SQLite 数据库 AI 分析工具 ===")
        print(f"数据库: {self.db_path}")
        if self.ai_provider == 'ollama':
            print(f"AI 提供商: Ollama (llama2)")
            print(f"Ollama 地址: {self.ollama_url}")
        elif self.ai_provider == 'doubao':
            print(f"AI 提供商: 豆包 AI ({self.doubao_model if hasattr(self, 'doubao_model') else 'unknown'})")
        print("\n命令:")
        print("  analyze - 使用 AI 分析整个数据库")
        print("  ask <问题> - 向 AI 提问关于数据库的问题")
        print("  tables - 查看所有表")
        print("  schema <表名> - 查看表结构")
        print("  query <SQL语句> - 执行 SQL 查询")
        print("  relationships - 分析表之间的关联关系")
        print("  suggest-join <表1> [表2] - 生成 JOIN 查询建议")
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

            elif user_input.lower() == 'relationships':
                print("\n正在分析表关联关系，请稍候...")
                if self.ai_provider == 'doubao':
                    print("注意：表关联分析功能使用本地数据库操作，不调用 AI API")
                analysis = self.analyze_relationships()
                formatted = self.format_relationship_analysis(analysis)
                print(f"\n{formatted}")

            elif user_input.lower().startswith('suggest-join '):
                parts = user_input[13:].strip().split()
                table1 = parts[0] if len(parts) > 0 else None
                table2 = parts[1] if len(parts) > 1 else None

                if not table1:
                    print("\n错误: 请指定至少一个表名")
                    print("用法: suggest-join <表1> [表2]")
                else:
                    print(f"\n正在生成 JOIN 查询建议...")
                    suggestions = self.suggest_join_queries(table1, table2)

                    if suggestions:
                        print(f"\n找到 {len(suggestions)} 个关联建议:\n")
                        for i, sug in enumerate(suggestions, 1):
                            print(f"{i}. 关联 / Relationship: {sug['relationship']}")
                            print(f"   置信度 / Confidence: {sug['confidence']}")
                            print(f"   查询 / Query:")
                            print(f"   {sug['query']}\n")
                    else:
                        print("\n未找到相关的表关联")

            else:
                print("未知命令。输入 'help' 查看可用命令")

def load_config(config_file='config.ini'):
    """加载配置文件"""
    if not os.path.exists(config_file):
        return None

    config = configparser.ConfigParser()
    
    # 使用 UTF-8 编码读取配置文件，避免 Windows GBK 编码问题
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config.read_file(f)
    except UnicodeDecodeError:
        # 如果 UTF-8 失败，尝试使用系统默认编码
        with open(config_file, 'r', encoding=sys.getdefaultencoding()) as f:
            config.read_file(f)

        return {
        'provider': config.get('settings', 'provider', fallback='ollama'),
        'doubao': {
            'api_key': config.get('doubao', 'api_key', fallback=''),
            'model': config.get('doubao', 'model', fallback='doubao-seed-251228'),
            'endpoint': config.get('doubao', 'endpoint', fallback='https://ark.cn-beijing.volces.com/api/v3')
        },
        'ollama': {
            'url': config.get('ollama', 'url', fallback='http://localhost:11434'),
            'model': config.get('ollama', 'model', fallback='llama2')
        }
    }

def main():
    import argparse

    parser = argparse.ArgumentParser(description='SQLite 数据库 AI 分析工具')
    parser.add_argument('--provider', choices=['ollama', 'doubao'], default=None,
                       help='AI 提供商 (ollama 或 doubao)')
    parser.add_argument('--api-key', help='AI API 密钥')
    parser.add_argument('--model', help='AI 模型名称（豆包默认：doubao-seed-251228）')
    parser.add_argument('--endpoint', help='API 端点地址')
    parser.add_argument('--ollama-url', help='Ollama 服务地址')
    parser.add_argument('--config', default='config.ini', help='配置文件路径')
    parser.add_argument('--db', default='example.db', help='SQLite 数据库文件路径')

    args = parser.parse_args()

    # 加载配置文件
    config = load_config(args.config)

    # 确定使用的提供商
    provider = args.provider or (config['provider'] if config else 'ollama')

    # 构建 API 配置
    api_config = {}

    if provider == 'ollama':
        api_config = {
            'url': args.ollama_url or (config['ollama']['url'] if config else 'http://localhost:11434')
        }
    elif provider == 'doubao':
        api_key = args.api_key or (config['doubao']['api_key'] if config else None) or os.getenv('DOUBAO_API_KEY')

        if not api_key:
            print("错误: 使用豆包 AI 需要提供 API 密钥")
            print("\n请选择以下方式之一配置 API 密钥：\n")
            print("方式 1: 命令行参数")
            print("  python3 sqlite_analyzer.py --provider doubao --api-key your_api_key\n")
            print("方式 2: 环境变量")
            print("  export DOUBAO_API_KEY=your_api_key")
            print("  python3 sqlite_analyzer.py --provider doubao\n")
            print("方式 3: 配置文件")
            print("  cp config.ini.example config.ini")
            print("  编辑 config.ini，填写你的 API 密钥")
            print("  python3 sqlite_analyzer.py --provider doubao --config config.ini\n")
            return

        api_config = {
            'api_key': args.api_key or (config['doubao']['api_key'] if config else None) or os.getenv('DOUBAO_API_KEY'),
            'model': args.model or (config['doubao']['model'] if config else 'ep-20241225194800-r0q4p4i'),
            'endpoint': args.endpoint or (config['doubao']['endpoint'] if config else 'https://ark.cn-beijing.volces.com/api/v3')
        }

    print(f"使用 AI 提供商: {provider}")
    if provider == 'doubao':
        print(f"  模型: {api_config['model']}")

    analyzer = SQLiteAnalyzer(args.db, provider, api_config)
    analyzer.connect()

    try:
        analyzer.interactive_mode()
    finally:
        analyzer.disconnect()

if __name__ == '__main__':
    main()
