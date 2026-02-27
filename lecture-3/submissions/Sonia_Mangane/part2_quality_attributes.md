# Quality Attributes Analysis

## 1. Availability

### Definition: (External, Dynamic)
The measure of the system's ability to remain operational and accessible to its users over a specific period.
### Importance:
If a user cannot unlock their front door or turn off a gas leak alarm because the system is "down," the smart home is a failure. Essential services must be reachable 24/7.
### Architecture support
This is supported by the microservices architecture. Ensuring that if one service fails, it does not affect the availability of the other services. 
### Trade-offs:
One of the biggest issues is that of increaed complexity and data redundancy which increases costs.

## 2. Security

### Definition: (External quality attribute, dynamic)
The ability of the system to protect data and resources from unauthorized access while providing access to authorized users.
### Importance:
A smart home captures sensitive video feeds and controls physical entry. A breach is a violation of privacy and a threat to physical safety. We need to ensure that user data is protected.
### Architecture support
The API Gateway centralizes authentication and the Repository Pattern ensures that raw database access is never exposed directly to business logic.
### Trade-offs:
Strong security measures (such as constant authentication and validation) typically increase Latency and can negatively impact perfomance.

## 3. Scalability

### Definition: (External quality attribute, dynamic)
Scalability is the ability of the system to handle increasing load without performance degradation.
### Importance:
The number of connected devices may grow, prioritazing scalability ensures that the application can be scaled.
### Architecture support
The microservice architecture allows the services to scale independently. The assumed cloud infrastructure enables horizontal scaling.
### Trade-offs:
By prioritazing scalability we become prevy to higher operational complexity and distributed monitoring required.

## 4. Performance

### Definition: (External quality attribute, dynamic)
Performance measures system responsiveness and throughput.
### Importance:
Device commands must execute instantly. Users expect near-instant feedback. If a user clicks "Light On" and it takes 5 seconds to respond, the system feels broken.
### Architecture support
The Singleton Pattern keeps a single communication socket permanently open to the message broker. This means the system doesn't waste time "dialing the number" every time you want to toggle a light, it's already on the line.
### Trade-offs:
To achieve low latency, we often trade Consistency. We use asynchronous messaging, meaning the UI might update before the database has finished writing the record.

## 5. Maintainaility

### Definition: (Internal quality attribute, static)
The ease with which the system can be modified without introducing defects or degrading existing product quality.
### Importance:
New protocols and hardware must be integrated frequently without rewriting the whole system. New automation rules may be introduced and features evolve over time. So it is important that the application can easily adapt to this.
### Architecture support
The microservice architecture  ensures that a change in one service does not break the other functionalities. The event driven architecture ensures that a user can add a new service simply by having it "listen" to the existing message broker.
### Trade-offs:
To make the system modifiable, we use many abstractions. This can be confused for some developers.
