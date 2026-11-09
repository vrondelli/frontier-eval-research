"""Feature-free majority classifier. Training uses only the target column."""
import csv
import sys


def fit(rows):
    labels = [int(row["escalated"]) for row in rows]
    return int(sum(labels) * 2 >= len(labels)) if labels else 0


def main():
    with open("train.csv", newline="", encoding="utf-8-sig") as stream:
        prediction = fit(csv.DictReader(stream))
    with open(sys.argv[1], newline="", encoding="utf-8-sig") as source:
        rows = list(csv.DictReader(source))
    with open(sys.argv[2], "w", newline="", encoding="utf-8") as destination:
        writer = csv.writer(destination)
        writer.writerow(["id", "prediction"])
        writer.writerows((row["id"], prediction) for row in rows)


if __name__ == "__main__":
    main()
