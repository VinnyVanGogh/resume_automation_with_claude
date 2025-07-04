# Claude Code settings

> Learn how to configure Claude Code with global and project-level settings, themes, and environment variables.

Claude Code offers a variety of settings to configure its behavior to meet your
needs. You can configure Claude Code by running the `/config` command when using
the interactive REPL.

## Settings files

The new `settings.json` file format is our official mechanism for configuring Claude
Code through hierarchical settings:

* **User settings** are defined in `~/.claude/settings.json` and apply to all
  projects.
* **Project settings** are saved in your project directory under
  `.claude/settings.json` for shared settings, and `.claude/settings.local.json`
  for local project settings. Claude Code will configure git to ignore
  `.claude/settings.local.json` when it is created.
* For enterprise deployments of Claude Code, we also support **enterprise
  managed policy settings**. These take precedence over user and project
  settings. System administrators can deploy policies to
  `/Library/Application Support/ClaudeCode/policies.json` on macOS and
  `/etc/claude-code/policies.json` on Linux and Windows via WSL.

```JSON Example settings.json
{
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test:*)",
      "Read(~/.zshrc)"
    ],
    "deny": [
      "Bash(curl:*)"
    ]
  },
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp"
  }
}
```

### Available settings

`settings.json` supports a number of options:

