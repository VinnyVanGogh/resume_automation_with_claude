---
allowed-tools: Bash(ls:*), Bash(ll:*), Bash(tree:*), Bash(git:*), Bash(gh:*), Read()
description: Command for priming Claude Code with core knowledge about your project
---

# Prime Context for Claude Code

## Context

1. Use the !`tree` command to get an overview of the project structure.
2. !`Read(CLAUDE.md)` to understand core principles and guidelines.
3. !`Read(README.md)` to get an overview of the project purpose and goals.
4. Read key files in the `@src/` directory to understand the implementation details.
5. List any additional files that are important to understand the project.

## Tasks

Based on the context gathered, create a comprehensive overview of the project for Claude Code. Confirm you understand by explaining the following:

- Project structure
- Project purpose and goals
- Key files and their purposes
- Any important dependencies
- Any important configuration files
