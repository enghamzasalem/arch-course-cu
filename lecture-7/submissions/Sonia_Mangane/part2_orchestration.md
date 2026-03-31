# Part 2: Orchestrated Design

## 2.1 The Orchestrator: Pipeline Manager Service

In this design, we use a central Pipeline Manager (the Orchestrator). This component acts as the "brain" of the operation. None of the other services (Validator, Extractor, etc.) talk to each other; they only talk to the Manager.

### Exact Sequence of Calls
1.  **Start:** The API Gateway receives a document and sends it to the Pipeline Manager.
2.  **Step 1 (Validate):** The Manager calls the Validator. It waits for a "Success" or "Fail" response.
3.  **Step 2 (Extract):** If validated, the Manager sends the document to the Extractor. Because OCR takes a long time, the Manager monitors this task until it receives the text back.
4.  **Step 3 (Classify):** The Manager takes that text and sends it to the Classifier. It waits for the document label (e.g., "Invoice").
5.  **Step 4 (Store):** The Manager sends the final data to the Storage service.
6.  **Step 5 (Notify):** Once Storage confirms the save is complete, the Manager tells the Notifier to send the final alert to the user.

### Error Handling and Retries
Because the Manager is in control, it handles all the cases:
* **Retries:** If the Classifier is busy and returns an error, the Manager waits 5 seconds and tries again. This can can be implemented with a resilience system like Polly for .NET systems.
* **Centralized Logging:** If a document fails at the extraction step, the Manager logs the error in one central place so developers can see exactly where the process stopped.
* **Stop on Failure:** If the Validator says "Fail," the Manager immediately stops the sequence and tells the user, ensuring no time is wasted on the other steps.

---

## 2.2 Advantages and Disadvantages

### One Advantage: Easy to Follow and Debug
The biggest plus is visibility. Since all the logic is in the Pipeline Manager, you can look at one piece of code to understand the entire business process. If a document gets stuck, you only have to check the Manager’s logs to see which step failed.

### One Disadvantage: The "Single Point of Failure"
If the Pipeline Manager service crashes, the entire pipeline dies. Even if the Validator and Extractor are running perfectly, they won't do any work because no one is there to tell them what to do. The Manager becomes a bottleneck and a risky single point of failure.