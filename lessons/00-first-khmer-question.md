# Lesson 00. Answer your first Khmer question

**Time.** About 30 minutes. Start with paper or a notes app. The code uses Python 3 and its standard library.

## 1. Trace one question on paper

Imagine a company stores definitions for people reading its reports. A colleague asks «តើចំណូលសុទ្ធមានន័យដូចម្តេច?» (“What does net revenue mean?”).

| Step | Your first system |
| --- | --- |
| Input | The original Khmer question and which release the user is reading |
| Match | Find the question in a tiny glossary |
| Check availability | The matched fact is usable only if its first release is at or before the selected release |
| Output | The fact ID and definition, or `UNKNOWN` when there is no visible match |

A **fact ID** is a stable label for what the question means, such as `net_revenue`. The answer is the definition displayed to the user. A **release** is a collection of glossary updates that become available together.

| Query | At release 1 | At release 2 |
| --- | --- | --- |
| «តើចំណូលសុទ្ធមានន័យដូចម្តេច?» | `net_revenue` | `net_revenue` |
| «តើស្តុកបម្រុងជាអ្វី?» | `UNKNOWN` | `safety_stock` |
| «តើកិច្ចប្រជុំនៅបន្ទប់ណា?» | `UNKNOWN` | `UNKNOWN` |

Safety stock is released later. The meeting room is outside this glossary. From the user's viewpoint, both are unsupported at release 1. In your evaluation you should distinguish the two cases.

## 2. Create your first Python file

Open a local folder such as `khmermind-practice` in VS Code. Use the editor to create `lesson00.py`. This is your practice folder.

In its terminal, use `python3 --version` on macOS or Linux to check that Python is available. Use `py --version` on Windows if your Python installation provides that command. Save the Python file with UTF-8 encoding so it preserves the Khmer strings.

## 3. Type and run the example

```python
GLOSSARY = {
    "តើចំណូលសរុបមានន័យដូចម្តេច": {
        "fact_id": "gross_revenue",
        "release": 1,
        "answer": "ចំណូលសរុបគឺតម្លៃលក់សរុបមុនដកការបញ្ចុះតម្លៃ និងទំនិញបង្វិល។",
    },
    "តើចំណូលសុទ្ធមានន័យដូចម្តេច": {
        "fact_id": "net_revenue",
        "release": 1,
        "answer": "ចំណូលសុទ្ធគឺចំណូលសរុបក្រោយដកការបញ្ចុះតម្លៃ និងទំនិញបង្វិល។",
    },
    "តើអតិថិជនទិញម្តងទៀតមានន័យដូចម្តេច": {
        "fact_id": "repeat_customer",
        "release": 2,
        "answer": "អតិថិជនទិញម្តងទៀតគឺអ្នកដែលបានទិញយ៉ាងតិចពីរដង។",
    },
    "តើស្តុកបម្រុងជាអ្វី": {
        "fact_id": "safety_stock",
        "release": 2,
        "answer": "ស្តុកបម្រុងគឺទំនិញបន្ថែមដែលទុកសម្រាប់ការពារការខ្វះស្តុក។",
    },
}


def clean_question(question):
    return question.strip().rstrip("?។").strip()


def lookup(question, release):
    key = clean_question(question)
    record = GLOSSARY.get(key)
    if record is None or record["release"] > release:
        return None
    return record


def fact_id(record):
    if record is None:
        return "UNKNOWN"
    return record["fact_id"]


if __name__ == "__main__":
    for release in (1, 2):
        print(f"Release {release}")
        for question in (
            "តើចំណូលសុទ្ធមានន័យដូចម្តេច?",
            "តើស្តុកបម្រុងជាអ្វី?",
            "តើកិច្ចប្រជុំនៅបន្ទប់ណា?",
        ):
            result = lookup(question, release)
            print(f"  {question} -> {fact_id(result)}")
```

From the terminal in the same folder, run `python3 lesson00.py`, or `py lesson00.py` on Windows if you used `py` above. Compare the last column with the table in section 1.

## 4. Explain what Python did

| Code | What it does |
| --- | --- |
| `GLOSSARY = {...}` | Stores matching questions and their records in a dictionary. |
| `def clean_question(question)` | Defines a reusable operation on a string. `strip()` removes surrounding whitespace and `rstrip("?។")` removes those ending punctuation characters. |
| `GLOSSARY.get(key)` | Looks up the cleaned question. It returns `None` if the key is missing. |
| `record["release"] > release` | Stops a matching future fact from appearing before its release. |
| `for release in (1, 2)` | Runs the same queries under two releases. |
| `if __name__ == "__main__":` | Runs the example when this file is started directly. The next practice lesson can import the data without printing the example. |

Try `តើអ្វីទៅជាចំណូលសុទ្ធ?` in release 1. It is another way to ask about net revenue, but the exact wording is absent from the dictionary, so it returns `UNKNOWN`. That limitation gives you a clear problem to solve when you study character features and retrieval.

## 5. Do the first checkpoint

1. Add a fifth fictional fact to release 3. Write its ID, Khmer definition, and one matching question.
2. Run its question in releases 2 and 3. Record the expected ID before looking at the actual output.
3. Ask about the new fact using noticeably different words. Explain why it currently does or does not match.
4. In your own words, explain what the code actually checks when it returns `UNKNOWN`.

You have completed 0–10 when you can trace each output and reproduce your fifth-fact check. Keep a copy of the original sample if you want to reproduce the later practice results exactly.

Continue to [Lesson 01 · Define the problem and design the data](01-problem-and-data.md).
