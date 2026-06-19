# Google Play Store MCP Server & Autonomous Agent Workflow

An MCP (Model Context Protocol) server that connects to the **Google Play Developer API**, combined with a machine-executable **Autonomous Agent Monitoring Workflow** to monitor app vitals, subscriptions, and reviews.

---

## 🌟 Key Features

*   🚀 **App Deployment & Release Management**: Deploy APK/AAB builds to any track, control rollouts, or halt staged releases.
*   👥 **Tester & Store Listings Management**: Update email lists for testing tracks and manage localized store listings.
*   ⭐ **Review Management**: Retrieve recent user reviews and reply directly to feedback.
*   💳 **Monetization Analytics**: List subscriptions, check purchase tokens, and monitor refund/voided purchase patterns.
*   📈 **Android Vitals**: Monitor crash and ANR statistics.
*   🤖 **Autonomous Monitoring Workflow**: A flat, machine-parseable YAML workflow allowing AI agents to monitor app health daily.
*   🐳 **Docker & Health Checks**: Exposes a `/health` endpoint for remote server health monitoring.

---

## 📂 Project Structure

This project has been cleaned up and optimized for deployment:

*   [PlayStore_Agent_Workflow.yml](file:///c:/Users/K.Arunadevi/Google%20Playstore/PlayStore_Agent_Workflow.yml): Simplified flat YAML workflow for automated monitoring agents.
*   [PlayStore_Agent_Workflow.md](file:///c:/Users/K.Arunadevi/Google%20Playstore/PlayStore_Agent_Workflow.md): Detailed documentation covering the 23 execution steps of the monitoring workflow.
*   [RUNNING_INSTRUCTIONS.md](file:///c:/Users/K.Arunadevi/Google%20Playstore/RUNNING_INSTRUCTIONS.md): Comprehensive guide on setting up Google Cloud Service Accounts, Play Console permissions, and running the server.
*   `src/`: Python source code implementing the MCP server and API clients.
*   `tests/`: Test suite containing mock-based unit tests for all MCP tool definitions.

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.11+**
- **Google Cloud Service Account JSON Key** with Play Console access.
- **uv** (astral) package manager installed.

### 2. Install Dependencies
```powershell
python -m pip install uv
python -m uv sync --extra dev
```

### 3. Run the Server
Configure your credentials in the environment and start the server:

*   **Standard I/O (Default for Claude Desktop)**:
    ```powershell
    $env:GOOGLE_APPLICATION_CREDENTIALS="c:/path/to/key.json"
    python -m uv run play-store-mcp --transport stdio
    ```
*   **Streamable HTTP (For network environments)**:
    ```powershell
    python -m uv run play-store-mcp --transport streamable-http --host 127.0.0.1 --port 8000
    ```

---

## 🤖 Running the Agent Workflow
AI agents can read and execute [PlayStore_Agent_Workflow.yml](file:///c:/Users/K.Arunadevi/Google%20Playstore/PlayStore_Agent_Workflow.yml) step-by-step. The workflow executes the following routine:

1.  **Retrieve Vitals & Releases**: Fetches current tracks and crash/ANR rates.
2.  **Evaluate Safety**: If crash rate > 2% or ANR > 0.5%, triggers the **Critical Response Path** (halts rollout, replies to user reviews, alerts team).
3.  **Perform Regular Monitoring**: If healthy, reviews subscriptions, analyzes review sentiments, and raises rollout percentages.
4.  **Reporting**: Generates a daily status report and emails it to the team.

For full setup guides and advanced configuration, refer to [RUNNING_INSTRUCTIONS.md](file:///c:/Users/K.Arunadevi/Google%20Playstore/RUNNING_INSTRUCTIONS.md).