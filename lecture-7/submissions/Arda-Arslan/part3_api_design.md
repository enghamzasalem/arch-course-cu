# Task 3.1 API Design

## 1. Synchronous Endpoint

**POST /api/v1/pipeline/run**

Processes the document immediately and returns the result.

### Request
- file (document)
- options (optional processing parameters)

### Response
- validation result  
- extracted data  
- classification result  
- storage confirmation  

---

## 2. Asynchronous Endpoint

**POST /api/v1/pipeline/jobs**

Submits a document for background processing.

### Request
- file (document)
- options (optional processing parameters)
- callback_url (optional)

### Response
- job_id  
- status ("accepted")

---

## 3. Job Status Endpoint

**GET /api/v1/pipeline/jobs/{job_id}**

Returns the status of a submitted job.

### Response
- job_id  
- status (pending / processing / completed / failed)  
- result (only if completed)  

---

## 4. Optional Callback (Webhook)

If a `callback_url` is provided, a notification is sent when processing is completed.

The Notification Service sends this callback.

---

## 5. Synchronous Flow Mapping

1. The client sends a request to the Pipeline API.  
2. The Pipeline API calls the Validation Service.  
3. If the document is valid, the Pipeline API calls the Extraction Service.  
4. The Pipeline API then calls the Classification Service.  
5. The Pipeline API calls the Storage Service.  
6. The final result is returned to the client.  

---

## 6. Asynchronous Flow Mapping

1. The client sends a request to the Pipeline API.  
2. The Pipeline API validates the document.  
3. If valid, the Pipeline API creates a job and returns a job ID.  
4. The job is sent to a message queue for background processing.  
5. The pipeline continues asynchronously through Extraction, Classification, and Storage services.  
6. After processing is completed, the Notification Service sends a notification or callback to the client.  