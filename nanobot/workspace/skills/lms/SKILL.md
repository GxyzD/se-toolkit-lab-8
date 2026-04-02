---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

You have access to MCP tools that connect to the LMS backend.

## Available Tools

- `mcp_lms_lms_health` — check backend status and item count
- `mcp_lms_lms_labs` — list all labs with their names and IDs
- `mcp_lms_lms_pass_rates` — get per-task pass rates for a lab (requires lab parameter)
- `mcp_lms_lms_scores` — get score distribution for a lab
- `mcp_lms_lms_timeline` — get submission timeline for a lab
- `mcp_lms_lms_groups` — get group performance for a lab
- `mcp_lms_lms_top_learners` — get top students for a lab
- `mcp_lms_lms_completion_rate` — get completion percentage for a lab
- `mcp_lms_lms_sync_pipeline` — trigger ETL sync to refresh data

## Strategy

1. **When a lab is required but not specified:**
   - First call `mcp_lms_lms_labs` to get available labs
   - Ask the user to choose one
   - Show lab titles clearly

2. **For scores/pass rates/completion:**
   - If lab is given → call the tool directly
   - If not given → follow strategy #1

3. **Formatting:**
   - Show percentages with one decimal place (e.g., 92.3%)
   - Include attempt counts when available
   - Keep responses concise and user-friendly

4. **When the user asks "what can you do?":**
   - Explain you have LMS tools to query lab data, scores, pass rates, etc.
   - Mention you can help with lab-specific questions

5. **Multi-step reasoning:**
   - For "which lab has the lowest pass rate?" → get all labs, get pass rates for each, compare, answer

## Examples

**User:** Show me the scores
**Agent:** I can help with that. Which lab are you interested in? Available labs: Lab 01, Lab 02, Lab 03, Lab 04, Lab 05, Lab 06, Lab 07

**User:** Show me scores for Lab 04
**Agent:** Here are the pass rates for Lab 04:
- Task 1: 92.3% (245 attempts)
- Task 2: 78.5% (238 attempts)
