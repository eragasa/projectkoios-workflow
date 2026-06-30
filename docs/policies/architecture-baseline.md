# Architecture Baseline

## Purpose

This document records the current observed architecture.

It is not a list of decisions.

It is not a refactor plan.

It is a baseline for future reviews.

## Observed modules

| area | modules/files | notes |
|---|---|---|
| core/schema |  |  |
| runtime |  |  |
| UI |  |  |
| Petri-net/backend |  |  |
| adapters |  |  |
| tests |  |  |

## Observed dependency edges

| source | target | status |
|---|---|---|
|  |  | intended / questionable / legacy / unknown |

## Known problems

| id | area | issue | status | next action |
|---|---|---|---|---|
| D-001 |  |  | candidate | inspect later |
| D-002 |  |  | accepted legacy | do not block current work |

## Current target assumption

The working assumption is:

Core schema should remain independent of runtime, UI, Petri-net backends, process-mining libraries, and external adapters.

This assumption can be changed only by human decision.