| Key                   | Description                                                                                                                                                                                                    | Example                               |
| :-------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------ |
| `apiKeyHelper`        | Custom script, to be executed in `/bin/sh`, to generate an auth value. This value will generally be sent as `X-Api-Key`, `Authorization: Bearer`, and `Proxy-Authorization: Bearer` headers for model requests | `/bin/generate_temp_api_key.sh`       |
| `cleanupPeriodDays`   | How long to locally retain chat transcripts (default: 30 days)                                                                                                                                                 | `20`                                  |
| `env`                 | Environment variables that will be applied to every session                                                                                                                                                    | `{"FOO": "bar"}`                      |
| `includeCoAuthoredBy` | Whether to include the `co-authored-by Claude` byline in git commits and pull requests (default: `true`)                                                                                                       | `false`                               |
| `permissions`         | `allow` and `deny` keys are a list of [permission rules](#permissions)                                                                                                                                         | `{"allow": [ "Bash(npm run lint)" ]}` |

### Settings precedence

Settings are applied in order of precedence:

1. Enterprise policies
2. Command line arguments
3. Local project settings
4. Shared project settings
5. User settings

## Permissions

You can view & manage Claude Code's tool permissions with `/permissions`. This UI
lists all permission rules and the settings.json file they are sourced from.

* **Allow** rules will allow Claude Code to use the specified tool without
  further manual approval.
* **Deny** rules will prevent Claude Code from using the specified tool. Deny
  rules take precedence over allow rules.

Permission rules use the format: `Tool(optional-specifier)`

A rule that is just the tool name matched any use of that tool.
For example, adding `Bash` to the list of allow rules would allow Claude Code to use
the Bash tool without requiring user approval. See the list of
[tools available to Claude](security#tools-available-to-claude).

### Tool-specific permission rules

Some tools use the optional specifier for more fine-grained permission controls.
For example, an allow rule with `Bash(git diff:*)` would allow Bash commands
that start with `git diff`. The following tools support permission rules with specifiers:

#### Bash

* `Bash(npm run build)` Matches the exact Bash command `npm run build`
* `Bash(npm run test:*)` Matches Bash commands starting with `npm run test`.

<Tip>
  Claude Code is aware of shell operators (like `&&`) so a prefix match rule
  like `Bash(safe-cmd:*)` won't give it permission to run the command `safe-cmd
  && other-cmd`
</Tip>

#### Read & Edit

`Edit` rules apply to all built-in tools that edit files.
Claude will make a best-effort attempt to apply `Read` rules to
all built-in tools that read files like Grep, Glob, and LS.

Read & Edit rules both follow the
[gitignore](https://git-scm.com/docs/gitignore) specification. Patterns are
resolved relative to the directory containing `.claude/settings.json`. To
reference an absolute path, use `//`. For a path relative to your home
directory, use `~/`.

* `Edit(docs/**)` Matches edits to files in the `docs` directory of your project
* `Read(~/.zshrc)` Matches reads to your `~/.zshrc` file
* `Edit(//tmp/scratch.txt)` Matches edits to `/tmp/scratch.txt`

#### WebFetch

* `WebFetch(domain:example.com)` Matches fetch requests to example.com

#### MCP

* `mcp__puppeteer` Matches any tool provided by the `puppeteer` server (name configured in Claude Code)
* `mcp__puppeteer__puppeteer_navigate` Matches the `puppeteer_navigate` tool provided by the `puppeteer` server

## Auto-updater permission options

When Claude Code detects that it doesn't have sufficient permissions to write to
your global npm prefix directory (required for automatic updates), you'll see a
warning that points to this documentation page. For detailed solutions to
auto-updater issues, see the
[troubleshooting guide](/en/docs/claude-code/troubleshooting#auto-updater-issues).

### Recommended: Create a new user-writable npm prefix

```bash
# First, save a list of your existing global packages for later migration
npm list -g --depth=0 > ~/npm-global-packages.txt

# Create a directory for your global packages
mkdir -p ~/.npm-global

# Configure npm to use the new directory path
npm config set prefix ~/.npm-global

# Note: Replace ~/.bashrc with ~/.zshrc, ~/.profile, or other appropriate file for your shell
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc

# Apply the new PATH setting
source ~/.bashrc

# Now reinstall Claude Code in the new location
npm install -g @anthropic-ai/claude-code

# Optional: Reinstall your previous global packages in the new location
# Look at ~/npm-global-packages.txt and install packages you want to keep
# npm install -g package1 package2 package3...
```

**Why we recommend this option:**

* Avoids modifying system directory permissions
* Creates a clean, dedicated location for your global npm packages
* Follows security best practices

Since Claude Code is actively developing, we recommend setting up auto-updates
using the recommended option above.

### Disabling the auto-updater

If you prefer to disable the auto-updater instead of fixing permissions, you can
set the `DISABLE_AUTOUPDATER` [environment variable](#environment-variables) to `1`

## Optimize your terminal setup

Claude Code works best when your terminal is properly configured. Follow these
guidelines to optimize your experience.

**Supported shells**:

* Bash
* Zsh
* Fish

### Themes and appearance

Claude cannot control the theme of your terminal. That's handled by your
terminal application. You can match Claude Code's theme to your terminal during
onboarding or any time via the `/config` command

### Line breaks

You have several options for entering linebreaks into Claude Code:

* **Quick escape**: Type `\` followed by Enter to create a newline
* **Keyboard shortcut**: Press Option+Enter (Meta+Enter) with proper
  configuration

To set up Option+Enter in your terminal:

**For Mac Terminal.app:**

1. Open Settings → Profiles → Keyboard
2. Check "Use Option as Meta Key"

**For iTerm2 and VSCode terminal:**

1. Open Settings → Profiles → Keys
2. Under General, set Left/Right Option key to "Esc+"

**Tip for iTerm2 and VSCode users**: Run `/terminal-setup` within Claude Code to
automatically configure Shift+Enter as a more intuitive alternative.

### Notification setup

Never miss when Claude completes a task with proper notification configuration:

#### Terminal bell notifications

Enable sound alerts when tasks complete:

```sh
claude config set --global preferredNotifChannel terminal_bell
```

**For macOS users**: Don't forget to enable notification permissions in System
Settings → Notifications → \[Your Terminal App].

#### iTerm 2 system notifications

For iTerm 2 alerts when tasks complete:

1. Open iTerm 2 Preferences
2. Navigate to Profiles → Terminal
3. Enable "Silence bell" and Filter Alerts → "Send escape sequence-generated
   alerts"
4. Set your preferred notification delay

Note that these notifications are specific to iTerm 2 and not available in the
default macOS Terminal.

### Handling large inputs

When working with extensive code or long instructions:

* **Avoid direct pasting**: Claude Code may struggle with very long pasted
  content
* **Use file-based workflows**: Write content to a file and ask Claude to read
  it
* **Be aware of VS Code limitations**: The VS Code terminal is particularly
  prone to truncating long pastes

### Vim Mode

Claude Code supports a subset of Vim keybindings that can be enabled with `/vim`
or configured via `/config`.

The supported subset includes:

* Mode switching: `Esc` (to NORMAL), `i`/`I`, `a`/`A`, `o`/`O` (to INSERT)
* Navigation: `h`/`j`/`k`/`l`, `w`/`e`/`b`, `0`/`$`/`^`, `gg`/`G`
* Editing: `x`, `dw`/`de`/`db`/`dd`/`D`, `cw`/`ce`/`cb`/`cc`/`C`, `.` (repeat)

## Environment variables

Claude Code supports the following environment variables to control its
behavior:

<Note>
  All environment variables can also be configured in
  [`settings.json`](#available-settings). This is
  useful as a way to automatically set environment variables for each session,
  or to roll out a set of environment variables for your whole team or
  organization.
</Note>

| Variable                                   | Purpose                                                                                                                                |
| :----------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------- |
| `ANTHROPIC_API_KEY`                        | API key sent as `X-Api-Key` header, typically for the Claude SDK (for interactive usage, run `/login`)                                 |
| `ANTHROPIC_AUTH_TOKEN`                     | Custom value for the `Authorization` and `Proxy-Authorization` headers (the value you set here will be prefixed with `Bearer `)        |
| `ANTHROPIC_CUSTOM_HEADERS`                 | Custom headers you want to add to the request (in `Name: Value` format)                                                                |
| `ANTHROPIC_MODEL`                          | Name of custom model to use (see [Model Configuration](/en/docs/claude-code/bedrock-vertex-proxies#model-configuration))               |
| `ANTHROPIC_SMALL_FAST_MODEL`               | Name of [Haiku-class model for background tasks](/en/docs/claude-code/costs)                                                           |
| `BASH_DEFAULT_TIMEOUT_MS`                  | Default timeout for long-running bash commands                                                                                         |
| `BASH_MAX_TIMEOUT_MS`                      | Maximum timeout the model can set for long-running bash commands                                                                       |
| `BASH_MAX_OUTPUT_LENGTH`                   | Maximum number of characters in bash outputs before they are middle-truncated                                                          |
| `CLAUDE_CODE_API_KEY_HELPER_TTL_MS`        | Interval in milliseconds at which credentials should be refreshed (when using `apiKeyHelper`)                                          |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS`            | Set the maximum number of output tokens for most requests                                                                              |
| `CLAUDE_CODE_USE_BEDROCK`                  | Use Bedrock (see [Bedrock & Vertex](/en/docs/claude-code/bedrock-vertex-proxies))                                                      |
| `CLAUDE_CODE_USE_VERTEX`                   | Use Vertex (see [Bedrock & Vertex](/en/docs/claude-code/bedrock-vertex-proxies))                                                       |
| `CLAUDE_CODE_SKIP_BEDROCK_AUTH`            | Skip AWS authentication for Bedrock (e.g. when using an LLM gateway)                                                                   |
| `CLAUDE_CODE_SKIP_VERTEX_AUTH`             | Skip Google authentication for Vertex (e.g. when using an LLM gateway)                                                                 |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Equivalent of setting `DISABLE_AUTOUPDATER`, `DISABLE_BUG_COMMAND`, `DISABLE_ERROR_REPORTING`, and `DISABLE_TELEMETRY`                 |
| `DISABLE_AUTOUPDATER`                      | Set to `1` to disable the automatic updater                                                                                            |
| `DISABLE_BUG_COMMAND`                      | Set to `1` to disable the `/bug` command                                                                                               |
| `DISABLE_COST_WARNINGS`                    | Set to `1` to disable cost warning messages                                                                                            |
| `DISABLE_ERROR_REPORTING`                  | Set to `1` to opt out of Sentry error reporting                                                                                        |
| `DISABLE_NON_ESSENTIAL_MODEL_CALLS`        | Set to `1` to disable model calls for non-critical paths like flavor text                                                              |
| `DISABLE_TELEMETRY`                        | Set to `1` to opt out of Statsig telemetry (note that Statsig events do not include user data like code, file paths, or bash commands) |
| `HTTP_PROXY`                               | Specify HTTP proxy server for network connections                                                                                      |
| `HTTPS_PROXY`                              | Specify HTTPS proxy server for network connections                                                                                     |
| `MAX_THINKING_TOKENS`                      | Force a thinking for the model budget                                                                                                  |
| `MCP_TIMEOUT`                              | Timeout in milliseconds for MCP server startup                                                                                         |
| `MCP_TOOL_TIMEOUT`                         | Timeout in milliseconds for MCP tool execution                                                                                         |

## Configuration options

We are in the process of migration global configuration to `settings.json`.

`claude config` will be deprecated in place of [settings.json](#settings-files)

To manage your configurations, use the following commands:

* List settings: `claude config list`
* See a setting: `claude config get <key>`
* Change a setting: `claude config set <key> <value>`
* Push to a setting (for lists): `claude config add <key> <value>`
* Remove from a setting (for lists): `claude config remove <key> <value>`

By default `config` changes your project configuration. To manage your global
configuration, use the `--global` (or `-g`) flag.

### Global configuration

To set a global configuration, use `claude config set -g <key> <value>`:

| Key                     | Description                                                      | Example                                                                    |
| :---------------------- | :--------------------------------------------------------------- | :------------------------------------------------------------------------- |
| `autoUpdaterStatus`     | Enable or disable the auto-updater (default: `enabled`)          | `disabled`                                                                 |
| `preferredNotifChannel` | Where you want to receive notifications (default: `iterm2`)      | `iterm2`, `iterm2_with_bell`, `terminal_bell`, or `notifications_disabled` |
| `theme`                 | Color theme                                                      | `dark`, `light`, `light-daltonized`, or `dark-daltonized`                  |
| `verbose`               | Whether to show full bash and command outputs (default: `false`) | `true`                                                                     |


# Manage permissions and security

> Learn about Claude Code's permission system, tools access, and security safeguards.

Claude Code uses a tiered permission system to balance power and safety:

| Tool Type         | Example              | Approval Required | "Yes, don't ask again" Behavior               |
| :---------------- | :------------------- | :---------------- | :-------------------------------------------- |
| Read-only         | File reads, LS, Grep | No                | N/A                                           |
| Bash Commands     | Shell execution      | Yes               | Permanently per project directory and command |
| File Modification | Edit/write files     | Yes               | Until session end                             |

## Tools available to Claude

Claude Code has access to a set of powerful tools that help it understand and modify your codebase:

| Tool             | Description                                          | Permission Required |
| :--------------- | :--------------------------------------------------- | :------------------ |
| **Agent**        | Runs a sub-agent to handle complex, multi-step tasks | No                  |
| **Bash**         | Executes shell commands in your environment          | Yes                 |
| **Edit**         | Makes targeted edits to specific files               | Yes                 |
| **Glob**         | Finds files based on pattern matching                | No                  |
| **Grep**         | Searches for patterns in file contents               | No                  |
| **LS**           | Lists files and directories                          | No                  |
| **MultiEdit**    | Performs multiple edits on a single file atomically  | Yes                 |
| **NotebookEdit** | Modifies Jupyter notebook cells                      | Yes                 |
| **NotebookRead** | Reads and displays Jupyter notebook contents         | No                  |
| **Read**         | Reads the contents of files                          | No                  |
| **TodoRead**     | Reads the current session's task list                | No                  |
| **TodoWrite**    | Creates and manages structured task lists            | No                  |
| **WebFetch**     | Fetches content from a specified URL                 | Yes                 |
| **WebSearch**    | Performs web searches with domain filtering          | Yes                 |
| **Write**        | Creates or overwrites files                          | Yes                 |

Permission rules can be configured using `/allowed-tools` or in [permission settings](/en/docs/claude-code/settings#permissions).

## Protect against prompt injection

Prompt injection is a technique where an attacker attempts to override or manipulate an AI assistant's instructions by inserting malicious text. Claude Code includes several safeguards against these attacks:

* **Permission system**: Sensitive operations require explicit approval
* **Context-aware analysis**: Detects potentially harmful instructions by analyzing the full request
* **Input sanitization**: Prevents command injection by processing user inputs
* **Command blocklist**: Blocks risky commands that fetch arbitrary content from the web like `curl` and `wget`

**Best practices for working with untrusted content**:

1. Review suggested commands before approval
2. Avoid piping untrusted content directly to Claude
3. Verify proposed changes to critical files
4. Report suspicious behavior with `/bug`

<Warning>
  While these protections significantly reduce risk, no system is completely
  immune to all attacks. Always maintain good security practices when working
  with any AI tool.
</Warning>

## Configure network access

Claude Code requires access to:

* api.anthropic.com
* statsig.anthropic.com
* sentry.io

Allowlist these URLs when using Claude Code in containerized environments.

## Development container reference implementation

Claude Code provides a development container configuration for teams that need consistent, secure environments. This preconfigured [devcontainer setup](https://code.visualstudio.com/docs/devcontainers/containers) works seamlessly with VS Code's Remote - Containers extension and similar tools.

The container's enhanced security measures (isolation and firewall rules) allow you to run `claude --dangerously-skip-permissions` to bypass permission prompts for unattended operation. We've included a [reference implementation](https://github.com/anthropics/claude-code/tree/main/.devcontainer) that you can customize for your needs.

<Warning>
  While the devcontainer provides substantial protections, no system is
  completely immune to all attacks. Always maintain good security practices and
  monitor Claude's activities.
</Warning>

### Key features

* **Production-ready Node.js**: Built on Node.js 20 with essential development dependencies
* **Security by design**: Custom firewall restricting network access to only necessary services
* **Developer-friendly tools**: Includes git, ZSH with productivity enhancements, fzf, and more
* **Seamless VS Code integration**: Pre-configured extensions and optimized settings
* **Session persistence**: Preserves command history and configurations between container restarts
* **Works everywhere**: Compatible with macOS, Windows, and Linux development environments

### Getting started in 4 steps

1. Install VS Code and the Remote - Containers extension
2. Clone the [Claude Code reference implementation](https://github.com/anthropics/claude-code/tree/main/.devcontainer) repository
3. Open the repository in VS Code
4. When prompted, click "Reopen in Container" (or use Command Palette: Cmd+Shift+P → "Remote-Containers: Reopen in Container")

### Configuration breakdown

The devcontainer setup consists of three primary components:

* [**devcontainer.json**](https://github.com/anthropics/claude-code/blob/main/.devcontainer/devcontainer.json): Controls container settings, extensions, and volume mounts
* [**Dockerfile**](https://github.com/anthropics/claude-code/blob/main/.devcontainer/Dockerfile): Defines the container image and installed tools
* [**init-firewall.sh**](https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh): Establishes network security rules

### Security features

The container implements a multi-layered security approach with its firewall configuration:

* **Precise access control**: Restricts outbound connections to whitelisted domains only (npm registry, GitHub, Anthropic API, etc.)
* **Default-deny policy**: Blocks all other external network access
* **Startup verification**: Validates firewall rules when the container initializes
* **Isolation**: Creates a secure development environment separated from your main system

### Customization options

The devcontainer configuration is designed to be adaptable to your needs:

* Add or remove VS Code extensions based on your workflow
* Modify resource allocations for different hardware environments
* Adjust network access permissions
* Customize shell configurations and developer tooling


# Team setup

> Learn how to onboard your team to Claude Code, including user management, security, and best practices.

## User management

Setting up Claude Code requires access to Anthropic models. For teams, you can set up Claude Code access in one of three ways:

* Anthropic API via the Anthropic Console
* Amazon Bedrock
* Google Vertex AI

**To set up Claude Code access for your team via Anthropic API:**

1. Use your existing Anthropic Console account or create a new Anthropic Console account
2. You can add users through either method below:
   * Bulk invite users from within the Console (Console -> Settings -> Members -> Invite)
   * [Set up SSO](https://support.anthropic.com/en/articles/10280258-setting-up-single-sign-on-on-the-api-console)
3. When inviting users, they need one of the following roles:
   * "Claude Code" role means users can only create Claude Code API keys
   * "Developer" role means users can create any kind of API key
4. Each invited user needs to complete these steps:
   * Accept the Console invite
   * [Check system requirements](/en/docs/claude-code/getting-started#check-system-requirements)
   * [Install Claude Code](/en/docs/claude-code/getting-started#install-and-authenticate)
   * Login with Console account credentials

**To set up Claude Code access for your team via Bedrock or Vertex:**

1. Follow the [Bedrock docs](/en/docs/claude-code/bedrock-vertex-proxies#connect-to-amazon-bedrock) or [Vertex docs](/en/docs/claude-code/bedrock-vertex-proxies#connect-to-google-vertex-ai)
2. Distribute the environment variables and instructions for generating cloud credentials to your users. Read more about how to [manage configuration here](/en/docs/claude-code/settings).
3. Users can [install Claude Code](/en/docs/claude-code/getting-started#install-and-authenticate)

# How we approach security

Your code's security is paramount. Claude Code is built with security at its core. We've developed Claude Code, as we develop all of our applications and services, according to the requirements of Anthropic's comprehensive security program. You can read more about our program and request access to resources (such as our SOC 2 Type 2 report, ISO 27001 certificate, etc.) at [Anthropic Trust Center](https://trust.anthropic.com).

We've designed Claude Code to have strict read-only permissions by default, including reading files in the current working directory, and specific bash commands such as `date`, `pwd`, and `whoami`. As Claude Code requests to perform additional actions (such as to edit files, run tests, and execute bash commands), it will ask users for permission. When Claude Code requests permission, users can approve it just for that instance or allow it to run that command automatically going forward. We support fine-grained permissions so that you're able to specify exactly what the agent is allowed to do (e.g. run tests, run linter) and what it is not allowed to do (e.g. update cloud infrastructure). These permission settings can be checked into version control and distributed to all developers in your organization, as well as customized by individual developers.

For enterprise deployments of Claude Code, we also support enterprise managed policy settings. These take precedence over user and project settings, allowing system administrators to enforce security policies that users cannot override. [Learn how to configure enterprise managed policy settings](/en/docs/claude-code/settings).

We designed Claude Code to be transparent and secure. For example, we allow the model to suggest `git` commands before executing them, thus giving control to the user to grant or deny permission. This enables users and organizations to configure their own permissions directly rather than trying to monitor all possible workarounds.

Agentic systems are fundamentally different from AI chat experiences since agents are able to call tools that interact with the real world and act for longer periods of time. Agentic systems are non-deterministic and we have a number of built in protections to mitigate risks for users.

1. **Prompt injection** is when model inputs alter model behavior in an undesired way. To reduce the risk of this happening, we've added a few in-product mitigations:
   * Tools that make network requests require user approval by default
   * Web fetch uses a separate context window, to avoid injecting potentially malicious prompts into the main context window
   * The first time you run Claude Code in a new codebase, we will prompt you to verify that you trust the code
   * The first time you see new MCP servers (configured via `.mcp.json`), we will prompt you to verify that you trust the servers
   * When we detect a bash command with potential command injection (as a result of prompt injection), we will ask users to manually approve the command even if they have allowlisted it
   * If we cannot reliably match a bash command to an allowlisted permission, we fail closed and prompt users for manual approval
   * When the model generates complex bash commands, we generate natural language descriptions for users, so that they understand what the command does
2. **Prompt fatigue.** We support allowlisting frequently used safe commands per-user, per-codebase, or per-organization. We also let you switch into Accept Edits mode to accept many edits at a time, focusing permission prompts on tools that may have side effects (eg. bash)

Ultimately, Claude Code only has as many permissions as the user who is guiding it, and users are responsible for making sure the proposed code and commands are safe.

**MCP security**

Claude Code allows users to configure Model Context Protocol (MCP) servers. The list of allowed MCP servers is configured in your source code, as part of Claude Code settings engineers check into source control.

We encourage either writing your own MCP servers or using MCP servers from providers that you trust. You are able to configure Claude Code permissions for MCP servers. Anthropic does not manage or audit any MCP servers.

# Data flow and dependencies

![Claude Code data flow diagram](https://mintlify.s3.us-west-1.amazonaws.com/anthropic/images/claude-code-data-flow.png)

Claude Code is installed from [NPM](https://www.npmjs.com/package/@anthropic-ai/claude-code). Claude Code runs locally. In order to interact with the LLM, Claude Code sends data over the network. This data includes all user prompts and model outputs. The data is encrypted in transit via TLS and is not encrypted at rest. Claude Code is compatible with most popular VPNs and LLM proxies.

Claude Code is built on Anthropic's APIs. For details regarding our API's security controls, including our API logging procedures, please refer to compliance artifacts offered in the [Anthropic Trust Center](https://trust.anthropic.com).

Claude Code supports authentication via Claude.ai credentials, Anthropic API credentials, Bedrock Auth, and Vertex Auth. On MacOS, the API keys, OAuth tokens, and other credentials are stored on encrypted macOS Keychain. Alternately, the setting [apiKeyHelper](/en/docs/claude-code/settings#available-settings) can be set to a shell script which returns an API key. By default, this helper is called after 5 minutes or on HTTP 401 response; specifying environment variable `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` defines a custom refresh interval.

Claude Code connects from users' machines to the Statsig service to log operational metrics such as latency, reliability, and usage patterns. This logging does not include any code or file paths. Data is encrypted in transit using TLS and at rest using 256-bit AES encryption. Read more in the [Statsig security documentation](https://www.statsig.com/trust/security). To opt out of Statsig telemetry, set the `DISABLE_TELEMETRY` environment variable.

Claude Code connects from users' machines to Sentry for operational error logging. The data is encrypted in transit using TLS and at rest using 256-bit AES encryption. Read more in the [Sentry security documentation](https://sentry.io/security/). To opt out of error logging, set the `DISABLE_ERROR_REPORTING` environment variable.

When users run the `/bug` command, a copy of their full conversation history including code is sent to Anthropic. The data is encrypted in transit and at rest. Optionally, a Github issue is created in our public repository. To opt out of bug reporting, set the `DISABLE_BUG_COMMAND` environment variable.

By default, we disable all non-essential traffic (including error reporting, telemetry, and bug reporting functionality) when using Bedrock or Vertex. You can also opt out of all of these at once by setting the `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` environment variable. Here are the full default behaviors:

| Service                            | Anthropic API                                            | Vertex API                                            | Bedrock API                                            |
| ---------------------------------- | -------------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------ |
| **Statsig (Metrics)**              | Default on.<br />`DISABLE_TELEMETRY=1` to disable.       | Default off.<br />`CLAUDE_CODE_USE_VERTEX` must be 1. | Default off.<br />`CLAUDE_CODE_USE_BEDROCK` must be 1. |
| **Sentry (Errors)**                | Default on.<br />`DISABLE_ERROR_REPORTING=1` to disable. | Default off.<br />`CLAUDE_CODE_USE_VERTEX` must be 1. | Default off.<br />`CLAUDE_CODE_USE_BEDROCK` must be 1. |
| **Anthropic API (`/bug` reports)** | Default on.<br />`DISABLE_BUG_COMMAND=1` to disable.     | Default off.<br />`CLAUDE_CODE_USE_VERTEX` must be 1. | Default off.<br />`CLAUDE_CODE_USE_BEDROCK` must be 1. |

All environment variables can be checked into `settings.json` ([read more](/en/docs/claude-code/settings)).

Claude Code stores conversation history locally, in plain text, so that users can resume prior conversations. Conversations are retained for 30 days, and they can delete them earlier by running `rm -r ~/.claude/projects/*/`. The retention period can be customized using the `cleanupPeriodDays` setting; like other settings, you can check this setting into your repository, set it globally so that it applies across all repositories, or manage it for all employees using your enterprise policy. Uninstalling `claude` does not delete history.

# Managing costs

When using Anthropic API, you can limit the total Claude Code workspace spend. To configure, [follow these instructions](https://support.anthropic.com/en/articles/9796807-creating-and-managing-workspaces). Admins can view cost and usage reporting by [following these instructions](https://support.anthropic.com/en/articles/9534590-cost-and-usage-reporting-in-console).

On Bedrock and Vertex, Claude Code does not send metrics from your cloud. In order to get cost metrics, several large enterprises reported using [LiteLLM](/en/docs/claude-code/bedrock-vertex-proxies#litellm), which is an open-source tool that helps companies [track spend by key](https://docs.litellm.ai/docs/proxy/virtual_keys#tracking-spend). This project is unaffiliated with Anthropic and we have not audited its security.

For team usage, Claude Code charges by API token consumption. On average, Claude Code costs \~\$50-60/developer per month with Sonnet 3.7 though there is large variance depending on how many instances users are running and whether they're using it in automation.

# Best practices for organizations

1. We strongly recommend investing in documentation so that Claude Code understands your codebase. Many organizations make a `CLAUDE.md` file (which we also refer to as memory) in the root of the repository that contains the system architecture, how to run tests and other common commands, and best practices for contributing to the codebase. This file is typically checked into source control so that all users can benefit from it. [Learn more](/en/docs/claude-code/memory).
2. If you have a custom development environment, we find that creating a "one click" way to install Claude Code is key to growing adoption across an organization.
3. Encourage new users to try Claude Code for codebase Q\&A, or on smaller bug fixes or feature requests. Ask Claude Code to make a plan. Check Claude's suggestions and give feedback if it's off-track. Over time, as users understand this new paradigm better, then they'll be more effective at letting Claude Code run more agentically.
4. Security teams can configure managed permissions for what Claude Code is and is not allowed to do, which cannot be overwritten by local configuration. [Learn more](/en/docs/claude-code/overview).
5. MCP is a great way to give Claude Code more information, such as connecting to ticket management systems or error logs. We recommend that one central team configures MCP servers and checks a `.mcp.json` configuration into the codebase so that all users benefit. [Learn more](/en/docs/claude-code/tutorials#set-up-model-context-protocol-mcp).

At Anthropic, we trust Claude Code to power development across every Anthropic codebase. We hope you enjoy using Claude Code as much as we do!

# FAQ

**Q: Does my existing commercial agreement apply?**

Whether you're using Anthropic's API directly (1P) or accessing it through AWS Bedrock or Google Vertex (3P), your existing commercial agreement will apply to Claude Code usage, unless we've mutually agreed otherwise.

**Q: Does Claude Code train on user content?**

By default, Anthropic does not train generative models using code or prompts that are sent to Claude Code.

If you explicitly opt in to methods to provide us with materials to train on, such as via the [Development Partner Program](https://support.anthropic.com/en/articles/11174108-about-the-development-partner-program), we may use those materials provided to train our models. An organization admin can expressly opt-in to the Development Partner Program for their organization. Note that this program is available only for Anthropic first-party API, and not for Bedrock or Vertex users.

More details can be found in our [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms) and [Privacy Policy](https://www.anthropic.com/legal/privacy).

**Q: Can I use a zero data retention key?**

Yes, you can use an API key from a zero data retention organization. When doing so, Claude Code will not retain your chat transcripts on our servers. Users' local Claude Code clients may store sessions locally for up to 30 days so that users can resume them. This behavior is configurable.

**Q: Where can I learn more about trust and safety at Anthropic?**

You can find more information in the [Anthropic Trust Center](https://trust.anthropic.com) and [Transparency Hub](https://www.anthropic.com/transparency).

**Q: How can I report security vulnerabilities?**

Anthropic manages our security program through HackerOne. [Use this form to report vulnerabilities](https://hackerone.com/anthropic-vdp/reports/new?type=team\&report_type=vulnerability).


# Monitoring usage

> Monitor Claude Code usage with OpenTelemetry metrics

<Note>
  OpenTelemetry support is currently in beta and details are subject to change.
</Note>

# OpenTelemetry in Claude Code

Claude Code supports OpenTelemetry (OTel) metrics and events for monitoring and observability. This document explains how to enable and configure OTel for Claude Code.

All metrics are time series data exported via OpenTelemetry's standard metrics protocol, and events are exported via OpenTelemetry's logs/events protocol. It is the user's responsibility to ensure their metrics and logs backends are properly configured and that the aggregation granularity meets their monitoring requirements.

## Quick Start

Configure OpenTelemetry using environment variables:

```bash
# 1. Enable telemetry
export CLAUDE_CODE_ENABLE_TELEMETRY=1

# 2. Choose exporters (both are optional - configure only what you need)
export OTEL_METRICS_EXPORTER=otlp       # Options: otlp, prometheus, console
export OTEL_LOGS_EXPORTER=otlp          # Options: otlp, console

# 3. Configure OTLP endpoint (for OTLP exporter)
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# 4. Set authentication (if required)
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer your-token"

# 5. For debugging: reduce export intervals
export OTEL_METRIC_EXPORT_INTERVAL=10000  # 10 seconds (default: 60000ms)
export OTEL_LOGS_EXPORT_INTERVAL=5000     # 5 seconds (default: 5000ms)

# 6. Run Claude Code
claude
```

<Note>
  The default export intervals are 60 seconds for metrics and 5 seconds for logs. During setup, you may want to use shorter intervals for debugging purposes. Remember to reset these for production use.
</Note>

For full configuration options, see the [OpenTelemetry specification](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/exporter.md#configuration-options).

## Administrator Configuration

Administrators can configure OpenTelemetry settings for all users through the managed settings file. This allows for centralized control of telemetry settings across an organization. See the [settings precedence](/en/docs/claude-code/settings#settings-precedence) for more information about how settings are applied.

The managed settings file is located at:

* macOS: `/Library/Application Support/ClaudeCode/managed-settings.json`
* Linux: `/etc/claude-code/managed-settings.json`

Example managed settings configuration:

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector.company.com:4317",
    "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Bearer company-token"
  }
}
```

<Note>
  Managed settings can be distributed via MDM (Mobile Device Management) or other device management solutions. Environment variables defined in the managed settings file have high precedence and cannot be overridden by users.
</Note>

## Configuration Details

### Common Configuration Variables

| Environment Variable                            | Description                                               | Example Values                       |
| ----------------------------------------------- | --------------------------------------------------------- | ------------------------------------ |
| `CLAUDE_CODE_ENABLE_TELEMETRY`                  | Enables telemetry collection (required)                   | `1`                                  |
| `OTEL_METRICS_EXPORTER`                         | Metrics exporter type(s) (comma-separated)                | `console`, `otlp`, `prometheus`      |
| `OTEL_LOGS_EXPORTER`                            | Logs/events exporter type(s) (comma-separated)            | `console`, `otlp`                    |
| `OTEL_EXPORTER_OTLP_PROTOCOL`                   | Protocol for OTLP exporter (all signals)                  | `grpc`, `http/json`, `http/protobuf` |
| `OTEL_EXPORTER_OTLP_ENDPOINT`                   | OTLP collector endpoint (all signals)                     | `http://localhost:4317`              |
| `OTEL_EXPORTER_OTLP_METRICS_PROTOCOL`           | Protocol for metrics (overrides general)                  | `grpc`, `http/json`, `http/protobuf` |
| `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`           | OTLP metrics endpoint (overrides general)                 | `http://localhost:4318/v1/metrics`   |
| `OTEL_EXPORTER_OTLP_LOGS_PROTOCOL`              | Protocol for logs (overrides general)                     | `grpc`, `http/json`, `http/protobuf` |
| `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT`              | OTLP logs endpoint (overrides general)                    | `http://localhost:4318/v1/logs`      |
| `OTEL_EXPORTER_OTLP_HEADERS`                    | Authentication headers for OTLP                           | `Authorization=Bearer token`         |
| `OTEL_EXPORTER_OTLP_METRICS_CLIENT_KEY`         | Client key for mTLS authentication                        | Path to client key file              |
| `OTEL_EXPORTER_OTLP_METRICS_CLIENT_CERTIFICATE` | Client certificate for mTLS authentication                | Path to client cert file             |
| `OTEL_METRIC_EXPORT_INTERVAL`                   | Export interval in milliseconds (default: 60000)          | `5000`, `60000`                      |
| `OTEL_LOGS_EXPORT_INTERVAL`                     | Logs export interval in milliseconds (default: 5000)      | `1000`, `10000`                      |
| `OTEL_LOG_USER_PROMPTS`                         | Enable logging of user prompt content (default: disabled) | `1` to enable                        |

### Metrics Cardinality Control

The following environment variables control which attributes are included in metrics to manage cardinality:

| Environment Variable                | Description                                     | Default Value | Example to Disable |
| ----------------------------------- | ----------------------------------------------- | ------------- | ------------------ |
| `OTEL_METRICS_INCLUDE_SESSION_ID`   | Include session.id attribute in metrics         | `true`        | `false`            |
| `OTEL_METRICS_INCLUDE_VERSION`      | Include app.version attribute in metrics        | `false`       | `true`             |
| `OTEL_METRICS_INCLUDE_ACCOUNT_UUID` | Include user.account\_uuid attribute in metrics | `true`        | `false`            |

These variables help control the cardinality of metrics, which affects storage requirements and query performance in your metrics backend. Lower cardinality generally means better performance and lower storage costs but less granular data for analysis.

### Example Configurations

```bash
# Console debugging (1-second intervals)
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=console
export OTEL_METRIC_EXPORT_INTERVAL=1000

# OTLP/gRPC
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Prometheus
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=prometheus

# Multiple exporters
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=console,otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=http/json

# Different endpoints/backends for metrics and logs
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_LOGS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_METRICS_PROTOCOL=http/protobuf
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=http://metrics.company.com:4318
export OTEL_EXPORTER_OTLP_LOGS_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=http://logs.company.com:4317

# Metrics only (no events/logs)
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Events/logs only (no metrics)
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_LOGS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

## Available Metrics and Events

### Metrics

Claude Code exports the following metrics:

| Metric Name                           | Description                                     | Unit   |
| ------------------------------------- | ----------------------------------------------- | ------ |
| `claude_code.session.count`           | Count of CLI sessions started                   | count  |
| `claude_code.lines_of_code.count`     | Count of lines of code modified                 | count  |
| `claude_code.pull_request.count`      | Number of pull requests created                 | count  |
| `claude_code.commit.count`            | Number of git commits created                   | count  |
| `claude_code.cost.usage`              | Cost of the Claude Code session                 | USD    |
| `claude_code.token.usage`             | Number of tokens used                           | tokens |
| `claude_code.code_edit_tool.decision` | Count of code editing tool permission decisions | count  |

### Metric Details

All metrics share these standard attributes:

* `session.id`: Unique session identifier (controlled by `OTEL_METRICS_INCLUDE_SESSION_ID`)
* `app.version`: Current Claude Code version (controlled by `OTEL_METRICS_INCLUDE_VERSION`)
* `organization.id`: Organization UUID (when authenticated)
* `user.account_uuid`: Account UUID (when authenticated, controlled by `OTEL_METRICS_INCLUDE_ACCOUNT_UUID`)

#### 1. Session Counter

Emitted at the start of each session.

#### 2. Lines of Code Counter

Emitted when code is added or removed.

* Additional attribute: `type` (`"added"` or `"removed"`)

#### 3. Pull Request Counter

Emitted when creating pull requests via Claude Code.

#### 4. Commit Counter

Emitted when creating git commits via Claude Code.

#### 5. Cost Counter

Emitted after each API request.

* Additional attribute: `model`

#### 6. Token Counter

Emitted after each API request.

* Additional attributes: `type` (`"input"`, `"output"`, `"cacheRead"`, `"cacheCreation"`) and `model`

#### 7. Code Edit Tool Decision Counter

Emitted when user accepts or rejects Edit, MultiEdit, Write, or NotebookEdit tool usage.

* Additional attributes: `tool` (tool name: `"Edit"`, `"MultiEdit"`, `"Write"`, `"NotebookEdit"`) and `decision` (`"accept"`, `"reject"`)

### Events

Claude Code exports the following events via OpenTelemetry logs/events (when `OTEL_LOGS_EXPORTER` is configured):

#### 1. User Prompt Event

* **Event Name**: `claude_code.user_prompt`
* **Description**: Logged when a user submits a prompt
* **Attributes**:
  * All standard attributes (user.id, session.id, etc.)
  * `event.name`: `"user_prompt"`
  * `event.timestamp`: ISO 8601 timestamp
  * `prompt_length`: Length of the prompt
  * `prompt`: Prompt content (redacted by default, enable with `OTEL_LOG_USER_PROMPTS=1`)

#### 2. Tool Result Event

* **Event Name**: `claude_code.tool_result`
* **Description**: Logged when a tool completes execution
* **Attributes**:
  * All standard attributes
  * `event.name`: `"tool_result"`
  * `event.timestamp`: ISO 8601 timestamp
  * `name`: Name of the tool
  * `success`: `"true"` or `"false"`
  * `duration_ms`: Execution time in milliseconds
  * `error`: Error message (if failed)

#### 3. API Request Event

* **Event Name**: `claude_code.api_request`
* **Description**: Logged for each API request to Claude
* **Attributes**:
  * All standard attributes
  * `event.name`: `"api_request"`
  * `event.timestamp`: ISO 8601 timestamp
  * `model`: Model used (e.g., "claude-3-5-sonnet-20241022")
  * `cost_usd`: Estimated cost in USD
  * `duration_ms`: Request duration in milliseconds
  * `input_tokens`: Number of input tokens
  * `output_tokens`: Number of output tokens
  * `cache_read_tokens`: Number of tokens read from cache
  * `cache_creation_tokens`: Number of tokens used for cache creation

#### 4. API Error Event

* **Event Name**: `claude_code.api_error`
* **Description**: Logged when an API request to Claude fails
* **Attributes**:
  * All standard attributes
  * `event.name`: `"api_error"`
  * `event.timestamp`: ISO 8601 timestamp
  * `model`: Model used (e.g., "claude-3-5-sonnet-20241022")
  * `error`: Error message
  * `status_code`: HTTP status code (if applicable)
  * `duration_ms`: Request duration in milliseconds
  * `attempt`: Attempt number (for retried requests)

#### 5. Tool Decision Event

* **Event Name**: `claude_code.tool_decision`
* **Description**: Logged when a tool permission decision is made (accept/reject)
* **Attributes**:
  * All standard attributes
  * `event.name`: `"tool_decision"`
  * `event.timestamp`: ISO 8601 timestamp
  * `tool_name`: Name of the tool (e.g., "Read", "Edit", "MultiEdit", "Write", "NotebookEdit", etc.)
  * `decision`: Either `"accept"` or `"reject"`
  * `source`: Decision source - `"config"`, `"user_permanent"`, `"user_temporary"`, `"user_abort"`, or `"user_reject"`

## Interpreting Metrics and Events Data

The metrics exported by Claude Code provide valuable insights into usage patterns and productivity. Here are some common visualizations and analyses you can create:

### Usage Monitoring

| Metric                                                        | Analysis Opportunity                                      |
| ------------------------------------------------------------- | --------------------------------------------------------- |
| `claude_code.token.usage`                                     | Break down by `type` (input/output), user, team, or model |
| `claude_code.session.count`                                   | Track adoption and engagement over time                   |
| `claude_code.lines_of_code.count`                             | Measure productivity by tracking code additions/removals  |
| `claude_code.commit.count` & `claude_code.pull_request.count` | Understand impact on development workflows                |

### Cost Monitoring

The `claude_code.cost.usage` metric helps with:

* Tracking usage trends across teams or individuals
* Identifying high-usage sessions for optimization

<Note>
  Cost metrics are approximations. For official billing data, refer to your API provider (Anthropic Console, AWS Bedrock, or Google Cloud Vertex).
</Note>

### Alerting and Segmentation

Common alerts to consider:

* Cost spikes
* Unusual token consumption
* High session volume from specific users

All metrics can be segmented by `user.account_uuid`, `organization.id`, `session.id`, `model`, and `app.version`.

### Event Analysis

The event data provides detailed insights into Claude Code interactions:

1. **Tool Usage Patterns**: Analyze tool result events to identify:
   * Most frequently used tools
   * Tool success rates
   * Average tool execution times
   * Error patterns by tool type

2. **Performance Monitoring**: Track API request durations and tool execution times to identify performance bottlenecks.

## Backend Considerations

Your choice of metrics and logs backends will determine the types of analyses you can perform:

### For Metrics:

* **Time series databases (e.g., Prometheus)**: Rate calculations, aggregated metrics
* **Columnar stores (e.g., ClickHouse)**: Complex queries, unique user analysis
* **Full-featured observability platforms (e.g., Honeycomb, Datadog)**: Advanced querying, visualization, alerting

### For Events/Logs:

* **Log aggregation systems (e.g., Elasticsearch, Loki)**: Full-text search, log analysis
* **Columnar stores (e.g., ClickHouse)**: Structured event analysis
* **Full-featured observability platforms (e.g., Honeycomb, Datadog)**: Correlation between metrics and events

For organizations requiring Daily/Weekly/Monthly Active User (DAU/WAU/MAU) metrics, consider backends that support efficient unique value queries.

## Service Information

All metrics are exported with:

* Service Name: `claude-code`
* Service Version: Current Claude Code version
* Meter Name: `com.anthropic.claude_code`

## Security/Privacy Considerations

* Telemetry is opt-in and requires explicit configuration
* Sensitive information like API keys or file contents are never included in metrics or events
* User prompt content is redacted by default - only prompt length is recorded. To enable user prompt logging, set `OTEL_LOG_USER_PROMPTS=1`


# Manage costs effectively

> Learn how to track and optimize token usage and costs when using Claude Code.

Claude Code consumes tokens for each interaction. The average cost is \$6 per developer per day, with daily costs remaining below \$12 for 90% of users.

## Track your costs

* Use `/cost` to see current session usage
* **Anthropic Console users**:
  * Check [historical usage](https://support.anthropic.com/en/articles/9534590-cost-and-usage-reporting-in-console) in the Anthropic Console (requires Admin or Billing role)
  * Set [workspace spend limits](https://support.anthropic.com/en/articles/9796807-creating-and-managing-workspaces) for the Claude Code workspace (requires Admin role)
* **Pro and Max plan users**: Usage is included in your subscription

## Reduce token usage

* **Compact conversations:**

  * Claude uses auto-compact by default when context exceeds 95% capacity
  * Toggle auto-compact: Run `/config` and navigate to "Auto-compact enabled"
  * Use `/compact` manually when context gets large
  * Add custom instructions: `/compact Focus on code samples and API usage`
  * Customize compaction by adding to CLAUDE.md:

    ```markdown
    # Summary instructions

    When you are using compact, please focus on test output and code changes
    ```

* **Write specific queries:** Avoid vague requests that trigger unnecessary scanning

* **Break down complex tasks:** Split large tasks into focused interactions

* **Clear history between tasks:** Use `/clear` to reset context

Costs can vary significantly based on:

* Size of codebase being analyzed
* Complexity of queries
* Number of files being searched or modified
* Length of conversation history
* Frequency of compacting conversations
* Background processes (haiku generation, conversation summarization)

## Background token usage

Claude Code uses tokens for some background functionality even when idle:

* **Haiku generation**: Small creative messages that appear while you type (approximately 1 cent per day)
* **Conversation summarization**: Background jobs that summarize previous conversations for the `claude --resume` feature
* **Command processing**: Some commands like `/cost` may generate requests to check status

These background processes consume a small amount of tokens (typically under \$0.04 per session) even without active interaction.

<Note>
  For team deployments, we recommend starting with a small pilot group to
  establish usage patterns before wider rollout.
</Note>


# Troubleshooting

> Solutions for common issues with Claude Code installation and usage.

## Common installation issues

### Linux permission issues

When installing Claude Code with npm, you may encounter permission errors if your npm global prefix is not user writable (eg. `/usr`, or `/usr/local`).

#### Recommended solution: Create a user-writable npm prefix

The safest approach is to configure npm to use a directory within your home folder:

```bash
# First, save a list of your existing global packages for later migration
npm list -g --depth=0 > ~/npm-global-packages.txt

# Create a directory for your global packages
mkdir -p ~/.npm-global

# Configure npm to use the new directory path
npm config set prefix ~/.npm-global

# Note: Replace ~/.bashrc with ~/.zshrc, ~/.profile, or other appropriate file for your shell
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc

# Apply the new PATH setting
source ~/.bashrc

# Now reinstall Claude Code in the new location
npm install -g @anthropic-ai/claude-code

# Optional: Reinstall your previous global packages in the new location
# Look at ~/npm-global-packages.txt and install packages you want to keep
```

This solution is recommended because it:

* Avoids modifying system directory permissions
* Creates a clean, dedicated location for your global npm packages
* Follows security best practices

#### System Recovery: If you have run commands that change ownership and permissions of system files or similar

If you've already run a command that changed system directory permissions (such as `sudo chown -R $USER:$(id -gn) /usr && sudo chmod -R u+w /usr`) and your system is now broken (for example, if you see `sudo: /usr/bin/sudo must be owned by uid 0 and have the setuid bit set`), you'll need to perform recovery steps.

##### Ubuntu/Debian Recovery Method:

1. While rebooting, hold **SHIFT** to access the GRUB menu

2. Select "Advanced options for Ubuntu/Debian"

3. Choose the recovery mode option

4. Select "Drop to root shell prompt"

5. Remount the filesystem as writable:
   ```bash
   mount -o remount,rw /
   ```

6. Fix permissions:

   ```bash
   # Restore root ownership
   chown -R root:root /usr
   chmod -R 755 /usr

   # Ensure /usr/local is owned by your user for npm packages
   chown -R YOUR_USERNAME:YOUR_USERNAME /usr/local

   # Set setuid bit for critical binaries
   chmod u+s /usr/bin/sudo
   chmod 4755 /usr/bin/sudo
   chmod u+s /usr/bin/su
   chmod u+s /usr/bin/passwd
   chmod u+s /usr/bin/newgrp
   chmod u+s /usr/bin/gpasswd
   chmod u+s /usr/bin/chsh
   chmod u+s /usr/bin/chfn

   # Fix sudo configuration
   chown root:root /usr/libexec/sudo/sudoers.so
   chmod 4755 /usr/libexec/sudo/sudoers.so
   chown root:root /etc/sudo.conf
   chmod 644 /etc/sudo.conf
   ```

7. Reinstall affected packages (optional but recommended):

   ```bash
   # Save list of installed packages
   dpkg --get-selections > /tmp/installed_packages.txt

   # Reinstall them
   awk '{print $1}' /tmp/installed_packages.txt | xargs -r apt-get install --reinstall -y
   ```

8. Reboot:
   ```bash
   reboot
   ```

##### Alternative Live USB Recovery Method:

If the recovery mode doesn't work, you can use a live USB:

1. Boot from a live USB (Ubuntu, Debian, or any Linux distribution)

2. Find your system partition:
   ```bash
   lsblk
   ```

3. Mount your system partition:
   ```bash
   sudo mount /dev/sdXY /mnt  # replace sdXY with your actual system partition
   ```

4. If you have a separate boot partition, mount it too:
   ```bash
   sudo mount /dev/sdXZ /mnt/boot  # if needed
   ```

5. Chroot into your system:

   ```bash
   # For Ubuntu/Debian:
   sudo chroot /mnt

   # For Arch-based systems:
   sudo arch-chroot /mnt
   ```

6. Follow steps 6-8 from the Ubuntu/Debian recovery method above

After restoring your system, follow the recommended solution above to set up a user-writable npm prefix.

## Auto-updater issues

If Claude Code can't update automatically, it may be due to permission issues with your npm global prefix directory. Follow the [recommended solution](#recommended-solution-create-a-user-writable-npm-prefix) above to fix this.

If you prefer to disable the auto-updater instead, you can use:
If you prefer to disable the auto-updater instead , you can
set the `DISABLE_AUTOUPDATER` [environment variable](settings#environment-variables) to `1`

## Permissions and authentication

### Repeated permission prompts

If you find yourself repeatedly approving the same commands, you can allow specific tools
to run without approval using the `/permissions` command. See [Permissions docs](settings#permissions).

### Authentication issues

If you're experiencing authentication problems:

1. Run `/logout` to sign out completely
2. Close Claude Code
3. Restart with `claude` and complete the authentication process again

If problems persist, try:

```bash
rm -rf ~/.config/claude-code/auth.json
claude
```

This removes your stored authentication information and forces a clean login.

## Performance and stability

### High CPU or memory usage

Claude Code is designed to work with most development environments, but may consume significant resources when processing large codebases. If you're experiencing performance issues:

1. Use `/compact` regularly to reduce context size
2. Close and restart Claude Code between major tasks
3. Consider adding large build directories to your `.gitignore` file

### Command hangs or freezes

If Claude Code seems unresponsive:

1. Press Ctrl+C to attempt to cancel the current operation
2. If unresponsive, you may need to close the terminal and restart

### ESC key not working in JetBrains (IntelliJ, PyCharm, etc.) terminals

If you're using Claude Code in JetBrains terminals and the ESC key doesn't interrupt the agent as expected, this is likely due to a keybinding clash with JetBrains' default shortcuts.

To fix this issue:

1. Go to Settings → Tools → Terminal
2. Click the "Configure terminal keybindings" hyperlink next to "Override IDE Shortcuts"
3. Within the terminal keybindings, scroll down to "Switch focus to Editor" and delete that shortcut

This will allow the ESC key to properly function for canceling Claude Code operations instead of being captured by PyCharm's "Switch focus to Editor" action.

## Getting more help

If you're experiencing issues not covered here:

1. Use the `/bug` command within Claude Code to report problems directly to Anthropic
2. Check the [GitHub repository](https://github.com/anthropics/claude-code) for known issues
3. Run `/doctor` to check the health of your Claude Code installation
