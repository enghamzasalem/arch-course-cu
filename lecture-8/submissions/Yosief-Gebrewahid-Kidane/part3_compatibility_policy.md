# Part 3.1 — Compatibility Policy

## 1. Overview

This policy defines how the Task Board API evolves while keeping existing clients—web, mobile, and partner integrations—working reliably.  

Our goals are to:  
- Ensure predictable API evolution  
- Minimize disruption for clients  
- Communicate changes clearly and consistently  

---

## 2. Rules for API Changes

### 2.1 Non-Breaking Changes (Allowed Anytime)

The following are considered **backward-compatible**:

- Adding optional request parameters  
- Adding optional response fields (e.g., `priority`)  
- Adding new endpoints (e.g., `/tasks/bulk`)  
- Adding new error codes without removing existing ones  

These changes:  
- Do **not** break existing clients  
- Require a **MINOR version bump**  

---

### 2.2 Breaking Changes (Require Versioning)

The following changes are considered **breaking**:

- Renaming or removing fields (e.g., `done` → `completed`)  
- Adding required request fields or headers (e.g., `X-Client-Id`)  
- Changing validation rules that would reject previously valid requests  
- Changing response structure or data types  

These changes:  
- Require a **MAJOR version bump**  
- Must be introduced in a **new API version** (e.g., `/v2`)  

---

## 3. Deprecation Policy

### 3.1 Deprecation Process

When a breaking change is introduced:  

1. Release a new API version (e.g., v2)  
2. Mark the old version (v1) as **deprecated**  
3. Provide a **sunset period** of 6–12 months  

### 3.2 Communication

Deprecation is communicated through:  
- Updates in API documentation  
- Announcements on the developer portal  
- Emails to partner integrations  
- Optional response headers (e.g., `Deprecation`, `Sunset`)  

### 3.3 Sunset

After the sunset period:  
- Deprecated endpoints are removed  
- Requests to old versions return an error (e.g., `410 Gone`)  

---

## 4. Error Format Stability

The API guarantees a **stable error structure**:


{
  "error": {
    "code": "STRING_CONSTANT",
    "message": "Human-readable message"
  }
}

---

# Rules:

- error.code remains stable and machine-readable
- New error codes may be added
- Existing error codes are not removed or renamed without version change
- message may change (not relied on by clients)

---

## 5. Partner vs First-Party Clients
### Partner Integrations

- Require strict stability guarantees
- Receive early notice of breaking changes
- Have longer migration periods

### First-Party Clients (Web, Mobile)
- Can adopt changes faster
- May use feature flags or staged rollouts
- Expected to migrate earlier than partners

---

## 6. Compatibility Principles

- Prefer additive changes over breaking changes
- Maintain backward compatibility whenever possible
- Use versioning for breaking changes
- Design APIs to be tolerant to unknown fields
- Avoid unnecessary coupling between clients and internal implementation
