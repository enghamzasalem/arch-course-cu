# Task 1.1 - Workload Dimensions and Bottlenecks

## Workload dimensions

1. Concurrent customer sessions  
This is measured by the number of active users at the same time. When many users browse menus and refresh order status, database connections are usually the first resource to saturate because each request needs access to the database.

2. Orders per minute  
This measures how many checkouts happen in a short time. This mainly affects database CPU, since every order creates write operations in PostgreSQL. During peak times, the database becomes a bottleneck because it must process many writes consistently.

3. Kitchen dashboard queries per restaurant  
This can be measured as requests per minute from restaurant tablets. If queries are not optimized, CPU or database CPU can become a problem. For example, scanning all orders instead of filtering by restaurant_id increases the cost of each request.

4. Dispatch dashboard queries  
These are repeated reads from internal systems that monitor deliveries. This can be measured as polling frequency. The main limitation here is database connections, since many repeated queries can overload the system.

5. Menu image traffic  
This can be measured as data transferred per minute. When many users browse menus at the same time, network egress becomes the first resource that saturates.

6. Notification or background job volume  
This includes tasks like sending order confirmations or updates. This can be measured as jobs per minute. The resource that usually saturates here is worker CPU, since many jobs need to be processed at the same time.

## Hero scenario

The main scenario is Friday 19:00 to 21:00 in one city, which represents the dinner rush. During this time, many customers place orders at the same time, restaurants keep refreshing their dashboards, and dispatch systems are also active.

If the system scales well, the app still feels responsive. Customers can place orders without waiting, restaurant tablets update quickly, and dispatch continues to work without delays.

If the system scales poorly, users experience slow responses and failed checkouts. Restaurant dashboards may lag behind real orders, and dispatch may show outdated information. This usually happens when the database or connection pool cannot handle the increased workload.