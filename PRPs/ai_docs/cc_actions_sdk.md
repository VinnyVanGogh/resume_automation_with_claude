# GitHub Actions

> Integrate Claude Code with your GitHub workflows for automated code review, PR management, and issue triage.

Claude Code GitHub Actions brings AI-powered automation to your GitHub workflow. With a simple `@claude` mention in any PR or issue, Claude can analyze your code, create pull requests, implement features, and fix bugs - all while following your project's standards.

<Info>
  Claude Code GitHub Actions is currently in beta. Features and functionality may evolve as we refine the experience.
</Info>

<Note>
  Claude Code GitHub Actions is built on top of the [Claude Code SDK](/en/docs/claude-code/sdk), which enables programmatic integration of Claude Code into your applications. You can use the SDK to build custom automation workflows beyond GitHub Actions.
</Note>

## Why use Claude Code GitHub Actions?

* **Instant PR creation**: Describe what you need, and Claude creates a complete PR with all necessary changes
* **Automated code implementation**: Turn issues into working code with a single command
* **Follows your standards**: Claude respects your `CLAUDE.md` guidelines and existing code patterns
* **Simple setup**: Get started in minutes with our installer and API key
* **Secure by default**: Your code stays on Github's runners

## What can Claude do?

Claude Code provides powerful GitHub Actions that transform how you work with code:

### Claude Code Action

This GitHub Action allows you to run Claude Code within your GitHub Actions workflows. You can use this to build any custom workflow on top of Claude Code.

