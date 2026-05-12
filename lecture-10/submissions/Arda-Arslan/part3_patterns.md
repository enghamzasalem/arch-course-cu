# Task 3.1 - Pattern Checklist

## Load balancing

CityBite should use load balancing in front of the Order API pods, because the API layer is stateless and can be replicated easily. This helps distribute requests during dinner spikes and marketing campaigns. It is a good first step because it is simple and works well with Kubernetes scaling. However, load balancing alone is not enough if all pods still depend on the same database bottleneck.

## Sharding / partitioning

CityBite can use partitioning based on restaurant_id, since many queries already focus on one restaurant, such as kitchen dashboards. This keeps queries local and avoids scanning all orders. It follows the idea that each request should only touch the data it needs. However, sharding is not the first choice in Year 1 because it adds complexity and is harder to operate. Multi-tenant fairness is important here, because one viral restaurant should not slow down queries for other restaurants.

## Scatter / gather

Scatter / gather is not needed for the main order flow in CityBite. Checkout and kitchen views should stay simple and fast, so adding fan-out requests would increase latency. A better use case could be something like “trending restaurants” or search across many restaurants, where results can be collected and combined. For the core system, this pattern is not the first choice because it introduces extra coordination.

## Master / worker

CityBite should use a master / worker pattern for background tasks after an order is placed. The Order API can act as the entry point, while workers handle tasks like notifications separately. This improves response time because users do not wait for slow external operations. It also supports scaling, since workers can be increased independently. Multi-tenant fairness can be handled here by limiting how many jobs one restaurant can create, so one busy restaurant does not affect others.