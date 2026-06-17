# Task 3.1 - Compatibility Policy

## 1. Additive vs Breaking Changes

**Additive (Non-breaking - MINOR)**
- Adding optional fields, new endpoints, optional headers
- Relaxing validation rules

**Breaking (MAJOR)**
- Removing or renaming fields
- Making optional fields required
- Stricter validation rules (e.g., reducing max length)
- Adding mandatory headers
- Changing error codes

## 2. Deprecation Process

- **Notice period:** 90 days for first-party apps, 180 days for partners
- **Communication:** Documentation, email, `Deprecation` and `Sunset` headers
- **Sunset:** Endpoint returns `410 Gone` after sunset date

## 3. Error Format Stability

- **Stable:** Error codes, JSON structure, HTTP status codes
- **Can change:** Error messages (human-readable)
- **Breaking:** Removing error codes or changing structure

## 4. Partners vs First-Party Apps

| Client Type | Notice Period | Support |
|-------------|---------------|---------|
| First-party apps | 90 days | Standard migration guide |
| Partners | 180 days | Dedicated support |

**Why:** Partners have longer release cycles and cannot update as quickly.

## 5. Client Responsibilities

- Read deprecation headers
- Migrate before sunset date
- Ignore unknown response fields
- Use versioned URLs (`/v2/`)