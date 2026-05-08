# Known Limitations

- Smithsonian search can return rows tagged as image-bearing that do not contain usable media. The MCP layer drops those rows.
- Dates and descriptions are often sparse, especially for some museum units, so timelines and captions can be thin.
- `DEMO_KEY` is rate-limited and not reliable for repeat testing.
- The app is a prototype only. There is no auth, persistence, payments, retry logic, or production observability.
