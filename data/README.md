# Synopsys Running Community feed

`events` accepts `race` and `workout` records. Required fields are `id`, `type`, `title` and `date` (ISO `YYYY-MM-DD`). Optional fields: `time`, `meeting_point`, `location`, `sport`, `distance_km`, `pace`, `website`, `registration_url`, `notes`.

Example:

```json
{
  "id": "lungo-cascine-2026-10-03",
  "type": "workout",
  "title": "Lungo del sabato",
  "date": "2026-10-03",
  "time": "08:30",
  "meeting_point": "Parco delle Cascine",
  "sport": "running",
  "distance_km": 16,
  "pace": "5:30–6:00 min/km"
}
```
