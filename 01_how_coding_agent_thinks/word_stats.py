"""Статистика слів і речень у текстовому файлі UTF-8."""

import argparse
from collections import Counter
from pathlib import Path
import re


# Апострофи й дефіси всередині слова не розділяють його на частини.
WORD_PATTERN = re.compile(r"[^\W\d_]+(?:['’ʼ-][^\W\d_]+)*")


def word_stats(path):
    text = path.read_text(encoding="utf-8-sig")
    words = WORD_PATTERN.findall(text.casefold())
    # Речення закінчується крапкою, знаком питання або знаком оклику.
    # Непорожній фрагмент наприкінці без такого знака теж є реченням.
    sentences = [
        part for part in re.split(r"[.!?…]+", text)
        if WORD_PATTERN.search(part)
    ]
    average = len(words) / len(sentences) if sentences else 0.0
    return len(words), Counter(words).most_common(10), average


def print_comparison(paths, stats):
    rows = [["Показник", str(paths[0]), str(paths[1])]]
    rows.append(["Кількість слів", str(stats[0][0]), str(stats[1][0])])
    rows.append([
        "Середня довжина речення у словах",
        f"{stats[0][2]:.2f}", f"{stats[1][2]:.2f}",
    ])
    for rank in range(10):
        row = [f"Найчастотніше слово №{rank + 1}"]
        for _, top_words, _ in stats:
            if rank < len(top_words):
                word, count = top_words[rank]
                row.append(f"{word}: {count}")
            else:
                row.append("—")
        rows.append(row)
    widths = [max(len(row[i]) for row in rows) for i in range(3)]
    for index, row in enumerate(rows):
        print(" | ".join(value.ljust(width) for value, width in zip(row, widths)))
        if index == 0:
            print("-+-".join("-" * width for width in widths))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", type=Path, nargs="+", help="Один або два файли UTF-8")
    args = parser.parse_args()
    if len(args.paths) > 2:
        parser.error("Вкажіть один або два файли")
    stats = []
    for path in args.paths:
        try:
            stats.append(word_stats(path))
        except (OSError, UnicodeError) as error:
            parser.error(f"{path}: {error}")
    if len(stats) == 2:
        print_comparison(args.paths, stats)
        return

    count, top_words, average = stats[0]
    print(f"Кількість слів: {count}")
    print("Десять найчастотніших слів:")
    for word, count in top_words:
        print(f"  {word}: {count}")
    print(f"Середня довжина речення у словах: {average:.2f}")


if __name__ == "__main__":
    main()
