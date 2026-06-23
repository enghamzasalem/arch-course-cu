# Task 1.1 - Coupling Inventory

- **Web SPA -> API Gateway (Data coupling)**
The web application sends requests and receives responses through the API Gateway. If the gateway changes request paths, required headers, or response fields, the web client may fail to call the API correctly or may not be able to parse the response data.

- **Mobile App -> API Gateway (Data coupling)**  
The mobile app depends on the same API contract. If the gateway changes field names, removes fields, or changes validation rules, the mobile app may fail to process responses or may need an update to handle the new format.

- **Partner Integration -> API Gateway (Data coupling - stronger)**  
External partners use the same public API. If the API changes (for example renaming fields or adding required headers), partner systems may break because their clients expect a fixed schema and are not updated frequently.

- **API Gateway -> Task API (Control + Data coupling)**  
The API Gateway forwards requests to the Task API and depends on its behavior. If the Task API changes endpoint logic, required parameters, or response format, the gateway may route requests incorrectly or fail to handle responses properly.

- **Task API -> Task Store (Data coupling - tight)**  
The Task API directly interacts with the database. If the database schema changes (such as renamed columns or stricter constraints), the API queries may fail or return incorrect data.

- **Task API -> Notification Service (Temporal coupling)**  
The Task API may call the Notification Service during request processing. If the notification service is slow or unavailable, the API request may timeout or fail because it is waiting for the notification to complete.

## Two intentionally tight couplings

- **API Gateway -> Task API**  
This coupling is acceptable because the gateway must route requests to the correct backend service. A close dependency here is normal and necessary.

- **Task API -> Task Store**  
This coupling is acceptable because the Task API needs direct access to the database to manage task data. This dependency is part of the core functionality.

## Two couplings that should be reduced

- **Partner Integration -> API contract**  
This coupling should be reduced because partner systems are long-lived and not updated frequently. It can be improved by keeping backward compatibility, avoiding breaking changes, and using API versioning when needed.

- **Task API -> Notification Service**  
This coupling should be reduced because it creates a timing dependency. It can be improved by using asynchronous communication (for example events or queues), so the main task operation does not depend on the notification service being immediately available.