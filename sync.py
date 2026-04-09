import os
import requests
import csv
import io

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_PAGE_ID = os.environ["NOTION_PAGE_ID"]
SHEET_ID = os.environ["SHEET_ID"]
SHEET_GID = "1246889171"

SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={SHEET_GID}"

def get_sheet_data():
    response = requests.get(SHEET_URL, allow_redirects=True)
    content = response.content.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    print(f"첫번째 행 샘플: {rows[0] if rows else '없음'}")
    return rows

def build_html(rows):
    max_cols = max(len(row) for row in rows) if rows else 0
    for row in rows:
        while len(row) < max_cols:
            row.append("")

    def get_cell_style(val):
        val = val.strip()
        if val == "Cabinet":
            return "cabinet"
        elif val in ["Call Room", "창고", "알림룸", "탕비실", "화장실", "회의실"]:
            return "room"
        elif val == "":
            return "empty"
        else:
            return "person"

    table_html = ""
    for row in rows:
        table_html += "<tr>"
        for cell in row:
            val = cell.strip()
            style = get_cell_style(val)
            if style == "cabinet":
                table_html += f'<td class="cell cabinet">{val}</td>'
            elif style == "room":
                table_html += f'<td class="cell room">{val}</td>'
            elif style == "empty":
                table_html += f'<td class="cell empty"></td>'
            else:
                table_html += f'<td class="cell person">{val}</td>'
        table_html += "</tr>"

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>강남 캠퍼스 자리배치도</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
    background: #f0f2f5;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    min-height: 100vh;
    padding: 40px 20px;
  }}
  .container {{
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.10);
    padding: 36px 40px;
    max-width: 1100px;
    width: 100%;
  }}
  h1 {{
    font-size: 22px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
  }}
  .subtitle {{
    font-size: 13px;
    color: #888;
    margin-bottom: 28px;
  }}
  .legend {{
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #555;
  }}
  .legend-dot {{
    width: 12px;
    height: 12px;
    border-radius: 3px;
  }}
  table {{
    border-collapse: separate;
    border-spacing: 5px;
    width: 100%;
  }}
  .cell {{
    padding: 10px 8px;
    text-align: center;
    font-size: 13px;
    font-weight: 500;
    border-radius: 8px;
    min-width: 60px;
    min-height: 40px;
    transition: transform 0.15s, box-shadow 0.15s;
  }}
  .person {{
    background: #e8f4fd;
    color: #1a6fa8;
    border: 1.5px solid #b3d9f5;
    cursor: default;
  }}
  .person:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(26,111,168,0.15);
    background: #d0eaf9;
  }}
  .room {{
    background: #fff3e0;
    color: #e65100;
    border: 1.5px solid #ffcc80;
    font-weight: 700;
    font-size: 12px;
  }}
  .cabinet {{
    background: #f3e5f5;
    color: #6a1b9a;
    border: 1.5px solid #ce93d8;
    font-weight: 600;
    font-size: 12px;
    writing-mode: vertical-rl;
  }}
  .empty {{
    background: transparent;
    border: none;
  }}
</style>
</head>
<body>
<div class="container">
  <h1>🏢 강남 캠퍼스 자리배치도</h1>
  <p class="subtitle">구글 시트와 자동 동기화됩니다</p>
  <div class="legend">
    <div class="legend-item"><div class="legend-dot" style="background:#e8f4fd;border:1.5px solid #b3d9f5;"></div> 직원</div>
    <div class="legend-item"><div class="legend-dot" style="background:#fff3e0;border:1.5px solid #ffcc80;"></div> 공간</div>
    <div class="legend-item"><div class="legend-dot" style="background:#f3e5f5;border:1.5px solid #ce93d8;"></div> Cabinet</div>
  </div>
  <table>
    {table_html}
  </table>
</div>
</body>
</html>"""
    return html

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

def update_notion_with_embed(github_pages_url):
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    url = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children"
    body = {
        "children": [
            {
                "type": "embed",
                "embed": {
                    "url": github_pages_url
                }
            }
        ]
    }
    res = requests.patch(url, headers=headers, json=body)
    print("노션 업데이트 결과:", res.status_code)

if __name__ == "__main__":
    print("시트 데이터 읽는 중...")
    rows = get_sheet_data()
    print(f"{len(rows)}행 읽음")

    print("HTML 생성 중...")
    html = build_html(rows)

    print("index.html 저장 중...")
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html 저장 완료!")

    print("노션 페이지 업데이트 중...")
    clear_notion_page()

    github_user = os.environ.get("GITHUB_REPOSITORY", "").split("/")[0]
    github_repo = os.environ.get("GITHUB_REPOSITORY", "").split("/")[-1]
    pages_url = f"https://{github_user}.github.io/{github_repo}/"

    update_notion_with_embed(pages_url)
    print(f"완료! 페이지 URL: {pages_url}")
