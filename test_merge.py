import requests


files = [
    (
        "files",
        (
            "first.pdf",
            open("first.pdf", "rb"),
            "application/pdf"
        )
    ),
    (
        "files",
        (
            "second.pdf",
            open("second.pdf", "rb"),
            "application/pdf"
        )
    )
]


response = requests.post(
    "http://127.0.0.1:8000/api/merge-pdfs",
    files=files
)


print("Status:", response.status_code)

if response.status_code == 200:

    with open("merged_test.pdf", "wb") as f:
        f.write(response.content)

    print("PDF merged successfully!")

else:
    print(response.text)