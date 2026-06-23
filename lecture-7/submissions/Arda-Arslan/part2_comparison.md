# Task 2.3 Comparison and Recommendation

## Comparison

### Ease of changing the pipeline order  
Orchestration: Easier, because the order is controlled in one place by the Pipeline API.  
Choreography: Harder, because the order depends on events and subscriptions.

### Ease of adding new steps  
Orchestration: New steps require changes in the Pipeline API.  
Choreography: Easier, because a new component can subscribe to an existing event.

### Debugging and tracing  
Orchestration: Easier, because the flow is controlled in one place.  
Choreography: Harder, because the flow is distributed across multiple components.

### Latency and scalability  
Orchestration: Good for synchronous processing, but the Pipeline API can become a bottleneck.  
Choreography: Better for scalability, because components process events independently.

## Recommendation

For this document pipeline, a hybrid approach is the best choice. Orchestration is more suitable for the synchronous path because the client expects an immediate result and the flow is easier to control. Choreography is more suitable for the asynchronous path because background processing and notifications work better with events. This combination fits the requirements of the pipeline better than using only one approach.