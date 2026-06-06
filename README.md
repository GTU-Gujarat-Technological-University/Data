# GTU Student Lookup

A local web tool to fetch GTU student details from official portals using an enrollment number.

---

## Setup

**Requirements:** Python 3.x

**Install dependencies:**
```bash
pip install requests flask lxml
```

**Run the server:**
```bash
python server.py
```

Then open `http://127.0.0.1:5000` in your browser.

---

## How It Works

Enter a student enrollment number, select a source portal, and hit **Search**. The app scrapes the selected GTU portal and returns:

- Student name
- College / department info
- Photo (fetched from AWS S3)
- Raw portal HTML (rendered in an iframe)

### Source Portals

| Key        | Portal URL                    | Returns                         |
|------------|-------------------------------|---------------------------------|
| `100`      | 100points.gtu.ac.in           | Email, college code, branch     |
| `de`       | de.gtu.ac.in                  | Year, college, department       |
| `pmms`     | pmms.gtu.ac.in                | Year, college, department       |
| `billdesk` | billdesk.gtu.ac.in            | Name only (payment records)     |

### API Endpoints

| Endpoint                        | Method     | Description                  |
|---------------------------------|------------|------------------------------|
| `/`                             | GET        | Main UI                      |
| `/<enrollment>/?source=<key>`   | POST       | Fetch student details (JSON) |
| `/<enrollment>/media/`          | GET        | Fetch student photo          |

---

## ⚠️ Data Privacy & Security Concerns

This tool **scrapes personally identifiable information (PII)** from public-facing GTU portals. Before using or deploying it, consider the following:

### What Data Is Exposed

The GTU portals return student data — name, email, college, department — in response to any enrollment number query **without authentication**. This is a data exposure issue on GTU's end.

Specifically:
- **Student names and emails** are returned by the `100points` portal
- **College and department info** is returned by DE and PMMS portals
- **Student photos** are fetched from a public AWS S3 bucket using only the enrollment number as the key

### How This Could Be Misused

- Anyone with a list of enrollment numbers could bulk-scrape student records
- The S3 photo bucket (`studentphoto.s3.us-west-2.amazonaws.com`) has no access control — photos are publicly accessible by guessing enrollment numbers

### How to Use This Responsibly

- **Do not deploy this publicly** — keep it running locally only
- **Do not store or share** the fetched student data
- **Do not automate bulk lookups** — only query for your own enrollment number or with explicit consent
- This tool is intended for **personal/educational use only**

### If You Are a GTU Administrator

The following should be addressed on the portal side:

1. **Add authentication** before returning student records (even basic session checks)
2. **Restrict the S3 bucket** — student photos should not be publicly accessible by enrollment number
3. **Rate-limit** the registration endpoints to prevent bulk scraping
4. **Audit what fields** are returned in unauthenticated responses and remove sensitive ones (email especially)

---

## Project Structure

```
.
├── server.py        # Flask backend — scraping logic & API routes
└── templates/
    └── index.html   # Frontend UI
```

---

## Disclaimer

This project is for **educational and personal use only**. The author does not condone scraping or misusing student data. Always comply with GTU's terms of service and applicable data protection laws.
