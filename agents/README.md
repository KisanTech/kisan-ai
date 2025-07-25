# AI Agent Layer for Kisan AI

## Step-by-Step Setup Instructions

1. **Navigate to the agents directory:**

   ```bash
   cd agents
   ```

2. **Install all Python dependencies using uv (recommended for speed and reliability):**

   ```bash
   uv sync
   ```

3. **Authenticate your Google Cloud CLI:**

   ```bash
   gcloud auth login
   ```

4. **(Recommended for API access) Set up Application Default Credentials:**

   ```bash
   gcloud auth application-default login
   ```

   > _Tip: This ensures your local environment can access Google Cloud services programmatically._

5. **Verify ADK installation and see available commands:**
   ```bash
   adk
   ```

---

## Running and Interacting with Agents

From the root `agents` folder, you can use the following commands:

- `adk web`  
  _Launches a web UI to interact with your agent locally at [http://localhost:8000](http://localhost:8000) with event streaming and debugging support._

- `adk run <agent_name>`  
  _Starts a CLI interface for direct interaction with the specified agent (e.g., `adk run crop_diagnosis_agent`)._

- `adk api_server`  
  _Runs a local REST API server for your agent, enabling programmatic access and integration with other services._

---

**Note:**

- Ensure your `.env` file is properly configured with all required environment variables before running or deploying agents.
- For more details on agent development, deployment, and troubleshooting, refer to the [Google ADK documentation](https://github.com/google/agent-development-kit).
