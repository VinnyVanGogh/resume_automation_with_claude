# Claude Code overview

> Learn about Claude Code, an agentic coding tool made by Anthropic.

Claude Code is an agentic coding tool that lives in your terminal, understands your codebase, and helps you code faster through natural language commands. By integrating directly with your development environment, Claude Code streamlines your workflow without requiring additional servers or complex setup.

```bash
npm install -g @anthropic-ai/claude-code
```

Claude Code's key capabilities include:

* Editing files and fixing bugs across your codebase
* Answering questions about your code's architecture and logic
* Executing and fixing tests, linting, and other commands
* Searching through git history, resolving merge conflicts, and creating commits and PRs
* Browsing documentation and resources from the internet using web search
* Works with [Amazon Bedrock and Google Vertex AI](/en/docs/claude-code/bedrock-vertex-proxies) for enterprise deployments

## Why Claude Code?

Claude Code operates directly in your terminal, understanding your project context and taking real actions. No need to manually add files to context - Claude will explore your codebase as needed.

### Enterprise integration

Claude Code seamlessly integrates with enterprise AI platforms. You can connect to [Amazon Bedrock or Google Vertex AI](/en/docs/claude-code/bedrock-vertex-proxies) for secure, compliant deployments that meet your organization's requirements.

### Security and privacy by design

Your code's security is paramount. Claude Code's architecture ensures:

* **Direct API connection**: Your queries go straight to Anthropic's API without intermediate servers
* **Works where you work**: Operates directly in your terminal
* **Understands context**: Maintains awareness of your entire project structure
* **Takes action**: Performs real operations like editing files and creating commits

## Getting started

To get started with Claude Code, follow our [installation guide](/en/docs/claude-code/getting-started) which covers system requirements, installation steps, and authentication process.

## Quick tour

Here's what you can accomplish with Claude Code:

### From questions to solutions in seconds

```bash
# Ask questions about your codebase
claude
> how does our authentication system work?

# Create a commit with one command
claude commit

# Fix issues across multiple files
claude "fix the type errors in the auth module"
```

### Understand unfamiliar code

```
> what does the payment processing system do?
> find where user permissions are checked
> explain how the caching layer works
```

### Automate Git operations

```
> commit my changes
> create a pr
> which commit added tests for markdown back in December?
> rebase on main and resolve any merge conflicts
```

## Next steps

<CardGroup>
  <Card title="Getting started" icon="rocket" href="/en/docs/claude-code/getting-started">
    Install Claude Code and get up and running
  </Card>

  <Card title="Core features" icon="star" href="/en/docs/claude-code/common-tasks">
    Explore what Claude Code can do for you
  </Card>

  <Card title="Commands" icon="terminal" href="/en/docs/claude-code/cli-usage">
    Learn about CLI commands and controls
  </Card>

  <Card title="Configuration" icon="gear" href="/en/docs/claude-code/settings">
    Customize Claude Code for your workflow
  </Card>
</CardGroup>

## Additional resources

<CardGroup>
  <Card title="Claude Code tutorials" icon="graduation-cap" href="/en/docs/claude-code/tutorials">
    Step-by-step guides for common tasks
  </Card>

  <Card title="Troubleshooting" icon="wrench" href="/en/docs/claude-code/troubleshooting">
    Solutions for common issues with Claude Code
  </Card>

  <Card title="Bedrock & Vertex integrations" icon="cloud" href="/en/docs/claude-code/bedrock-vertex-proxies">
    Configure Claude Code with Amazon Bedrock or Google Vertex AI
  </Card>

  <Card title="Reference implementation" icon="code" href="https://github.com/anthropics/claude-code/tree/main/.devcontainer">
    Clone our development container reference implementation.
  </Card>
</CardGroup>

## License and data usage

Claude Code is provided under Anthropic's [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms).

### How we use your data

We aim to be fully transparent about how we use your data. We may use feedback to improve our products and services, but we will not train generative models using your feedback from Claude Code. Given their potentially sensitive nature, we store user feedback transcripts for only 30 days.

