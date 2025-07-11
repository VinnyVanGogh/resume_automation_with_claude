---
allowed-tools: Bash(git:*), Bash(ls:*), Bash(cd:*), Bash(pwd:*), Bash(mkdir:*), Bash(rm:*), Bash(cat:*), Bash(echo:*), Read(), Write(), TodoWrite(), TodoRead(), Bash(gh:*)
description: Implement a specification using an existing SPEC PRP. (create these using `/spec-create-adv`)
---

# PRP File: $ARGUMENTS

## Context

1. Use the !`tree` command to get an overview of the project structure.
2. Confirm you're in a virtual environment if the project is Python-based !`echo $VIRTUAL_ENV`. (If not, activate it with !`source venv/bin/activate` !`cenv`.)
3. !`Read(CLAUDE.md)` to understand core principles and guidelines.
4. !`Read(README.md)` to get an overview of the project purpose and goals.
5. Read key files in the `@src/` directory to understand the implementation details.
6. List any additional files that are important to understand the project.

## Execution Process

**Important Note**: Make sure to track your progress as you go through comprehensive git commits as you complete each task or TodoWrite item. This will help us track progress and understand the development process later. If you are working with GitHub issues, make sure to close the issues as you complete the issue through working on the PRP.

Based on the context gathered, create a comprehensive implementation plan for the specification. Confirm you understand by explaining the following in your plan:

1. **Understand Spec**

   - Current state analysis
   - Desired state goals
   - Task dependencies

2. **ULTRATHINK**

   - Think hard before you execute the plan. Create a comprehensive plan addressing all requirements.
   - Break down complex tasks into smaller, manageable steps using your todos tools.
   - Use the TodoWrite tool to create and track your implementation plan.
   - Identify implementation patterns from existing code to follow.

3. **Execute Tasks**

   - Follow task order
   - Run validation after each
   - Fix failures before proceeding

4. **Verify Transformation**
   - Confirm desired state achieved
   - Run all validation gates
   - Test integration

Progress through each objective systematically.
