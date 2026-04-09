import os
import requests
import csv
import urllib.request

# 환경 변수
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_PAGE_ID = os.environ["NOTION_PAGE_ID"]
SHEET_ID = os.environ["SHEET_ID"]

# 구글 시트 CSV로 읽기 (공개 시트)
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def get_sheet_data():
    response = requests.get(SHEET_URL)
    response.encoding = "utf-8"
    lines = response.text.strip().split("\n")
    rows = [line.split(",") for line in lines]
    return rows

def build_notion_table(rows):
    """시트 데이터를 노션 테이블 블록으로 변환"""
    children = []
    for i, row in enumerate(rows):
        cells = []
        for cell in row:
            cells.append([{"type": "text", "text": {"content": cell.strip()}}])
        children.append({
            "type": "table_row",
            "table_row": {"cells": cells}
        })
    
    table_block = {
        "type": "table",
        "table": {
            "table_width": len(rows[0]) if rows else 1,
            "has_column_header": True,
            "has_row_header": False,
            "children": children
        }
    }
    return table_block

def clear_notion_page():
    """기존 노션 페이지 블록 전부 삭제"""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28"
    }
    url = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children"
    res = requests.get(url, headers=headers)
    blocks = res.json().get("results", [])
    
    for block in blocks:
        del_url = f"https://api.notion.com/v1/blocks/{block['id']}"
        requests.delete(del_url, headers=headers)

def update_notion_page(table_block):
    """노션 페이지에 테이블 추가"""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    url = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children"
    body = {"children": [table_block]}
    res = requests.patch(url, headers=headers, json=body)
    print("노션 업데이트 결과:", res.status_code)
    print(res.json())

if __name__ == "__main__":
    print("시트 데이터 읽는 중...")
    rows = get_sheet_data()
    print(f"{len(rows)}행 읽음")
    
    print("노션 페이지 초기화 중...")
    clear_notion_page()
    
    print("노션 페이지 업데이트 중...")
    table = build_notion_table(rows)
    update_notion_page(table)
    print("완료!")
