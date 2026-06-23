# Task 3.1 - Compatibility Policy

This policy defines how API changes are managed to ensure compatibility for clients, including first-party applications and external partners.

## 1. Rules for Additive vs Breaking Changes

### Additive Changes (Backward-Compatible)

The following changes are allowed without breaking existing clients:

- Adding new optional fields to responses
- Adding new endpoints
- Adding new optional request parameters
- Expanding enum values (if clients are expected to ignore unknown values)

These changes follow MINOR version updates and do not require client updates.

### Breaking Changes (Non-Backward-Compatible)

The following changes are considered breaking:

- Removing or renaming fields
- Changing field types or required constraints
- Introducing new required request headers or parameters
- Changing validation rules that reject previously valid requests

Breaking changes require a MAJOR version and must not be introduced in-place. Instead, they must be released under a new API version (e.g., /v2).

## 2. Deprecation Process

### Notice Period

A minimum 90-day deprecation period is required before removing or disabling an API version. Critical fixes may shorten this period only in exceptional cases such as security issues.

### Communication Channels

Deprecation notices are communicated through API documentation updates, developer portal announcements, email notifications to registered partners, and response headers such as `Deprecation` and `Sunset`.

### Sunset Announcement

Deprecated endpoints include a Sunset date in responses. After the sunset date, the endpoint may return errors such as `410 Gone` and traffic may be fully migrated to the newer version.

## 3. Error Format Stability

### Stable Elements

- Error response format (JSON structure)
- Error codes (e.g., `VALIDATION_ERROR`, `MISSING_CLIENT_ID`)
- Field names in error responses

### Allowed Changes

- Error messages (human-readable text) may change
- New error codes may be added

### Breaking Changes

Removing or renaming error codes is considered breaking. Changing the structure of the error response is not allowed without versioning.

## 4. Partner Integrations vs First-Party Apps

### Partner Integrations

Partner integrations are treated as highly stable clients. They require strict backward compatibility, and breaking changes must always go through the versioning and deprecation process. Partners receive a minimum 180-day sunset period, while first-party applications follow the standard 90-day period.

### First-Party Applications

First-party applications can be updated more frequently and may adopt new API versions earlier. They can tolerate faster migration cycles.