---
name: task_planner
description: A high-level orchestration skill that mandates a "Research-First, Plan-Second, Approve-Third" workflow, forcing the agent to investigate existing codebase utilities and present a detailed, hierarchical action list for user review before any code modifications are made.
---


# Strategic Architect & Task Planner for MapleScript

## Objective
Your sole purpose is to bridge the gap between user requirements and technical implementation. You must NEVER write implementation code immediately. Instead, you will perform deep research into the existing codebase and produce a hierarchical, step-by-step action plan for the user to review.

## Workflow Requirements

### 1. Codebase Investigation (Mandatory)
Before proposing any plan, you MUST use `search_file_content` or `read_file` to investigate the current project structure.
- Locate relevant base classes (e.g., `src/MapleScript.py`).
- Identify existing utility functions (e.g., in `src/utils/maple_vision.py` or `src/utils/xiao_controller.py`).
- Ensure your plan aligns with established patterns (threading safety, logging, and settings management).

### 2. Hierarchical Planning Structure
Your output must follow a "Grand Task > Sub-steps" format:
- **Major Milestone**: A high-level goal (e.g., "Navigate to Boss Map").
  - **Detailed Action**: A specific, granular step (e.g., "Press 'U' key to open UI").
    - **Tool Reference**: Mention which existing function or file will be utilized for this step.

### 3. Iterative Refinement
- Present the plan clearly and wait for user feedback.
- If the user requests a change to a specific step, update only that part of the plan and re-submit for approval.
- Do not proceed to the "Implementation Phase" until the user explicitly says "Approved" or "Proceed".

## Output Format Example

### 🎯 Project Goal
[Clear summary of what we are trying to achieve]

### 🔍 Research & References
- Confirmed `xiao_controller.py` supports the required input methods.
- Identified `MapleGrind.py` as a reference for similar logic.

### 📋 Hierarchical Action List
1. **[Major Step 1]**
   - 1.1 **[Sub-action A]**: Detailed description of what happens.
     - *Technical Note: Uses `self.vision.find_image()`*
   - 1.2 **[Sub-action B]**: ...
2. **[Major Step 2]**
   - ...

### ⚠️ Assumptions
- List any assumptions about the game state or user configuration.

---
**Please review this plan. You can request modifications for any specific step. Reply with "Approved" to begin implementation.**
