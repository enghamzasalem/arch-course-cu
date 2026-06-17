# Part 2.1 – API Design for pdf-parse HTTP/REST Service

## Overview

This document proposes a **REST API design** that exposes the functionality of the **pdf-parse library** as a web service. The goal is to allow clients such as web applications, backend services, or CLI tools to send PDF files and retrieve extracted content via HTTP requests.

The API maps library operations such as **text extraction, metadata extraction, image extraction, table detection, and page rendering** into clear and reusable REST endpoints.

The API follows standard REST principles:

- Resource-based URLs
- JSON request and response formats
- Consistent error handling
- Versioned endpoints (`/api/v1/`)

---

# Base URL
/api/v1

## Example full endpoint:
POST /api/v1/extract/text


---

# Input Methods

Clients can provide PDFs in three ways.

| Input Type | Description |
|------|------|
| File Upload | Multipart upload of a PDF file |
| URL | API downloads the PDF from a remote URL |
| Base64 | PDF encoded in base64 within JSON |

### Example: URL Input

json
{
  "url": "https://example.com/document.pdf"
}

1. Example: Base64 Input

{
  "base64": "JVBERi0xLjQKJ..."
}

2. Example: Multipart Upload

POST /api/v1/extract/text
Content-Type: multipart/form-data

file: document.pdf

 ---

# API Endpoints

## 1. Extract Text

### Endpoint
POST /api/v1/extract/text

### Description

Extracts all text from a PDF document.

Request Example
{
  "url": "https://example.com/sample.pdf"
}

Response Example
{
  "text": "Example document text...",
  "pages": 5
}

## 2. Extract Metadata

### Endpoint
POST /api/v1/extract/info

### Description

Extracts PDF metadata such as title, author, and creation date.

Request Example
{
  "url": "https://example.com/sample.pdf"
}

Response Example
{
  "title": "Sample PDF",
  "author": "John Doe",
  "creator": "Adobe Acrobat",
  "pages": 5,
  "creationDate": "2023-06-12"
}

## 3. Extract Embedded Images

### Endpoint
POST /api/v1/extract/images

### Description

Extracts embedded images from the PDF.

Request Example
{
  "url": "https://example.com/sample.pdf"
}

Response Example
{
  "images": [
    {
      "page": 1,
      "imageBase64": "iVBORw0KGgoAAAANSUhEUg..."
    },
    {
      "page": 2,
      "imageBase64": "iVBORw0KGgoAAAANSUhEUg..."
    }
  ]
}

## 4. Extract Tables

### Endpoint
POST /api/v1/extract/tables

### Description

Detects and extracts tabular data from the document.

Request Example
{
  "url": "https://example.com/sample.pdf"
}

Response Example
{
  "tables": [
    {
      "page": 2,
      "rows": [
        ["Name", "Age"],
        ["Alice", "24"],
        ["Bob", "31"]
      ]
    }
  ]
}

## 5. Generate Page Screenshot

### Endpoint
POST /api/v1/screenshot

### Description

Renders one or more pages as PNG images.

Request Example
{
  "url": "https://example.com/sample.pdf",
  "pages": [1,2],
  "scale": 2
}

Response Example
{
  "screenshots": [
    {
      "page": 1,
      "imageBase64": "iVBORw0KGgoAAAANS..."
    }
  ]
}

# Error Handling

The API returns consistent HTTP status codes.

| Status Code | Description                        |
| ----------- | ---------------------------------- |
| 400         | Invalid request or malformed input |
| 413         | File too large                     |
| 422         | PDF parsing failed                 |
| 500         | Internal server error              |

Example Error Response

{
  "error": {
    "code": 422,
    "message": "Unable to parse PDF file"
  }
}

# Design Decisions

## 1. Synchronous vs Asynchronous Processing

Most PDF operations are relatively fast for small documents. Therefore, the API supports synchronous processing for typical files.

However, large PDFs may require asynchronous processing in future versions.

Example future design:

POST /api/v1/jobs
GET /api/v1/jobs/{id}

This would allow long-running extraction tasks.

## 2. File Size Limits
To prevent abuse and excessive resource consumption:

| Limit             | Value      |
| ----------------- | ---------- |
| Maximum file size | 25 MB      |
| Maximum pages     | 500        |
| Timeout           | 30 seconds |

Requests exceeding these limits return:
413 Payload Too Large

## 3. Timeout Handling

Large PDF parsing operations may take longer than typical HTTP requests.

Recommended timeout configuration:
30 seconds

If exceeded:
504 Gateway Timeout

# Example Full Workflow

Example request for text extraction:

POST /api/v1/extract/text

Body:

{
  "url": "https://example.com/report.pdf"
}

Response:

{
  "text": "Annual report text...",
  "pages": 12
}