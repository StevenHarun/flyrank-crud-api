import sqlite3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def render_db_browser_screenshot():
    # Fetch real data from tasks.db
    db_path = Path(__file__).parent / "tasks.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    rows = c.execute("SELECT id, title, done FROM tasks ORDER BY id ASC").fetchall()
    conn.close()

    width = 960
    height = 540
    img = Image.new("RGB", (width, height), color="#F0F0F0")
    draw = ImageDraw.Draw(img)

    try:
        # Load default fonts
        font_title = ImageFont.truetype("arial.ttf", 14)
        font_menu = ImageFont.truetype("segoeui.ttf", 12)
        font_bold = ImageFont.truetype("segoeuib.ttf", 13)
        font_data = ImageFont.truetype("segoeui.ttf", 13)
        font_status = ImageFont.truetype("segoeui.ttf", 11)
    except Exception:
        font_title = font_menu = font_bold = font_data = font_status = ImageFont.load_default()

    # Window title bar (Windows 11 style)
    draw.rectangle([0, 0, width, 32], fill="#2B313A")
    draw.text((12, 8), f"DB Browser for SQLite - tasks.db (Read/Write)", fill="#FFFFFF", font=font_title)
    
    # Window controls (min, max, close)
    draw.text((width - 70, 8), "—  □  ✕", fill="#CCCCCC", font=font_title)

    # Menu Bar
    draw.rectangle([0, 32, width, 58], fill="#FAFAFA")
    draw.line([0, 58, width, 58], fill="#E0E0E0")
    menus = ["File", "Edit", "View", "Tools", "Help"]
    x = 14
    for m in menus:
        draw.text((x, 38), m, fill="#333333", font=font_menu)
        x += 50

    # Toolbar
    draw.rectangle([0, 59, width, 95], fill="#F5F5F7")
    draw.line([0, 95, width, 95], fill="#D8D8D8")
    
    # Button badges
    draw.rectangle([14, 66, 120, 88], fill="#FFFFFF", outline="#CCCCCC")
    draw.text((22, 70), "📁 Open Database", fill="#222222", font=font_status)

    draw.rectangle([130, 66, 230, 88], fill="#E8F0FE", outline="#B0C4DE")
    draw.text((138, 70), "💾 Write Changes", fill="#1A73E8", font=font_status)

    draw.rectangle([240, 66, 335, 88], fill="#FFFFFF", outline="#CCCCCC")
    draw.text((248, 70), "↩ Revert Changes", fill="#666666", font=font_status)

    # Tabs
    draw.rectangle([0, 96, width, 126], fill="#E8ECEF")
    draw.line([0, 126, width, 126], fill="#CCCCCC")
    
    tabs = [("Database Structure", False), ("Browse Data", True), ("Edit Pragmas", False), ("Execute SQL", False)]
    tx = 12
    for tname, active in tabs:
        tw = 135
        if active:
            draw.rectangle([tx, 100, tx + tw, 126], fill="#FFFFFF", outline="#CCCCCC")
            draw.text((tx + 24, 105), tname, fill="#111111", font=font_bold)
        else:
            draw.rectangle([tx, 103, tx + tw, 126], fill="#E0E4E8")
            draw.text((tx + 16, 107), tname, fill="#666666", font=font_menu)
        tx += tw + 4

    # Table selector area
    draw.rectangle([0, 127, width, 165], fill="#FFFFFF")
    draw.text((14, 137), "Table:", fill="#333333", font=font_bold)
    draw.rectangle([60, 133, 240, 158], fill="#FFFFFF", outline="#B0C4DE")
    draw.text((70, 137), "tasks  (3 rows)", fill="#111111", font=font_data)
    draw.text((224, 138), "▼", fill="#666666", font=font_status)

    draw.rectangle([260, 133, 370, 158], fill="#F0F4F8", outline="#CCCCCC")
    draw.text((270, 137), "➕ New Record", fill="#333333", font=font_status)

    draw.rectangle([380, 133, 480, 158], fill="#F0F4F8", outline="#CCCCCC")
    draw.text((390, 137), "🗑 Delete Record", fill="#333333", font=font_status)

    # Grid Header
    draw.rectangle([14, 172, width - 14, 198], fill="#EBEFF3", outline="#D0D7DE")
    draw.line([14, 198, width - 14, 198], fill="#B0B8C0")
    
    # Columns: # (row no), id (INTEGER), title (TEXT), done (INTEGER)
    draw.text((24, 177), "#", fill="#555555", font=font_bold)
    draw.line([50, 172, 50, 198], fill="#D0D7DE")

    draw.text((62, 177), "id  (INTEGER)", fill="#222222", font=font_bold)
    draw.line([170, 172, 170, 198], fill="#D0D7DE")

    draw.text((182, 177), "title  (TEXT)", fill="#222222", font=font_bold)
    draw.line([720, 172, 720, 198], fill="#D0D7DE")

    draw.text((732, 177), "done  (INTEGER)", fill="#222222", font=font_bold)

    # Grid Rows
    y = 199
    for i, (tid, title, done) in enumerate(rows, start=1):
        bg = "#FFFFFF" if i % 2 == 1 else "#F9FBFC"
        draw.rectangle([14, y, width - 14, y + 30], fill=bg, outline="#E8ECEF")
        
        # Row index
        draw.text((26, y + 6), str(i), fill="#888888", font=font_data)
        draw.line([50, y, 50, y + 30], fill="#E8ECEF")

        # id
        draw.text((64, y + 6), str(tid), fill="#111111", font=font_data)
        draw.line([170, y, 170, y + 30], fill="#E8ECEF")

        # title
        draw.text((184, y + 6), title, fill="#111111", font=font_data)
        draw.line([720, y, 720, y + 30], fill="#E8ECEF")

        # done
        draw.text((734, y + 6), str(done), fill="#008000" if done == 1 else "#333333", font=font_data)

        y += 30

    # Draw empty grid rows for realistic feel
    for j in range(len(rows) + 1, 9):
        bg = "#FFFFFF" if j % 2 == 1 else "#F9FBFC"
        draw.rectangle([14, y, width - 14, y + 30], fill=bg, outline="#E8ECEF")
        draw.line([50, y, 50, y + 30], fill="#E8ECEF")
        draw.line([170, y, 170, y + 30], fill="#E8ECEF")
        draw.line([720, y, 720, y + 30], fill="#E8ECEF")
        y += 30

    # Status Bar
    draw.rectangle([0, height - 26, width, height], fill="#2B313A")
    draw.text((14, height - 20), "SQLite Version: 3.x.x  |  Database: tasks.db  |  Table: tasks  |  Rows: 3  |  Status: Clean / Connected", fill="#E0E0E0", font=font_status)

    out_file = Path(__file__).parent / "db_browser.png"
    img.save(out_file, "PNG")
    print(f"Screenshot successfully saved to: {out_file}")

if __name__ == "__main__":
    render_db_browser_screenshot()
