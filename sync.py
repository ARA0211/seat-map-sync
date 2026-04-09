import os
import requests

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_PAGE_ID = os.environ["NOTION_PAGE_ID"]
SHEET_ID = os.environ["SHEET_ID"]

SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1246889171"

def get_sheet_data():
    response = requests.get(SHEET_URL)
    response.encoding = "utf-8"
    lines = response.text.strip().split("\n")
    rows = [line.split(",") for line in lines]
    # 모든 행의 셀 수를 최대값으로 맞추기
    max_cols = max(len(row) for row in rows)
    for row in rows:
        while len(row) < max_cols:
            row.append("")
    return rows, max_cols

def build_notion_table(rows, max_cols):
    children = []
    for row in rows:
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
            "table_width": max_cols,
            "has_column_header": True,
            "has_row_header": False,
            "children": children
        }
    }
    return table_block

def clear_notion_page():
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
    rows, max_cols = get_sheet_data()
    print(f"{len(rows)}행 읽음")
    print("노션 페이지 초기화 중...")
    clear_notion_page()
    print("노션 페이지 업데이트 중...")
    table = build_notion_table(rows, max_cols)
    update_notion_page(table)
    print("완료!")
