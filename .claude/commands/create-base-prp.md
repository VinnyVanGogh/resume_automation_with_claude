---
allowed-tools: Bash(ls:*), Bash(cd:*), Bash(pwd:*), Bash(mkdir:*), Bash(rm:*), Bash(cat:*), Bash(echo:*), Read()
description: A comprehensive guide to creating a base PRP (Product Requirement Prompt) for feature implementation or a new project.
---

# Create BASE PRP

## Feature: $ARGUMENTS

Generate a complete PRP for general feature implementation with thorough research. Ensure context is passed to the AI agent to enable self-validation and iterative refinement.

The AI agent only gets the context you are appending to the PRP and training data. Assume the AI agent has access to the codebase and the same knowledge cutoff as you, so its important that your research findings are included or referenced in the PRP. The Agent has Websearch and MCP capabilities, so pass urls and reference things such as context7 in documentation and examples.

## Research Process

1. **Codebase Analysis**

   - Search for similar features/patterns in the codebase
   - Identify files to reference in PRP
   - Note existing conventions to follow
   - Check test patterns for validation approach

2. **External Research**

   - Search for similar features/patterns online
   - Library documentation (use and reference context7 mcp server before URLs)
   - Implementation examples (Context7/GitHub/StackOverflow/blogs)
   - Best practices and common pitfalls

3. **User Clarification** (if needed)
   - Specific patterns to mirror and where to find them?
   - Integration requirements and where to find them?

## PRP Generation

Using PRPs/templates/prp_base.md as template:

### Critical Context to Include and pass to the AI agent as part of the PRP

- **Documentation**: URLs with specific sections or library's and their ID's in context7
- **Code Examples**: Real snippets from codebase or external sources such as GitHub or Context7
- **Gotchas**: Library quirks, version issues
- **Patterns**: Existing approaches to follow

### Implementation Blueprint

- Start with pseudocode showing approach
- Reference real files for patterns
- Include error handling strategy
- list tasks to be completed to fullfill the PRP in the order they should be completed

### Validation Gates (Must be Executable) eg for python

```bash
# Syntax/Style
ruff check --fix && mypy .

# Unit Tests
uv run pytest tests/ -v

```

**_ CRITICAL AFTER YOU ARE DONE RESEARCHING AND EXPLORING THE CODEBASE BEFORE YOU START WRITING THE PRP _**

**_ ULTRATHINK ABOUT THE PRP AND PLAN YOUR APPROACH THEN START WRITING THE PRP _**

## Output

Save as: `PRPs/{feature-name}.md`

## Quality Checklist

- [ ] All necessary context included
- [ ] Validation gates are executable by AI
- [ ] References existing patterns
- [ ] Clear implementation path
- [ ] Error handling documented

Score the PRP on a scale of 1-10 (confidence level to succeed in one-pass implementation using claude codes)

Remember: The goal is one-pass implementation success through comprehensive context.
