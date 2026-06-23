# Task 2.1 Orchestrated Design

## Orchestrator

The orchestrator is the Pipeline API. It controls the order of the pipeline and decides which step runs next.

## Sequence of Calls

### Synchronous Flow

1. The client sends a request to the Pipeline API.  
2. The Pipeline API calls the Validation Service.  
3. If the document is valid, the Pipeline API calls the Extraction Service.  
4. The Pipeline API then calls the Classification Service with the extracted text.  
5. The Pipeline API then calls the Storage Service with the classification result.  
6. The Pipeline API returns the final result to the client.  

### Asynchronous Flow

1. The client sends a job request to the Pipeline API.  
2. The Pipeline API calls the Validation Service.  
3. If the document is valid, the Pipeline API creates a background job and returns a job ID to the client.  
4. The Pipeline API sends the job to the queue for background processing.  
5. The pipeline continues in the background through Extraction, Classification, and Storage.  
6. After storage is completed, the Notification Service notifies the client.  

## Error and Retry Handling

If validation fails, the Pipeline API returns an error immediately.

If extraction, classification, or storage fails in the synchronous flow, the Pipeline API stops the process and returns an error.

In the asynchronous flow, failed jobs can be retried without blocking the client.

If notification fails, the document can still remain stored, and the notification can be retried later.

## Advantage

If the processing order needs to change, for example by adding a new step between extraction and classification, the control logic can be updated in one main place.

## Disadvantage

If the Pipeline API goes down, both the synchronous and asynchronous flows are affected because the whole pipeline depends on it.