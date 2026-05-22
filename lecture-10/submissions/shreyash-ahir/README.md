# CityBite at Peak — Scalability Architecture

## File Map

```
submissions/YOUR_NAME/
├── part1_workload_and_bottlenecks.md    6 dimensions, hero scenario Fri 19:00 Amsterdam
├── part1_scale_decisions.md             5-row table, does-not-scale-infinitely note on DB
├── part2_data_scaling.md                Write path (strong vs eventual), read path, Redis cache, SQS decoupling
├── part2_architecture_steady_vs_peak.drawio
├── part2_architecture_steady_vs_peak.png
├── part3_patterns.md                    Load balancing, sharding, scatter/gather, master/worker, fairness
├── part3_autoscaling_and_limits.md      HPA YAML, backpressure policy, DB-forgot failure lesson
└── README.md
```

## Key Design Decisions

- **Scale out API pods via HPA** (min 3, max 20, 60% CPU target) -- stateless, fast to add.
- **Redis cache** (`menu:{restaurant_id}`, TTL 60s, active invalidation on update) -- eliminates duplicate DB reads per restaurant.
- **Read replica** for kitchen dashboard -- protects primary from reporting queries at peak.
- **SQS + worker pool** -- decouples order confirmation from SMS/push latency (example2 pattern).
- **PgBouncer transaction pooling** -- breaks coupling between pod count and DB connection count.
- **Per-restaurant rate limiting** -- prevents one viral restaurant from starving others.
