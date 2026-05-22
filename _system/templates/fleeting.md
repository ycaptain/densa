---
type: fleeting
domain: <your-domain>
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
sources: []
aliases: []
tags: [fleeting]
status: active
compiled_against: 1
---

# <% tp.file.title %>

A short note. No structure required. Lint will flag this if it's still
here after 30 days; at that point either upgrade to a pattern/analysis
(and `git mv` this file under `wiki/.legacy/`) or delete the thought.
