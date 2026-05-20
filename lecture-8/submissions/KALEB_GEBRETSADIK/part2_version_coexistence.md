# Part 2.2: Version Coexistence Strategy

## 1. Chosen Strategy: Global Path Prefixing (`/v1/` vs `/v2/`) with Internal Adapters
To guarantee safe coexistence during a major breaking release, I recommend implementing **Global Path Versioning** at the API Gateway level (e.g., `api.example.com/v1/tasks` and `api.example.com/v2/tasks`), combined with an internal translation adapter within the Task API service. 

While custom `Accept-Version` headers are technically more strictly REST-compliant, URL paths are significantly easier for external Partners to configure, cache at the CDN level, and debug via proxy logs.

## 2. Managing the Sunset Period (Legacy vs. New Clients)

During our defined deprecation grace window (e.g., 6 to 12 months), both versions will safely coexist side-by-side using the following flow:

- **Legacy Clients (Older Mobile Installs & Partner Integrations):** 
  Existing clients remain pinned to the `/v1/` endpoints. When the API Gateway routes a `/v1/` request, hits the backend service, the request is intercepted by a "V1 Translation Adapter". For example, if a partner creates a task in V1, the Adapter dynamically maps `done: false` to `completed: false` and intercepts the lack of an `X-Client-Id` header by injecting a generic `legacy-v1-client` override string before writing to the shared database.
- **New & Migrated Clients (Web SPA & Updated Integrations):** 
  Clients point their base URLs to the new `/v2/` endpoints. They bypass the translation adapter entirely, interact with the pure, modern domain schema (utilizing `completed`, `priority`, and the new `/tasks/bulk` route).
- **Sunset Termination:**
  Once the Gateway metrics confirm `/v1/` traffic has flatlined or the deprecation deadline is reached, the Gateway routing rule is deleted (returning `HTTP 410 Gone`), and the backend engineers can safely tear down the V1 translation code.

## 3. The Major Operational Cost

The primary operational cost of this coexistence strategy is the **Code Maintenance Burden and Dual-Testing Overhead**. 
Instead of deploying code and walking away, engineers are forced to actively maintain the legacy translation layer for the entire year. Every time a new database column or feature is added to the core domain, engineers must systematically verify that the V1 Adapter successfully strips, hides, or defaults the new data so that legacy parsing schemas are not accidentally invalidated.
