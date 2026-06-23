# Task 2.2 Choreographed Design

## Events

- `DocumentSubmitted`
- `DocumentValidated`
- `ValidationFailed`
- `TextExtracted`
- `DocumentClassified`
- `DocumentStored`
- `NotificationSent`

## Component Event Responsibilities

### 1. Pipeline API
Subscribes to: None  
Publishes: `DocumentSubmitted` when a new document request is accepted  

### 2. Validation Service
Subscribes to: `DocumentSubmitted`  
Publishes: `DocumentValidated` when the document passes validation  
Publishes: `ValidationFailed` when the document is invalid  

### 3. Extraction Service
Subscribes to: `DocumentValidated`  
Publishes: `TextExtracted` when text extraction is completed  

### 4. Classification Service
Subscribes to: `TextExtracted`  
Publishes: `DocumentClassified` when classification is completed  

### 5. Storage Service
Subscribes to: `DocumentClassified`  
Publishes: `DocumentStored` when the document and result are stored successfully  

### 6. Notification Service
Subscribes to: `DocumentStored`  
Publishes: `NotificationSent` when the user notification is sent  

## Flow Description

There is no central orchestrator in this design. The flow happens through events.  
The Pipeline API only publishes the first event. After that, each component reacts to the previous event and publishes the next one.

The event flow is:

`DocumentSubmitted` --> `DocumentValidated` --> `TextExtracted` --> `DocumentClassified` --> `DocumentStored` --> `NotificationSent`

If validation fails, the flow stops after `ValidationFailed`.

## Advantage

This design has loose coupling because each component only reacts to events and does not need to know the internal logic of other components.

## Disadvantage

This design is harder to trace because the full pipeline flow is spread across multiple event handlers instead of one central place.