"""导入词库数据到数据库 - 示例脚本
实际使用时需要准备完整的 CET-4/CET-6 词库 CSV 文件

CSV 格式: word, meaning, phonetic, example, level
示例:
abandon,放弃,/əˈbændən/,Don't abandon your dreams.,cet4
"""
import csv
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal, Base
from app.models.word import Word


def import_words(csv_path: str, level: str):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    count = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            word = Word(
                word=row[0].strip(),
                meaning=row[1].strip(),
                phonetic=row[2].strip() if len(row) > 2 else "",
                example=row[3].strip() if len(row) > 3 else "",
                level=level,
            )
            db.add(word)
            count += 1
            if count % 500 == 0:
                db.commit()
                print(f"已导入 {count} 个单词...")

    db.commit()
    print(f"完成！共导入 {count} 个 {level} 单词")
    db.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python import_words.py <csv文件路径> <level>")
        print("示例: python import_words.py cet4_words.csv cet4")
        sys.exit(1)

    csv_path = sys.argv[1]
    level = sys.argv[2]

    if level not in ("cet4", "cet6"):
        print("level 必须是 cet4 或 cet6")
        sys.exit(1)

    import_words(csv_path, level)
