# Instructions to Run the Play Store MCP Server

This guide explains how to configure, run, and integrate the Play Store MCP Server on your local machine (Windows) or in Docker.

---

## 🔑 Step 1: Google Cloud & Play Console Setup

Before running the server, you need to authenticate with the Google Play Developer API.

### 1. Create a Service Account (Google Cloud)
1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Select or create a project.
3. Enable the **Google Play Developer API**.
4. Navigate to **IAM & Admin** > **Service Accounts**.
5. Click **Create Service Account** and assign a name.
6. Under **Keys**, click **Add Key** > **Create New Key** > Select **JSON** format.
7. Save the downloaded JSON file (e.g. `c:/credentials/play-store-key.json`). **Keep this file secure!**

### 2. Grant Access in Google Play Console
1. Go to the [Google Play Console](https://play.google.com/console/).
2. Navigate to **Users and permissions** > Click **Invite new users**.
3. Enter the email of the Service Account you created (found in the JSON key).
4. Grant the following permissions under **Account permissions**:
   - **Release apps to testing tracks** (internal/alpha/beta rollouts)
   - **Release apps to production** (production deployments)
   - **Reply to reviews** (fetching and responding to user reviews)
   - **View app information and download bulk reports** (stability vitals data)
5. Save the invitation.

---

## ⚙️ Step 2: Configure Environment Variables

On Windows, you can set the path to your service account key. 

### In PowerShell:
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="c:/credentials/play-store-key.json"
```

### In Command Prompt (CMD):
```cmd
set GOOGLE_APPLICATION_CREDENTIALS=c:/credentials/play-store-key.json
```

---

## 🚀 Step 3: Run the Server

You can run the server using `uv` (our package manager) with different transport mechanisms:

### Option A: Standard I/O (Recommended for local clients)
This runs the server using standard input/output (stdio), which is the default protocol used by local clients like Claude Desktop:
```powershell
python -m uv run play-store-mcp --transport stdio
```

### Option B: HTTP Streamable Transport (For network access)
This starts an HTTP FastAPI server, useful if you want to deploy the server on a host and connect remotely:
```powershell
python -m uv run play-store-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```
- Custom HTTP headers (`X-Google-Credentials` or `X-Google-Credentials-Base64`) can be passed with requests.
- Health Check is available at: `http://localhost:8000/health`
- Credentials can be dynamically updated via: `http://localhost:8000/credentials`

---

## 💻 Step 4: Configure Claude Desktop

To connect the server to Claude Desktop:

1. Open your Claude Desktop configuration file:
   - Path: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the `play-store` configuration to the `mcpServers` object:

```json
{
  "mcpServers": {
    "play-store": {
      "command": "python",
      "args": [
        "-m",
        "uv",
        "run",
        "--project",
        "c:/Users/K.Arunadevi/Google Playstore",
        "play-store-mcp",
        "--transport",
        "stdio"
      ],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "c:/credentials/play-store-key.json"
      }
    }
  }
}
```
3. Restart Claude Desktop.

---

## 🐳 Step 5: Run with Docker

If you prefer to run the server in a containerized environment:

### 1. Build the Docker Image
```powershell
docker build -t play-store-mcp .
```

### 2. Run the Container (passing credentials as a volume)
```powershell
docker run -d `
  --name play-store-mcp-container `
  -p 8000:8000 `
  -e GOOGLE_APPLICATION_CREDENTIALS=/creds/key.json `
  -e MCP_TRANSPORT=streamable-http `
  -v c:/credentials/play-store-key.json:/creds/key.json:ro `
  play-store-mcp
```

### 3. Verify Health Check
```powershell
curl http://localhost:8000/health
```
