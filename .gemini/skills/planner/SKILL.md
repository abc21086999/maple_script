---
name: planner
description: Enforces a strict "Understand -> Plan -> Approve -> Implement" workflow for all coding tasks. Use this when the user requests features, bug fixes, or any code modifications.
---

# Planner

## Overview

This skill forces a deliberate, safe, and transparent development process. It strictly prohibits immediate coding actions upon receiving a request. Instead, it mandates a preliminary investigation and planning phase.

## Workflow Rules

### Phase 1: Understanding & Investigation
**Trigger**: User makes a request (feature, fix, refactor).
**Action**:
1.  **Do NOT** write or modify any code yet.
2.  **Explore** the codebase to understand the context.
    *   Use `search_file_content` to find relevant keywords.
    *   Use `read_file` to examine existing implementations, patterns, and dependencies.
    *   Use `list_directory` to understand file structure.
3.  **Identify** dependencies, potential side effects, and architectural fit.

### Phase 2: Planning
**Trigger**: After understanding the context.
**Action**:
1.  **Formulate** a detailed, step-by-step action plan.
2.  **Reference** the template at `references/action_list_template.md` (read it if you need the structure, but you can adapt it).
3.  **Present** this plan to the user.
    *   The plan MUST be specific (e.g., "Modify `src/main.py` to add argument parsing" instead of "Update main").
    *   The plan MUST include a verification strategy (tests or checks).

### Phase 3: Approval & Iteration
**Trigger**: User reviews the plan.
**Action**:
1.  **Wait** for explicit user approval (e.g., "Go ahead", "Looks good", "Start").
2.  **If the user asks questions or requests changes**:
    *   Discuss the points.
    *   **Revise** the plan.
    *   **Go back** to the beginning of Phase 3 (Wait for approval of the *new* plan).

### Phase 4: Implementation
**Trigger**: User explicitly approves the plan.
**Action**:
1.  **Execute** the plan step-by-step.
2.  **Verify** each step as defined in the plan.