#!/usr/bin/env python3

import sqlite3
import requests
import json
import sys

def test_ollama_connection(url='http://localhost:11434'):
    try:
        response = requests.get(f'{url}/api/version', timeout=5)
        if response.status_code == 200:
            version = response.json()
            print(f"Ollama 服务运行正常，版本: {version.get('version', 'unknown')}")
            return True
        else:
            print(f"Ollama 服务返回错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"无法连接到 Ollama 服务: {e}")
        return False

def test_database(db_path='example.db'):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print(f"\n数据库 '{db_path}' 连接成功")
        print(f"表列表: {[t[0] for t in tables]}")

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  {table[0]}: {count} 行")

        conn.close()
        return True
    except Exception as e:
        print(f"数据库错误: {e}")
        return False

def test_llama2(url='http://localhost:11434'):
    try:
        print("\n测试 llama2 模型（这可能需要几分钟）...")
        response = requests.post(
            f'{url}/api/generate',
            json={
                'model': 'llama2',
                'prompt': '用一句话介绍你自己',
                'stream': False
            },
            timeout=300
        )

        if response.status_code == 200:
            result = response.json()
            print(f"llama2 响应: {result.get('response', '无响应')}")
            return True
        else:
            print(f"llama2 模型请求失败: {response.status_code}")
            print(f"详细信息: {response.text}")
            return False
    except Exception as e:
        print(f"llama2 测试失败: {e}")
        return False

def main():
    print("=== SQLite + Ollama 测试程序 ===\n")

    all_pass = True

    print("1. 测试 Ollama 服务...")
    if not test_ollama_connection():
        print("错误: Ollama 服务未运行")
        all_pass = False

    print("\n2. 测试 SQLite 数据库...")
    if not test_database():
        print("错误: 数据库无法访问")
        all_pass = False

    if all_pass:
        print("\n3. 测试 llama2 模型...")
        test_llama2()

    print("\n" + "="*40)
    if all_pass:
        print("所有测试完成！可以运行 sqlite_analyzer.py 开始使用")
    else:
        print("部分测试失败，请检查服务状态")

if __name__ == '__main__':
    main()
