# Task 3.1: Compatibility policy


## 1. When do we need a new version? 

We categorize every change into two buckets so we know if we're making a "safe" update or a "scary" one.

### **Safe Stuff: Additive Changes**
* **What it is:** Adding a new optional field (like `priority`), a new optional search filter, or a brand new endpoint (like `/tasks/bulk`).
* **How we release it:** These are **MINOR** or **PATCH** updates. We don't change the URL.
* **The "Golden Rule":** We assume all clients follow **Postel’s Law** (be liberal in what you accept). If we add a field and a client crashes because it didn't expect it, that's actually a bug in their code, not ours. 

### **Breaking Stuff: Contract Changes**
* **What it is:** Renaming a field (`done` → `completed`), deleting a field, changing a number to a string, or making a header mandatory (like `X-Client-Id`). 
* **How we release it:** These **ALWAYS** require a new **MAJOR** version (like moving from `/v1/` to `/v2/`).
* **The Promise:** We will never "ninja-push" a breaking change to an existing version. If a partner is using `/v1/`, it should keep working exactly as it does today.


## 2. How we "Sunset" old versions

We can't keep old code running forever (it's a maintenance nightmare!), so we use a "Sunset" process to retire old versions gracefully.

1.  **The Heads Up:** We post an announcement on our Dashboard and send an email to all developers.
2.  **The 6-Month Timer:** Usually, partners have 6 months to move to the new version. If there’s a massive security hole, we might have to move faster (30 days), but that’s a "break glass in case of emergency" scenario.
3.  **The "Nag" Headers:** We’ll start sending a `Deprecation` header in the API response. It’s like a digital sticky note telling the client's developers: "Hey, this version is dying soon!"
4.  **Brownouts:** In the final month, we’ll purposely turn off the old version for 15 minutes at a time. It’s a "scream test"—if someone hasn't migrated yet, they'll definitely notice now!


## 3. Error Codes are Forever

When things go wrong, the way we say "oops" needs to stay consistent.

* **Codes are for machines:** The error `code` (like `VALIDATION_ERROR`) is a permanent part of our contract. Don't change the spelling or the casing!
* **Messages are for humans:** We can change the `message` string (the text people read) whenever we want to make it clearer. **Warning:** Never write code that looks for specific words in the message string—use the code instead!



## 4. Internal Apps vs. External Partners

We’re a bit stricter with ourselves than we are with our partners.

| Feature | Our Own Apps (Web/Mobile) | Outside Partners |
| :--- | :--- | :--- |
| **Deadline** | **3 Months.** We have the source code, so we should be fast. | **6-12 Months.** They have their own jobs to do; be patient. |
| **Communication** | Ping us on Slack! | Use the Support Portal. |
| **Beta Testing** | You get the "Alpha" bugs. Sorry! | They get the "mostly stable" Beta. |


## 5. How to stay in the loop

* **Check the Portal:** All major news goes to the "Announcements" page.
* **Watch your Inbox:** We’ll email the "Technical Lead" on file for each API key.
* **Read the Headers:** We sometimes tuck important alerts directly into the API response headers.
