# Project Plan — Study Group Matcher

## Version 1: Quick Match MVP

### Objective
Create a minimal working product where students can find study partners based on the same course.

### Implementation Steps

1. **Create one simple web page** where a student enters their name and course.
2. **Send this data to the backend** and store it in a database.
3. **Check if another student with the same course already exists** using simple linear search with filtering by course.
4. **If a match is found**, display it on the page.
5. **Test the full flow**: input → match → display → Telegram message.

### Outcome
A minimal working MVP where students can quickly find someone in the same course and receive a Telegram notification when a match appears.

---

## Version 2: Full Study Group Matcher

### Objective
Build a complete application with smart matching, group formation, history tracking, and a polished user experience.

### Implementation Steps

1. **Add full user profiles** including:
   - Courses
   - Topics of interest
   - Availability / time preferences

2. **Improve matching logic** based on:
   - Course match
   - Topic overlap
   - Time availability overlap

3. **Allow users to accept or reject matches** with a request/response flow.

4. **Create study groups automatically** when both users accept a match.

5. **Add new pages** for:
   - Viewing matches
   - Viewing study groups

6. **Store history** of:
   - Past matches
   - Formed groups

7. **Deploy the full system** on a VM and refine based on feedback.

### Outcome
A complete application with:
- Smart matching algorithm
- Group formation workflow
- History tracking
- Polished user experience for ongoing use

---

## Feature Comparison

| Feature | Version 1 | Version 2 |
|---------|-----------|-----------|
| Name + course registration | ✅ | ✅ |
| Simple course match | ✅ | ✅ |
| Telegram notification | ✅ | ✅ |
| Topics & availability | ❌ | ✅ |
| Score-based matching (course + topics + time) | ❌ | ✅ |
| Accept / reject matches | ❌ | ✅ |
| Automatic study group creation | ❌ | ✅ |
| View matches page | ❌ | ✅ |
| View groups page | ❌ | ✅ |
| Match and group history | ❌ | ✅ |
| Deployment on VM | ✅ | ✅ |

---

## Technical Stack (Both Versions)

| Component | Technology |
|-----------|------------|
| Frontend | HTML, CSS, JavaScript |
| Backend | FastAPI (Python) |
| Database | SQLite (V1) / PostgreSQL (V2) |
| Notifications | Telegram Bot API |
| Deployment | Docker, Docker Compose |
| VM OS | Ubuntu 24.04 |