[View repository →](https://github.com/anthropics/claude-code-action)

### Claude Code Action (Base)

The foundation for building custom GitHub workflows with Claude. This extensible framework gives you full access to Claude's capabilities for creating tailored automation.

[View repository →](https://github.com/anthropics/claude-code-base-action)

## Quick start

The easiest way to set up this action is through Claude Code in the terminal. Just open claude and run `/install-github-app`.

This command will guide you through setting up the GitHub app and required secrets.

<Note>
  * You must be a repository admin to install the GitHub app and add secrets
  * This quickstart method is only available for direct Anthropic API users. If you're using AWS Bedrock or Google Vertex AI, please see the [Using with AWS Bedrock & Google Vertex AI](#using-with-aws-bedrock-%26-google-vertex-ai) section.
</Note>

### If the setup script fails

If the `/install-github-app` command fails or you prefer manual setup, please follow these manual setup instructions:

1. **Install the Claude GitHub app** to your repository: [https://github.com/apps/claude](https://github.com/apps/claude)
2. **Add ANTHROPIC\_API\_KEY** to your repository secrets ([Learn how to use secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions))
3. **Copy the workflow file** from [examples/claude.yml](https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml) into your repository's `.github/workflows/`

<Steps>
  <Step title="Test the action">
    After completing either the quickstart or manual setup, test the action by tagging `@claude` in an issue or PR comment!
  </Step>
</Steps>

## Example use cases

Claude Code GitHub Actions can help you with a variety of tasks. For complete working examples, see the [examples directory](https://github.com/anthropics/claude-code-action/tree/main/examples).

### Turn issues into PRs

```yaml
# In an issue comment:
@claude implement this feature based on the issue description
```

Claude will analyze the issue, write the code, and create a PR for review.

### Get implementation help

```yaml
# In a PR comment:
@claude how should I implement user authentication for this endpoint?
```

Claude will analyze your code and provide specific implementation guidance.

### Fix bugs quickly

```yaml
# In an issue:
@claude fix the TypeError in the user dashboard component
```

Claude will locate the bug, implement a fix, and create a PR.

## Best practices

### CLAUDE.md configuration

Create a `CLAUDE.md` file in your repository root to define code style guidelines, review criteria, project-specific rules, and preferred patterns. This file guides Claude's understanding of your project standards.

### Security considerations

**⚠️ IMPORTANT: Never commit API keys directly to your repository!**

Always use GitHub Secrets for API keys:

* Add your API key as a repository secret named `ANTHROPIC_API_KEY`
* Reference it in workflows: `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}`
* Limit action permissions to only what's necessary
* Review Claude's suggestions before merging

Always use GitHub Secrets (e.g., `${{ secrets.ANTHROPIC_API_KEY }}`) rather than hardcoding API keys directly in your workflow files.

### Optimizing performance

Use issue templates to provide context, keep your `CLAUDE.md` concise and focused, and configure appropriate timeouts for your workflows.

### CI costs

When using Claude Code GitHub Actions, be aware of the associated costs:

**GitHub Actions costs:**

* Claude Code runs on GitHub-hosted runners, which consume your GitHub Actions minutes
* See [GitHub's billing documentation](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions) for detailed pricing and minute limits

**API costs:**

* Each Claude interaction consumes API tokens based on the length of prompts and responses
* Token usage varies by task complexity and codebase size
* See [Claude's pricing page](https://www.anthropic.com/api) for current token rates

**Cost optimization tips:**

* Use specific `@claude` commands to reduce unnecessary API calls
* Configure appropriate `max_turns` limits to prevent excessive iterations
* Set reasonable `timeout_minutes` to avoid runaway workflows
* Consider using GitHub's concurrency controls to limit parallel runs

## Configuration examples

For ready-to-use workflow configurations for different use cases, including:

* Basic workflow setup for issue and PR comments
* Automated code reviews on pull requests
* Custom implementations for specific needs

Visit the [examples directory](https://github.com/anthropics/claude-code-action/tree/main/examples) in the Claude Code Action repository.

<Tip>
  The examples repository includes complete, tested workflows that you can copy directly into your `.github/workflows/` directory.
</Tip>

## Using with AWS Bedrock & Google Vertex AI

For enterprise environments, you can use Claude Code GitHub Actions with your own cloud infrastructure. This approach gives you control over data residency and billing while maintaining the same functionality.

### Prerequisites

Before setting up Claude Code GitHub Actions with cloud providers, you need:

#### For Google Cloud Vertex AI:

1. A Google Cloud Project with Vertex AI enabled
2. Workload Identity Federation configured for GitHub Actions
3. A service account with the required permissions
4. A GitHub App (recommended) or use the default GITHUB\_TOKEN

#### For AWS Bedrock:

1. An AWS account with Amazon Bedrock enabled
2. GitHub OIDC Identity Provider configured in AWS
3. An IAM role with Bedrock permissions
4. A GitHub App (recommended) or use the default GITHUB\_TOKEN

<Steps>
  <Step title="Create a custom GitHub App (Recommended for 3P Providers)">
    For best control and security when using 3P providers like Vertex AI or Bedrock, we recommend creating your own GitHub App:

    1. Go to [https://github.com/settings/apps/new](https://github.com/settings/apps/new)
    2. Fill in the basic information:
       * **GitHub App name**: Choose a unique name (e.g., "YourOrg Claude Assistant")
       * **Homepage URL**: Your organization's website or the repository URL
    3. Configure the app settings:
       * **Webhooks**: Uncheck "Active" (not needed for this integration)
    4. Set the required permissions:
       * **Repository permissions**:
         * Contents: Read & Write
         * Issues: Read & Write
         * Pull requests: Read & Write
    5. Click "Create GitHub App"
    6. After creation, click "Generate a private key" and save the downloaded `.pem` file
    7. Note your App ID from the app settings page
    8. Install the app to your repository:
       * From your app's settings page, click "Install App" in the left sidebar
       * Select your account or organization
       * Choose "Only select repositories" and select the specific repository
       * Click "Install"
    9. Add the private key as a secret to your repository:
       * Go to your repository's Settings → Secrets and variables → Actions
       * Create a new secret named `APP_PRIVATE_KEY` with the contents of the `.pem` file
    10. Add the App ID as a secret:

    * Create a new secret named `APP_ID` with your GitHub App's ID

    <Note>
      This app will be used with the [actions/create-github-app-token](https://github.com/actions/create-github-app-token) action to generate authentication tokens in your workflows.
    </Note>

    **Alternative for Anthropic API or if you don't want to setup your own Github app**: Use the official Anthropic app:

    1. Install from: [https://github.com/apps/claude](https://github.com/apps/claude)
    2. No additional configuration needed for authentication
  </Step>

  <Step title="Configure cloud provider authentication">
    Choose your cloud provider and set up secure authentication:

    <AccordionGroup>
      <Accordion title="AWS Bedrock">
        **Configure AWS to allow GitHub Actions to authenticate securely without storing credentials.**

        > **Security Note**: Use repository-specific configurations and grant only the minimum required permissions.

        **Required Setup**:

        1. **Enable Amazon Bedrock**:
           * Request access to Claude models in Amazon Bedrock
           * For cross-region models, request access in all required regions

        2. **Set up GitHub OIDC Identity Provider**:
           * Provider URL: `https://token.actions.githubusercontent.com`
           * Audience: `sts.amazonaws.com`

        3. **Create IAM Role for GitHub Actions**:
           * Trusted entity type: Web identity
           * Identity provider: `token.actions.githubusercontent.com`
           * Permissions: `AmazonBedrockFullAccess` policy
           * Configure trust policy for your specific repository

        **Required Values**:

        After setup, you'll need:

        * **AWS\_ROLE\_TO\_ASSUME**: The ARN of the IAM role you created

        <Tip>
          OIDC is more secure than using static AWS access keys because credentials are temporary and automatically rotated.
        </Tip>

        See [AWS documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html) for detailed OIDC setup instructions.
      </Accordion>

      <Accordion title="Google Vertex AI">
        **Configure Google Cloud to allow GitHub Actions to authenticate securely without storing credentials.**

        > **Security Note**: Use repository-specific configurations and grant only the minimum required permissions.

        **Required Setup**:

        1. **Enable APIs** in your Google Cloud project:
           * IAM Credentials API
           * Security Token Service (STS) API
           * Vertex AI API

        2. **Create Workload Identity Federation resources**:
           * Create a Workload Identity Pool
           * Add a GitHub OIDC provider with:
             * Issuer: `https://token.actions.githubusercontent.com`
             * Attribute mappings for repository and owner
             * **Security recommendation**: Use repository-specific attribute conditions

        3. **Create a Service Account**:
           * Grant only `Vertex AI User` role
           * **Security recommendation**: Create a dedicated service account per repository

        4. **Configure IAM bindings**:
           * Allow the Workload Identity Pool to impersonate the service account
           * **Security recommendation**: Use repository-specific principal sets

        **Required Values**:

        After setup, you'll need:

        * **GCP\_WORKLOAD\_IDENTITY\_PROVIDER**: The full provider resource name
        * **GCP\_SERVICE\_ACCOUNT**: The service account email address

        <Tip>
          Workload Identity Federation eliminates the need for downloadable service account keys, improving security.
        </Tip>

        For detailed setup instructions, consult the [Google Cloud Workload Identity Federation documentation](https://cloud.google.com/iam/docs/workload-identity-federation).
      </Accordion>
    </AccordionGroup>
  </Step>

  <Step title="Add Required Secrets">
    Add the following secrets to your repository (Settings → Secrets and variables → Actions):

    #### For Anthropic API (Direct):

    1. **For API Authentication**:
       * `ANTHROPIC_API_KEY`: Your Anthropic API key from [console.anthropic.com](https://console.anthropic.com)

    2. **For GitHub App (if using your own app)**:
       * `APP_ID`: Your GitHub App's ID
       * `APP_PRIVATE_KEY`: The private key (.pem) content

    #### For Google Cloud Vertex AI

    1. **For GCP Authentication**:
       * `GCP_WORKLOAD_IDENTITY_PROVIDER`
       * `GCP_SERVICE_ACCOUNT`

    2. **For GitHub App (if using your own app)**:
       * `APP_ID`: Your GitHub App's ID
       * `APP_PRIVATE_KEY`: The private key (.pem) content

    #### For AWS Bedrock

    1. **For AWS Authentication**:
       * `AWS_ROLE_TO_ASSUME`

    2. **For GitHub App (if using your own app)**:
       * `APP_ID`: Your GitHub App's ID
       * `APP_PRIVATE_KEY`: The private key (.pem) content
  </Step>

  <Step title="Create workflow files">
    Create GitHub Actions workflow files that integrate with your cloud provider. The examples below show complete configurations for both AWS Bedrock and Google Vertex AI:

    <AccordionGroup>
      <Accordion title="AWS Bedrock workflow">
        **Prerequisites:**

        * AWS Bedrock access enabled with Claude model permissions
        * GitHub configured as an OIDC identity provider in AWS
        * IAM role with Bedrock permissions that trusts GitHub Actions

        **Required GitHub secrets:**

        | Secret Name          | Description                                       |
        | -------------------- | ------------------------------------------------- |
        | `AWS_ROLE_TO_ASSUME` | ARN of the IAM role for Bedrock access            |
        | `APP_ID`             | Your GitHub App ID (from app settings)            |
        | `APP_PRIVATE_KEY`    | The private key you generated for your GitHub App |

        ```yaml
        name: Claude PR Action 

        permissions:
          contents: write
          pull-requests: write
          issues: write
          id-token: write 

        on:
          issue_comment:
            types: [created]
          pull_request_review_comment:
            types: [created]
          issues:
            types: [opened, assigned]

        jobs:
          claude-pr:
            if: |
              (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
              (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
              (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
            runs-on: ubuntu-latest
            env:
              AWS_REGION: us-west-2
            steps:
              - name: Checkout repository
                uses: actions/checkout@v4

              - name: Generate GitHub App token
                id: app-token
                uses: actions/create-github-app-token@v2
                with:
                  app-id: ${{ secrets.APP_ID }}
                  private-key: ${{ secrets.APP_PRIVATE_KEY }}

              - name: Configure AWS Credentials (OIDC)
                uses: aws-actions/configure-aws-credentials@v4
                with:
                  role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
                  aws-region: us-west-2

              - uses: ./.github/actions/claude-pr-action
                with:
                  trigger_phrase: "@claude"
                  timeout_minutes: "60"
                  github_token: ${{ steps.app-token.outputs.token }}
                  use_bedrock: "true"
                  model: "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        ```

        <Tip>
          The model ID format for Bedrock includes the region prefix (e.g., `us.anthropic.claude...`) and version suffix.
        </Tip>
      </Accordion>

      <Accordion title="Google Vertex AI workflow">
        **Prerequisites:**

        * Vertex AI API enabled in your GCP project
        * Workload Identity Federation configured for GitHub
        * Service account with Vertex AI permissions

        **Required GitHub secrets:**

        | Secret Name                      | Description                                       |
        | -------------------------------- | ------------------------------------------------- |
        | `GCP_WORKLOAD_IDENTITY_PROVIDER` | Workload identity provider resource name          |
        | `GCP_SERVICE_ACCOUNT`            | Service account email with Vertex AI access       |
        | `APP_ID`                         | Your GitHub App ID (from app settings)            |
        | `APP_PRIVATE_KEY`                | The private key you generated for your GitHub App |

        ```yaml
        name: Claude PR Action

        permissions:
          contents: write
          pull-requests: write
          issues: write
          id-token: write  

        on:
          issue_comment:
            types: [created]
          pull_request_review_comment:
            types: [created]
          issues:
            types: [opened, assigned]

        jobs:
          claude-pr:
            if: |
              (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
              (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
              (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
            runs-on: ubuntu-latest
            steps:
              - name: Checkout repository
                uses: actions/checkout@v4

              - name: Generate GitHub App token
                id: app-token
                uses: actions/create-github-app-token@v2
                with:
                  app-id: ${{ secrets.APP_ID }}
                  private-key: ${{ secrets.APP_PRIVATE_KEY }}

              - name: Authenticate to Google Cloud
                id: auth
                uses: google-github-actions/auth@v2
                with:
                  workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
                  service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}
              
              - uses: ./.github/actions/claude-pr-action
                with:
                  trigger_phrase: "@claude"
                  timeout_minutes: "60"
                  github_token: ${{ steps.app-token.outputs.token }}
                  use_vertex: "true"
                  model: "claude-3-7-sonnet@20250219"
                env:
                  ANTHROPIC_VERTEX_PROJECT_ID: ${{ steps.auth.outputs.project_id }}
                  CLOUD_ML_REGION: us-east5
                  VERTEX_REGION_CLAUDE_3_7_SONNET: us-east5
        ```

        <Tip>
          The project ID is automatically retrieved from the Google Cloud authentication step, so you don't need to hardcode it.
        </Tip>
      </Accordion>
    </AccordionGroup>
  </Step>
</Steps>

## Troubleshooting

### Claude not responding to @claude commands

Verify the GitHub App is installed correctly, check that workflows are enabled, ensure API key is set in repository secrets, and confirm the comment contains `@claude` (not `/claude`).

### CI not running on Claude's commits

Ensure you're using the GitHub App or custom app (not Actions user), check workflow triggers include the necessary events, and verify app permissions include CI triggers.

### Authentication errors

Confirm API key is valid and has sufficient permissions. For Bedrock/Vertex, check credentials configuration and ensure secrets are named correctly in workflows.

## Advanced configuration

### Action parameters

The Claude Code Action supports these key parameters:

| Parameter           | Description                    | Required |
| ------------------- | ------------------------------ | -------- |
| `prompt`            | The prompt to send to Claude   | Yes\*    |
| `prompt_file`       | Path to file containing prompt | Yes\*    |
| `anthropic_api_key` | Anthropic API key              | Yes\*\*  |
| `max_turns`         | Maximum conversation turns     | No       |
| `timeout_minutes`   | Execution timeout              | No       |

\*Either `prompt` or `prompt_file` required\
\*\*Required for direct Anthropic API, not for Bedrock/Vertex

### Alternative integration methods

While the `/install-github-app` command is the recommended approach, you can also:

* **Custom GitHub App**: For organizations needing branded usernames or custom authentication flows. Create your own GitHub App with required permissions (contents, issues, pull requests) and use the actions/create-github-app-token action to generate tokens in your workflows.
* **Manual GitHub Actions**: Direct workflow configuration for maximum flexibility
* **MCP Configuration**: Dynamic loading of Model Context Protocol servers

See the [Claude Code Action repository](https://github.com/anthropics/claude-code-action) for detailed documentation.

### Customizing Claude's behavior

You can configure Claude's behavior in two ways:

1. **CLAUDE.md**: Define coding standards, review criteria, and project-specific rules in a `CLAUDE.md` file at the root of your repository. Claude will follow these guidelines when creating PRs and responding to requests. Check out our [Memory documentation](/en/docs/claude-code/memory) for more details.
2. **Custom prompts**: Use the `prompt` parameter in the workflow file to provide workflow-specific instructions. This allows you to customize Claude's behavior for different workflows or tasks.

Claude will follow these guidelines when creating PRs and responding to requests.

# SDK

> Programmatically integrate Claude Code into your applications using the SDK.

The Claude Code SDK allows developers to programmatically integrate Claude Code into their applications. It enables running Claude Code as a subprocess, providing a way to build AI-powered coding assistants and tools that leverage Claude's capabilities.

The SDK currently support command line usage. TypeScript and Python SDKs are coming soon.

## Authentication

To use the Claude Code SDK, we recommend creating a dedicated API key:

1. Create an Anthropic API key in the [Anthropic Console](https://console.anthropic.com/)
2. Then, set the `ANTHROPIC_API_KEY` environment variable. We recommend storing this key securely (eg. using a Github [secret](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions))

## Basic SDK usage

The Claude Code SDK allows you to use Claude Code in non-interactive mode from your applications. Here's a basic example:

```bash
# Run a single prompt and exit (print mode)
$ claude -p "Write a function to calculate Fibonacci numbers"

# Using a pipe to provide stdin
$ echo "Explain this code" | claude -p

# Output in JSON format with metadata
$ claude -p "Generate a hello world function" --output-format json

# Stream JSON output as it arrives
$ claude -p "Build a React component" --output-format stream-json
```

## Advanced usage

### Multi-turn conversations

For multi-turn conversations, you can resume conversations or continue from the most recent session:

```bash
# Continue the most recent conversation
$ claude --continue

# Continue and provide a new prompt
$ claude --continue "Now refactor this for better performance"

# Resume a specific conversation by session ID
$ claude --resume 550e8400-e29b-41d4-a716-446655440000

# Resume in print mode (non-interactive)
$ claude -p --resume 550e8400-e29b-41d4-a716-446655440000 "Update the tests"

# Continue in print mode (non-interactive)
$ claude -p --continue "Add error handling"
```

### Custom system prompts

You can provide custom system prompts to guide Claude's behavior:

```bash
# Override system prompt (only works with --print)
$ claude -p "Build a REST API" --system-prompt "You are a senior backend engineer. Focus on security, performance, and maintainability."

# System prompt with specific requirements
$ claude -p "Create a database schema" --system-prompt "You are a database architect. Use PostgreSQL best practices and include proper indexing."
```

You can also append instructions to the default system prompt:

```bash
# Append system prompt (only works with --print)
$ claude -p "Build a REST API" --append-system-prompt "After writing code, be sure to code review yourself."
```

### MCP Configuration

The Model Context Protocol (MCP) allows you to extend Claude Code with additional tools and resources from external servers. Using the `--mcp-config` flag, you can load MCP servers that provide specialized capabilities like database access, API integrations, or custom tooling.

Create a JSON configuration file with your MCP servers:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/allowed/files"
      ]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your-github-token"
      }
    }
  }
}
```

Then use it with Claude Code:

```bash
# Load MCP servers from configuration
$ claude -p "List all files in the project" --mcp-config mcp-servers.json

# Important: MCP tools must be explicitly allowed using --allowedTools
# MCP tools follow the format: mcp__$serverName__$toolName
$ claude -p "Search for TODO comments" \
  --mcp-config mcp-servers.json \
  --allowedTools "mcp__filesystem__read_file,mcp__filesystem__list_directory"

# Use an MCP tool for handling permission prompts in non-interactive mode
$ claude -p "Deploy the application" \
  --mcp-config mcp-servers.json \
  --allowedTools "mcp__permissions__approve" \
  --permission-prompt-tool mcp__permissions__approve
```

Note: When using MCP tools, you must explicitly allow them using the `--allowedTools` flag. MCP tool names follow the pattern `mcp__<serverName>__<toolName>` where:

* `serverName` is the key from your MCP configuration file
* `toolName` is the specific tool provided by that server

This security measure ensures that MCP tools are only used when explicitly permitted.

### Custom permission prompt tool

Optionally, use `--permission-prompt-tool` to pass in an MCP tool that we will use to check whether or not the user grants the model permissions to invoke a given tool. When the model invokes a tool the following happens:

1. We first check permission settings: all [settings.json files](/en/docs/claude-code/settings), as well as `--allowedTools` and `--disallowedTools` passed into the SDK; if one of these allows or denies the tool call, we proceed with the tool call
2. Otherwise, we invoke the MCP tool you provided in `--permission-prompt-tool`

The `--permission-prompt-tool` MCP tool is passed the tool name and input, and must return a JSON-stringified payload with the result. The payload must be one of:

```ts
// tool call is allowed
{
  "behavior": "allow",
  "updatedInput": {...}, // updated input, or just return back the original input
}

// tool call is denied
{
  "behavior": "deny",
  "message": "..." // human-readable string explaining why the permission was denied
}
```

For example, a TypeScript MCP permission prompt tool implementation might look like this:

```ts
const server = new McpServer({
  name: "Test permission prompt MCP Server",
  version: "0.0.1",
});

server.tool(
  "approval_prompt",
  'Simulate a permission check - approve if the input contains "allow", otherwise deny',
  {
    tool_name: z.string().describe("The tool requesting permission"),
    input: z.object({}).passthrough().describe("The input for the tool"),
  },
  async ({ tool_name, input }) => {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            JSON.stringify(input).includes("allow")
              ? {
                  behavior: "allow",
                  updatedInput: input,
                }
              : {
                  behavior: "deny",
                  message: "Permission denied by test approval_prompt tool",
                }
          ),
        },
      ],
    };
  }
);
```

To use this tool, add your MCP server (eg. with `--mcp-config`), then invoke the SDK like so:

```sh
claude -p "..." \
  --permission-prompt-tool mcp__test-server__approval_prompt \
  --mcp-config my-config.json
```

Usage notes:

* Use `updatedInput` to tell the model that the permission prompt mutated its input; otherwise, set `updatedInput` to the original input, as in the example above. For example, if the tool shows a file edit diff to the user and lets them edit the diff manually, the permission prompt tool should return that updated edit.
* The payload must be JSON-stringified

## Available CLI options

The SDK leverages all the CLI options available in Claude Code. Here are the key ones for SDK usage:

| Flag                       | Description                                                      | Example                                                     |
| :------------------------- | :--------------------------------------------------------------- | :---------------------------------------------------------- |
| `--print`, `-p`            | Run in non-interactive mode                                      | `claude -p "query"`                                         |
| `--output-format`          | Specify output format (`text`, `json`, `stream-json`)            | `claude -p --output-format json`                            |
| `--resume`, `-r`           | Resume a conversation by session ID                              | `claude --resume abc123`                                    |
| `--continue`, `-c`         | Continue the most recent conversation                            | `claude --continue`                                         |
| `--verbose`                | Enable verbose logging                                           | `claude --verbose`                                          |
| `--max-turns`              | Limit agentic turns in non-interactive mode                      | `claude --max-turns 3`                                      |
| `--system-prompt`          | Override system prompt (only with `--print`)                     | `claude --system-prompt "Custom instruction"`               |
| `--append-system-prompt`   | Append to system prompt (only with `--print`)                    | `claude --append-system-prompt "Custom instruction"`        |
| `--allowedTools`           | Comma/space-separated list of allowed tools (includes MCP tools) | `claude --allowedTools "Bash(npm install),mcp__filesystem"` |
| `--disallowedTools`        | Comma/space-separated list of denied tools                       | `claude --disallowedTools "Bash(git commit),mcp__github"`   |
| `--mcp-config`             | Load MCP servers from a JSON file                                | `claude --mcp-config servers.json`                          |
| `--permission-prompt-tool` | MCP tool for handling permission prompts (only with `--print`)   | `claude --permission-prompt-tool mcp__auth__prompt`         |

For a complete list of CLI options and features, see the [CLI usage](/en/docs/claude-code/cli-usage) documentation.

## Output formats

The SDK supports multiple output formats:

### Text output (default)

Returns just the response text:

```bash
$ claude -p "Explain file src/components/Header.tsx"
# Output: This is a React component showing...
```

### JSON output

Returns structured data including metadata:

```bash
$ claude -p "How does the data layer work?" --output-format json
```

Response format:

```json
{
  "type": "result",
  "subtype": "success",
  "cost_usd": 0.003,
  "is_error": false,
  "duration_ms": 1234,
  "duration_api_ms": 800,
  "num_turns": 6,
  "result": "The response text here...",
  "session_id": "abc123"
}
```

### Streaming JSON output

Streams each message as it is received:

```bash
$ claude -p "Build an application" --output-format stream-json
```

Each conversation begins with an initial `init` system message, followed by a list of user and assistant messages, followed by a final `result` system message with stats. Each message is emitted as a separate JSON object.

## Message schema

Messages returned from the JSON API are strictly typed according to the following schema:

```ts
type SDKMessage =
  // An assistant message
  | {
      type: "assistant";
      message: Message; // from Anthropic SDK
      session_id: string;
    }

  // A user message
  | {
      type: "user";
      message: MessageParam; // from Anthropic SDK
      session_id: string;
    }

  // Emitted as the last message
  | {
      type: "result";
      subtype: "success";
      cost_usd: float;
      duration_ms: float;
      duration_api_ms: float;
      is_error: boolean;
      num_turns: int;
      result: string;
      session_id: string;
    }

  // Emitted as the last message, when we've reached the maximum number of turns
  | {
      type: "result";
      subtype: "error_max_turns";
      cost_usd: float;
      duration_ms: float;
      duration_api_ms: float;
      is_error: boolean;
      num_turns: int;
      session_id: string;
    }

  // Emitted as the first message at the start of a conversation
  | {
      type: "system";
      subtype: "init";
      session_id: string;
      tools: string[];
      mcp_servers: {
        name: string;
        status: string;
      }[];
    };
```

We will soon publish these types in a JSONSchema-compatible format. We use semantic versioning for the main Claude Code package to communicate breaking changes to this format.

`Message` and `MessageParam` types are available in Anthropic SDKs. For example, see the Anthropic [TypeScript](https://github.com/anthropics/anthropic-sdk-typescript) and [Python](https://github.com/anthropics/anthropic-sdk-python/) SDKs.

## Examples

### Simple script integration

```bash
#!/bin/bash

# Simple function to run Claude and check exit code
run_claude() {
    local prompt="$1"
    local output_format="${2:-text}"

    if claude -p "$prompt" --output-format "$output_format"; then
        echo "Success!"
    else
        echo "Error: Claude failed with exit code $?" >&2
        return 1
    fi
}

# Usage examples
run_claude "Write a Python function to read CSV files"
run_claude "Optimize this database query" "json"
```

### Processing files with Claude

```bash
# Process a file through Claude
$ cat mycode.py | claude -p "Review this code for bugs"

# Process multiple files
$ for file in *.js; do
    echo "Processing $file..."
    claude -p "Add JSDoc comments to this file:" < "$file" > "${file}.documented"
done

# Use Claude in a pipeline
$ grep -l "TODO" *.py | while read file; do
    claude -p "Fix all TODO items in this file" < "$file"
done
```

### Session management

```bash
# Start a session and capture the session ID
$ claude -p "Initialize a new project" --output-format json | jq -r '.session_id' > session.txt

# Continue with the same session
$ claude -p --resume "$(cat session.txt)" "Add unit tests"
```

## Best practices

1. **Use JSON output format** for programmatic parsing of responses:

   ```bash
   # Parse JSON response with jq
   result=$(claude -p "Generate code" --output-format json)
   code=$(echo "$result" | jq -r '.result')
   cost=$(echo "$result" | jq -r '.cost_usd')
   ```

2. **Handle errors gracefully** - check exit codes and stderr:

   ```bash
   if ! claude -p "$prompt" 2>error.log; then
       echo "Error occurred:" >&2
       cat error.log >&2
       exit 1
   fi
   ```

3. **Use session management** for maintaining context in multi-turn conversations

4. **Consider timeouts** for long-running operations:

   ```bash
   timeout 300 claude -p "$complex_prompt" || echo "Timed out after 5 minutes"
   ```

5. **Respect rate limits** when making multiple requests by adding delays between calls

## Real-world applications

The Claude Code SDK enables powerful integrations with your development workflow. One notable example is the [Claude Code GitHub Actions](/en/docs/claude-code/github-actions), which uses the SDK to provide automated code review, PR creation, and issue triage capabilities directly in your GitHub workflow.

## Related resources

* [CLI usage and controls](/en/docs/claude-code/cli-usage) - Complete CLI documentation
* [GitHub Actions integration](/en/docs/claude-code/github-actions) - Automate your GitHub workflow with Claude
* [Tutorials](/en/docs/claude-code/tutorials) - Step-by-step guides for common use cases

