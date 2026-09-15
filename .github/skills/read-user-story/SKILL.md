---
name: read-user-story
description: "Read and extract a user story from userstory.docx, a Jira issue, or a Confluence page so the Requirements Agent can turn it into requirements. Use at the start of Step 1, or whenever a new user story must be ingested."
---

# Skill: Read User Story

Use this skill to reliably ingest a user story from any supported source and
extract the fields the Requirements Agent needs.

## Sources and how to read them

### 1. Local Word document (default: `userstory.docx`)
A `.docx` is a ZIP archive whose text lives in `word/document.xml`. Extract the
text (strip XML tags) rather than trying to read the raw bytes. Example
(PowerShell):

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead((Resolve-Path 'userstory.docx'))
$entry = $zip.Entries | Where-Object { $_.FullName -eq 'word/document.xml' }
$reader = New-Object System.IO.StreamReader($entry.Open())
$xml = $reader.ReadToEnd(); $reader.Close(); $zip.Dispose()
[System.Text.RegularExpressions.Regex]::Replace($xml, '<[^>]+>', ' ') `
  -replace '\s+', ' '
```

If the file is plain text disguised as `.docx`, read it directly.

### 2. Jira issue
Use the Atlassian MCP tools (e.g. `jira_get_issue`) with the issue key. Extract
summary, description, acceptance criteria, priority, labels, and linked issues
(dependencies). Never print credentials or tokens from the MCP configuration.

### 3. Confluence page
Use the Atlassian MCP tools (e.g. `confluence_get_page`) with the page ID or
title. Extract the story body and any acceptance-criteria / business-rules
tables.

## Fields to extract

- **Title** and the "As a … I want … so that …" statement
- **Description / context**
- **Acceptance criteria** (Given / When / Then)
- **Business rules and constraints** (security, compliance, HTTPS, masking, etc.)
- **Priority**
- **Dependencies** (other features, services, APIs, modules)
- **Actors / stakeholders**

## Output

Hand the extracted content to the Requirements Agent as structured notes. Flag
anything missing, vague, or conflicting as an **open question** — never invent
business-critical behavior. Preserve source wording for acceptance criteria so
they stay traceable.
