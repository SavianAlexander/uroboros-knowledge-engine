# ADR 003 Thread Local SQLite Lifecycle

## Status
ACCEPTED

## Summary
Prevent Windows WinError 32 permission locks via thread-local connection pooling and explicit reset.

## Provenance
- **Standard**: Ponytail Senior Dev
- **Project**: Neuro Alexander (Project #13)
