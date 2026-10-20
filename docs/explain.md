# Indexed query evidence

Query (admin list filtered by status, newest first):

```python
HealthProfile.objects.filter(status="active").order_by("-created_at").explain()
```

SQLite plan:

```
SEARCH profiles_healthprofile USING INDEX idx_profile_status_created (status=?)
```

- Composite index `(status, -created_at)` serves the filter and the ordering,
  so SQLite does not need a temporary B-tree sort.
- Without the index the plan would be a full table `SCAN` plus a sort.
- The composite index lets SQLite find the status='active' rows already ordered by created_at DESC, so no temporary B-tree sort is needed. On a few rows the planner may choose a scan either way, so the plan is the evidence here and timings are not.

## Why each index exists
| Index | Query it serves |
|---|---|
| `uniq_user_email_lower` (unique, on lower(email)) | login lookup and duplicate-email prevention |
| `idx_profile_status_created` | admin list: filter by status, newest first |
| `profiles_healthprofile.user_id` (unique, from OneToOne) | `GET /profiles/me` lookup by user |