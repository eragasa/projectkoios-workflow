# `projectkoios.workflow.compilation.definitions` implementation

## Responsibility

Use frozen slotted records with strict built-in type validation, canonical tuple order, bounded collections, and a single content digest for each complete definition. Persist explicit schema and compiler-contract versions.

Migration evidence is historical `definitions.py`, blob `d39a473622aaa97d970279fd105ad6ba38e28c83`. Preserve its source-owner-to-final-value separation while extending definitions to carry fragment/action declarations needed for CPN lowering.
