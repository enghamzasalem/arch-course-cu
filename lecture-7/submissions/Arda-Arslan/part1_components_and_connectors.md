# Task 1.1 Component Decomposition

## Components

### 1. Pipeline API
Responsibility: Entry point for clients to submit documents and retrieve results  
Inputs: HTTP requests (file upload, job requests, status queries)  
Outputs: HTTP responses (validation result, processing result, job ID)  
Sync/Async: Both. Sync in direct processing flow, async in job submission flow

### 2. Validation Service
Responsibility: Validate uploaded documents (format, size, basic checks)  
Inputs: Document file and metadata from Pipeline API  
Outputs: Validation result (valid or invalid with reason)  
Sync/Async: Sync from caller's perspective because the caller waits for the validation result

### 3. Extraction Service
Responsibility: Extract text or content from documents  
Inputs: Valid document from Pipeline API in sync flow, or job message in async flow  
Outputs: Extracted text data  
Sync/Async: Sync in direct processing flow, async from caller's perspective in background flow

### 4. Classification Service
Responsibility: Classify extracted content into categories  
Inputs: Extracted text from Extraction Service in sync flow, or queue message in async flow  
Outputs: Classification result (category label)  
Sync/Async: Sync in direct processing flow, async from caller's perspective in background flow

### 5. Storage Service
Responsibility: Store processed documents and results  
Inputs: Document and classification result  
Outputs: Storage confirmation (ID or success status)  
Sync/Async: Sync in direct processing flow, async from caller's perspective in background flow

### 6. Notification Service
Responsibility: Notify users when asynchronous processing is completed  
Inputs: Completion event or message with job result  
Outputs: Notification (email or callback)  
Sync/Async: Async from caller's perspective because it happens after background processing

## Connectors

### 1. Client to Pipeline API
Type: REST  
Sync/Async: Sync  
Protocol or Format: HTTP with JSON or multipart file upload  

### 2. Pipeline API to Validation Service
Type: Direct Call  
Sync/Async: Sync  
Protocol or Format: Internal method call with document metadata and file reference  

### 3. Pipeline API to Extraction Service
Type: Direct Call  
Sync/Async: Sync  
Protocol or Format: Internal method call with validated document  

### 4. Extraction Service to Classification Service
Type: Direct Call  
Sync/Async: Sync  
Protocol or Format: Internal method call with extracted text  

### 5. Classification Service to Storage Service
Type: Direct Call  
Sync/Async: Sync  
Protocol or Format: Internal method call with document and classification result  

### 6. Pipeline API to Extraction Service in background flow
Type: Message Queue  
Sync/Async: Async  
Protocol or Format: JSON message with job and document reference  

### 7. Extraction Service to Classification Service in background flow
Type: Message Queue  
Sync/Async: Async  
Protocol or Format: JSON message with extracted text  

### 8. Classification Service to Storage Service in background flow
Type: Message Queue  
Sync/Async: Async  
Protocol or Format: JSON message with classification result  

### 9. Storage Service to Notification Service
Type: Message Queue  
Sync/Async: Async  
Protocol or Format: JSON message with processing completed event  

## Justification of Sync vs Async

Validation is synchronous because the client needs an immediate answer if the file is invalid.

In the direct processing flow, extraction, classification, and storage use synchronous direct calls because the client is waiting for the final result in the same request.

In the background flow, the system uses message queues so the client does not need to wait. This allows the job to continue in the background and supports better scalability.

Notification is asynchronous because informing the user does not need to block document processing.