#### Feedback transcripts

If you choose to send us feedback about Claude Code, such as transcripts of your usage, Anthropic may use that feedback to debug related issues and improve Claude Code's functionality (e.g., to reduce the risk of similar bugs occurring in the future). We will not train generative models using this feedback.

### Privacy safeguards

We have implemented several safeguards to protect your data, including limited retention periods for sensitive information, restricted access to user session data, and clear policies against using feedback for model training.

For full details, please review our [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms) and [Privacy Policy](https://www.anthropic.com/legal/privacy).

### License

© Anthropic PBC. All rights reserved. Use is subject to Anthropic's [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms).


# Getting started with Claude Code

> Learn how to install, authenticate, and start using Claude Code.

## Check system requirements

* **Operating Systems**: macOS 10.15+, Ubuntu 20.04+/Debian 10+, or Windows via WSL
* **Hardware**: 4GB RAM minimum
* **Software**:
  * Node.js 18+
  * [git](https://git-scm.com/downloads) 2.23+ (optional)
  * [GitHub](https://cli.github.com/) or [GitLab](https://gitlab.com/gitlab-org/cli) CLI for PR workflows (optional)
  * [ripgrep](https://github.com/BurntSushi/ripgrep?tab=readme-ov-file#installation) (rg) for enhanced file search (optional)
* **Network**: Internet connection required for authentication and AI processing
* **Location**: Available only in [supported countries](https://www.anthropic.com/supported-countries)

<Note>
  **Troubleshooting WSL installation**

  Currently, Claude Code does not run directly in Windows, and instead requires WSL. If you encounter issues in WSL:

  1. **OS/platform detection issues**: If you receive an error during installation, WSL may be using Windows `npm`. Try:

     * Run `npm config set os linux` before installation
     * Install with `npm install -g @anthropic-ai/claude-code --force --no-os-check` (Do NOT use `sudo`)

  2. **Node not found errors**: If you see `exec: node: not found` when running `claude`, your WSL environment may be using a Windows installation of Node.js. You can confirm this with `which npm` and `which node`, which should point to Linux paths starting with `/usr/` rather than `/mnt/c/`. To fix this, try installing Node via your Linux distribution's package manager or via [`nvm`](https://github.com/nvm-sh/nvm).
</Note>

## Install and authenticate

<Steps>
  <Step title="Install Claude Code">
    Install [NodeJS 18+](https://nodejs.org/en/download), then run:

    ```sh
    npm install -g @anthropic-ai/claude-code
    ```

    <Warning>
      Do NOT use `sudo npm install -g` as this can lead to permission issues and
      security risks. If you encounter permission errors, see [configure Claude
      Code](/en/docs/claude-code/troubleshooting#linux-permission-issues) for recommended solutions.
    </Warning>
  </Step>

  <Step title="Navigate to your project">
    ```bash
    cd your-project-directory 
    ```
  </Step>

  <Step title="Start Claude Code">
    ```bash
    claude
    ```
  </Step>

  <Step title="Complete authentication">
    Claude Code offers multiple authentication options:

    1. **Anthropic Console**: The default option. Connect through the Anthropic Console and
       complete the OAuth process. Requires active billing at [console.anthropic.com](https://console.anthropic.com).
    2. **Claude App (with Pro or Max plan)**: Subscribe to Claude's [Pro or Max plan](https://www.anthropic.com/pricing) for a unified subscription that includes both Claude Code and the web interface. Get more value at the same price point while managing your account in one place. Log in with your Claude.ai account. During launch, choose the option that matches your subscription type.
    3. **Enterprise platforms**: Configure Claude Code to use
       [Amazon Bedrock or Google Vertex AI](/en/docs/claude-code/bedrock-vertex-proxies)
       for enterprise deployments with your existing cloud infrastructure.
  </Step>
</Steps>

## Initialize your project

For first-time users, we recommend:

<Steps>
  <Step title="Start Claude Code">
    ```bash
    claude
    ```
  </Step>

  <Step title="Run a simple command">
    ```bash
    summarize this project
    ```
  </Step>

  <Step title="Generate a CLAUDE.md project guide">
    ```bash
    /init 
    ```
  </Step>

  <Step title="Commit the generated CLAUDE.md file">
    Ask Claude to commit the generated CLAUDE.md file to your repository.
  </Step>
</Steps>

# Core tasks and workflows

> Explore Claude Code's powerful features for editing, searching, testing, and automating your development workflow.

Claude Code operates directly in your terminal, understanding your project
context and taking real actions. No need to manually add files to context -
Claude will explore your codebase as needed.

## Understand unfamiliar code

```
> what does the payment processing system do?
> find where user permissions are checked
> explain how the caching layer works
```

## Automate Git operations

```
> commit my changes
> create a pr
> which commit added tests for markdown back in December?
> rebase on main and resolve any merge conflicts
```

## Edit code intelligently

```
> add input validation to the signup form
> refactor the logger to use the new API
> fix the race condition in the worker queue
```

## Test and debug your code

```
> run tests for the auth module and fix failures
> find and fix security vulnerabilities
> explain why this test is failing
```

## Encourage deeper thinking

For complex problems, explicitly ask Claude to think more deeply:

```
> think about how we should architect the new payment service
> think hard about the edge cases in our authentication flow
```

Claude Code will show when the model is using extended thinking. You can
proactively prompt Claude to "think" or "think deeply" for more
planning-intensive tasks. We suggest that you first tell Claude about your task
and let it gather context from your project. Then, ask it to "think" to create a
plan.

<Tip>
  Claude will think more based on the words you use. For example, "think hard" will trigger more extended thinking than saying "think" alone.

  For more tips, see
  [Extended thinking tips](/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips).
</Tip>

## Automate CI and infra workflows

Claude Code comes with a non-interactive mode for headless execution. This is
especially useful for running Claude Code in non-interactive contexts like
scripts, pipelines, and Github Actions.

Use `--print` (`-p`) to run Claude in non-interactive mode. In this mode, you
can set the `ANTHROPIC_API_KEY` environment variable to provide a custom API
key.

Non-interactive mode is especially useful when you pre-configure the set of
commands Claude is allowed to use:

```sh
export ANTHROPIC_API_KEY=sk_...
claude -p "update the README with the latest changes" --allowedTools "Bash(git diff:*)" "Bash(git log:*)" Write --disallowedTools ...
```

# IDE integrations

> Integrate Claude Code with your favorite development environments

Claude Code seamlessly integrates with popular Integrated Development
Environments (IDEs) to enhance your coding workflow. This integration allows you
to leverage Claude's capabilities directly within your preferred development
environment.

## Supported IDEs

Claude Code currently supports two major IDE families:

* **Visual Studio Code** (including popular forks like Cursor and Windsurf)
* **JetBrains IDEs** (including PyCharm, WebStorm, IntelliJ, and GoLand)

## Features

* **Quick launch**: Use `Cmd+Esc` (Mac) or `Ctrl+Esc` (Windows/Linux) to open
  Claude Code directly from your editor, or click the Claude Code button in the
  UI
* **Diff viewing**: Code changes can be displayed directly in the IDE diff
  viewer instead of the terminal. You can configure this in `/config`
* **Selection context**: The current selection/tab in the IDE is automatically
  shared with Claude Code
* **File reference shortcuts**: Use `Cmd+Option+K` (Mac) or `Alt+Ctrl+K`
  (Linux/Windows) to insert file references (e.g., @File#L1-99)
* **Diagnostic sharing**: Diagnostic errors (lint, syntax, etc.) from the IDE
  are automatically shared with Claude as you work

## Installation

### VS Code

1. Open VSCode
2. Open the integrated terminal
3. Run `claude` - the extension will auto-install

Going forward you can also use the `/ide` command in any external terminal to
connect to the IDE.

<Note>
  These installation instructions also apply to VS Code forks like Cursor and
  Windsurf.
</Note>

### JetBrains IDEs

Install the
[Claude Code plugin](https://docs.anthropic.com/s/claude-code-jetbrains) from
the marketplace and restart your IDE.

<Note>
  The plugin may also be auto-installed when you run `claude` in the integrated
  terminal. The IDE must be restarted completely to take effect.
</Note>

<Warning>
  **Remote Development Limitations**: When using JetBrains Remote Development,
  you must install the plugin in the remote host via `Settings > Plugin (Host)`.
</Warning>

## Configuration

Both integrations work with Claude Code's configuration system. To enable
IDE-specific features:

1. Connect Claude Code to your IDE by running `claude` in the built-in terminal
2. Run the `/config` command
3. Set the diff tool to `auto` for automatic IDE detection
4. Claude Code will automatically use the appropriate viewer based on your IDE

If you're using an external terminal (not the IDE's built-in terminal), you can
still connect to your IDE by using the `/ide` command after launching Claude
Code. This allows you to benefit from IDE integration features even when running
Claude from a separate terminal application. This works for both VS Code and
JetBrains IDEs.

<Note>
  When using an external terminal, to ensure Claude has default access to the
  same files as your IDE, start Claude from the same directory as your IDE
  project root.
</Note>

## Troubleshooting

### VS Code extension not installing

* Ensure you're running Claude Code from VS Code's integrated terminal
* Ensure that the CLI corresponding to your IDE is installed:
  * For VS Code: `code` command should be available
  * For Cursor: `cursor` command should be available
  * For Windsurf: `windsurf` command should be available
  * If not installed, use `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
    and search for "Shell Command: Install 'code' command in PATH" (or the
    equivalent for your IDE)
* Check that VS Code has permission to install extensions

### JetBrains plugin not working

* Ensure you're running Claude Code from the project root directory
* Check that the JetBrains plugin is enabled in the IDE settings
* Completely restart the IDE. You may need to do this multiple times
* For JetBrains Remote Development, ensure that the Claude Code plugin is
  installed in the remote host and not locally on the client

For additional help, refer to our
[troubleshooting guide](/en/docs/claude-code/troubleshooting) or reach out to
support.


# CLI usage and controls

> Learn how to use Claude Code from the command line, including CLI commands, flags, and slash commands.

## Getting started

Claude Code provides two main ways to interact:

* **Interactive mode**: Run `claude` to start a REPL session
* **One-shot mode**: Use `claude -p "query"` for quick commands

```bash
# Start interactive mode
claude

# Start with an initial query
claude "explain this project"

# Run a single command and exit
claude -p "what does this function do?"

# Process piped content
cat logs.txt | claude -p "analyze these errors"
```

## CLI commands

| Command                            | Description                              | Example                                                                                          |
| :--------------------------------- | :--------------------------------------- | :----------------------------------------------------------------------------------------------- |
| `claude`                           | Start interactive REPL                   | `claude`                                                                                         |
| `claude "query"`                   | Start REPL with initial prompt           | `claude "explain this project"`                                                                  |
| `claude -p "query"`                | Run one-off query, then exit             | `claude -p "explain this function"`                                                              |
| `cat file \| claude -p "query"`    | Process piped content                    | `cat logs.txt \| claude -p "explain"`                                                            |
| `claude -c`                        | Continue most recent conversation        | `claude -c`                                                                                      |
| `claude -c -p "query"`             | Continue in print mode                   | `claude -c -p "Check for type errors"`                                                           |
| `claude -r "<session-id>" "query"` | Resume session by ID                     | `claude -r "abc123" "Finish this PR"`                                                            |
| `claude update`                    | Update to latest version                 | `claude update`                                                                                  |
| `claude mcp`                       | Configure Model Context Protocol servers | [See MCP section in tutorials](/en/docs/claude-code/tutorials#set-up-model-context-protocol-mcp) |

## CLI flags

Customize Claude Code's behavior with these command-line flags:

| Flag                             | Description                                                                                                                                              | Example                                                    |
| :------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------- |
| `--allowedTools`                 | A list of tools that should be allowed without prompting the user for permission, in addition to [settings.json files](/en/docs/claude-code/settings)    | `"Bash(git log:*)" "Bash(git diff:*)" "Write"`             |
| `--disallowedTools`              | A list of tools that should be disallowed without prompting the user for permission, in addition to [settings.json files](/en/docs/claude-code/settings) | `"Bash(git log:*)" "Bash(git diff:*)" "Write"`             |
| `--print`, `-p`                  | Print response without interactive mode (see [SDK documentation](/en/docs/claude-code/sdk) for programmatic usage details)                               | `claude -p "query"`                                        |
| `--output-format`                | Specify output format for print mode (options: `text`, `json`, `stream-json`)                                                                            | `claude -p "query" --output-format json`                   |
| `--verbose`                      | Enable verbose logging, shows full turn-by-turn output (helpful for debugging in both print and interactive modes)                                       | `claude --verbose`                                         |
| `--max-turns`                    | Limit the number of agentic turns in non-interactive mode                                                                                                | `claude -p --max-turns 3 "query"`                          |
| `--model`                        | Sets the model for the current session with an alias for the latest model (`sonnet` or `opus`) or a model's full name                                    | `claude --model claude-sonnet-4-20250514`                  |
| `--permission-prompt-tool`       | Specify an MCP tool to handle permission prompts in non-interactive mode                                                                                 | `claude -p --permission-prompt-tool mcp_auth_tool "query"` |
| `--resume`                       | Resume a specific session by ID, or by choosing in interactive mode                                                                                      | `claude --resume abc123 "query"`                           |
| `--continue`                     | Load the most recent conversation in the current directory                                                                                               | `claude --continue`                                        |
| `--dangerously-skip-permissions` | Skip permission prompts (use with caution)                                                                                                               | `claude --dangerously-skip-permissions`                    |

<Tip>
  The `--output-format json` flag is particularly useful for scripting and
  automation, allowing you to parse Claude's responses programmatically.
</Tip>

For detailed information about print mode (`-p`) including output formats,
streaming, verbose logging, and programmatic usage, see the
[SDK documentation](/en/docs/claude-code/sdk).

## Slash commands

Control Claude's behavior during an interactive session:

| Command                   | Purpose                                                               |
| :------------------------ | :-------------------------------------------------------------------- |
| `/bug`                    | Report bugs (sends conversation to Anthropic)                         |
| `/clear`                  | Clear conversation history                                            |
| `/compact [instructions]` | Compact conversation with optional focus instructions                 |
| `/config`                 | View/modify configuration                                             |
| `/cost`                   | Show token usage statistics                                           |
| `/doctor`                 | Checks the health of your Claude Code installation                    |
| `/help`                   | Get usage help                                                        |
| `/init`                   | Initialize project with CLAUDE.md guide                               |
| `/login`                  | Switch Anthropic accounts                                             |
| `/logout`                 | Sign out from your Anthropic account                                  |
| `/memory`                 | Edit CLAUDE.md memory files                                           |
| `/model`                  | Select or change the AI model                                         |
| `/permissions`            | View or update [permissions](settings#permissions)                    |
| `/pr_comments`            | View pull request comments                                            |
| `/review`                 | Request code review                                                   |
| `/status`                 | View account and system statuses                                      |
| `/terminal-setup`         | Install Shift+Enter key binding for newlines (iTerm2 and VSCode only) |
| `/vim`                    | Enter vim mode for alternating insert and command modes               |

## Special shortcuts

### Quick memory with `#`

Add memories instantly by starting your input with `#`:

```
# Always use descriptive variable names
```

You'll be prompted to select which memory file to store this in.

### Line breaks in terminal

Enter multiline commands using:

* **Quick escape**: Type `\` followed by Enter
* **Keyboard shortcut**: Option+Enter (or Shift+Enter if configured)

To set up Option+Enter in your terminal:

**For Mac Terminal.app:**

1. Open Settings → Profiles → Keyboard
2. Check "Use Option as Meta Key"

**For iTerm2 and VSCode terminal:**

1. Open Settings → Profiles → Keys
2. Under General, set Left/Right Option key to "Esc+"

**Tip for iTerm2 and VSCode users**: Run `/terminal-setup` within Claude Code to
automatically configure Shift+Enter as a more intuitive alternative.

See [terminal setup in settings](/en/docs/claude-code/settings#line-breaks) for
configuration details.

## Vim Mode

Claude Code supports a subset of Vim keybindings that can be enabled with `/vim`
or configured via `/config`.

The supported subset includes:

* Mode switching: `Esc` (to NORMAL), `i`/`I`, `a`/`A`, `o`/`O` (to INSERT)
* Navigation: `h`/`j`/`k`/`l`, `w`/`e`/`b`, `0`/`$`/`^`, `gg`/`G`
* Editing: `x`, `dw`/`de`/`db`/`dd`/`D`, `cw`/`ce`/`cb`/`cc`/`C`, `.` (repeat)


# Manage Claude's memory

> Learn how to manage Claude Code's memory across sessions with different memory locations and best practices.

Claude Code can remember your preferences across sessions, like style guidelines and common commands in your workflow.

## Determine memory type

Claude Code offers three memory locations, each serving a different purpose:

| Memory Type                | Location              | Purpose                                  | Use Case Examples                                                |
| -------------------------- | --------------------- | ---------------------------------------- | ---------------------------------------------------------------- |
| **Project memory**         | `./CLAUDE.md`         | Team-shared instructions for the project | Project architecture, coding standards, common workflows         |
| **User memory**            | `~/.claude/CLAUDE.md` | Personal preferences for all projects    | Code styling preferences, personal tooling shortcuts             |
| **Project memory (local)** | `./CLAUDE.local.md`   | Personal project-specific preferences    | *(Deprecated, see below)* Your sandbox URLs, preferred test data |

All memory files are automatically loaded into Claude Code's context when launched.

## CLAUDE.md imports

CLAUDE.md files can import additional files using `@path/to/import` syntax. The following example imports 3 files:

```
See @README for project overview and @package.json for available npm commands for this project.

# Additional Instructions
- git workflow @docs/git-instructions.md
```

Both relative and absolute paths are allowed. In particular, importing files in user's home dir is a convenient way for your team members to provide individual instructions that are not checked into the repository. Previously CLAUDE.local.md served a similar purpose, but is now deprecated in favor of imports since they work better across multiple git worktrees.

```
# Individual Preferences
- @~/.claude/my-project-instructions.md
```

To avoid potential collisions, imports are not evaluated inside markdown code spans and code blocks.

```
This code span will not be treated as an import: `@anthropic-ai/claude-code`
```

Imported files can recursively import additional files, with a max-depth of 5 hops. You can see what memory files are loaded by running `/memory` command.

## How Claude looks up memories

Claude Code reads memories recursively: starting in the cwd, Claude Code recurses up to */* and reads any CLAUDE.md or CLAUDE.local.md files it finds. This is especially convenient when working in large repositories where you run Claude Code in *foo/bar/*, and have memories in both *foo/CLAUDE.md* and *foo/bar/CLAUDE.md*.

Claude will also discover CLAUDE.md nested in subtrees under your current working directory. Instead of loading them at launch, they are only included when Claude reads files in those subtrees.

## Quickly add memories with the `#` shortcut

The fastest way to add a memory is to start your input with the `#` character:

```
# Always use descriptive variable names
```

You'll be prompted to select which memory file to store this in.

## Directly edit memories with `/memory`

Use the `/memory` slash command during a session to open any memory file in your system editor for more extensive additions or organization.

## Memory best practices

* **Be specific**: "Use 2-space indentation" is better than "Format code properly".
* **Use structure to organize**: Format each individual memory as a bullet point and group related memories under descriptive markdown headings.
* **Review periodically**: Update memories as your project evolves to ensure Claude is always using the most up to date information and context.


