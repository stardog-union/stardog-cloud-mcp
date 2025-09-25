# Stardog Cloud MCP Server

## Table of Contents
- [Overview](#overview)
- [Available Tools](#available-tools)
- [Requirements](#requirements)
- [Obtaining the API Token](#obtaining-the-api-token)
- [Local Setup](#local-setup)
  - [Setting up the Server](#setting-up-the-server)
  - [Integrations](#integrations)
- [Remote Setup (Beta)](#remote-setup-beta)
  - [Integrating with Cursor](#integrating-with-cursor)
  - [Integrating with Claude](#integrating-with-claude)
- [Local Development](#local-development)

---

## Overview

This project provides a server for accessing Stardog Cloud's Voicebox APIs, enabling natural language interaction with your Stardog knowledge graphs. The server is designed to be integrated with various MCP host applications (such as Claude Desktop, Cursor, custom clients etc) and can be configured for local, as well as remote MCP access.

---

## Available Tools

- **voicebox_settings**: Retrieve the current settings for your Voicebox application, including database, model, and configuration details.
- **voicebox_ask**: Ask natural language questions and receive answers from Stardog Voicebox, leveraging your database and model.
- **voicebox_generate_query**: Generate SPARQL queries from natural language questions using Voicebox's AI capabilities.

---

## Requirements

You can run the server locally using either Docker or Python/uv:

- **Python**: `>=3.12`
- **uv**: a python package and project manager ([uv](https://github.com/astral-sh/uv))
- **npx**: only for running mcp-remote based MCP host-server connections see [Integrating Claude desktop with Remote MCP](#integrating-with-claude)
- **Stardog Cloud API Token**: Required for authentication with Stardog Cloud APIs

---

## Obtaining the API Token

1. Go to [cloud.stardog.com](https://cloud.stardog.com) and log in.
2. Click on your profile icon (top right) and select **Manage API Keys**.
3. Create a new application and generate a secret.
4. Copy the API token and keep it secure.
5. For more details, see [Stardog Voicebox API access](https://docs.stardog.com/voicebox/voicebox-dev-guide/#api-access).

---

## Local Setup

### Setting up the Server

**Clone the repository into your system and ensure you have Python and uv set up to proceed with local integration.**  
For local development, you can use the provisioned make commands. See [Local Development](#local-development) for more details.
> You can run `which uv` to find the path to the `uv` command. This is the path you should use for the `command` field in the configuration.
>```bash
>$ which uv
>/Users/pranavk/.local/bin/uv
>```

### Integrating with Claude Desktop: 
Use the following sample json to make Claude Desktop to point to your local MCP server. 
- Go to Claude Desktop settings, go to the Developer section, and click on Edit Config to open the configuration file
- Create your entry using the below and add it to the `claude_desktop_config.json` file.
- See [Claude MCP documentation](https://modelcontextprotocol.io/quickstart/user) for more details.
```json
{
    "mcpServers": {
        "stardog-cloud-mcp": {
            "command": "uv",
            "args": [
                "--directory",
                "/path/to/stardog-cloud-mcp",
                "run",
                "stardog-cloud-mcp",
                "--token",
                "your_stardog_cloud_voicebox_api_token",
                "--client_id",
                "your_stardog_cloud_voicebox_app_id"
            ]
        }
    }
}
```

> [!NOTE]
> - You can additionally specify `--endpoint` to point to a different Stardog Cloud instance \[Default: https://cloud.stardog.com/api\]  
> - The `--client_id` is optional but recommended to help track usage
### **Cursor**: 
Use Cursor's MCP integration to connect to your local server by configuring the `mcp.json` file. 
- Add this file to your project workspace at _./cursor/mcp.json_.
- Go to Cursor settings, under MCP and Integration, find your configured server and verify the available tools. 
- See [Cursor MCP documentation](https://docs.cursor.com/en/context/mcp#using-mcp-json) to find more details.
```json
{
  "mcpServers": {
    "stardog-cloud-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/stardog-cloud-mcp",
        "run",
        "stardog-cloud-mcp",
        "--token",
        "your_stardog_cloud_voicebox_api_token",
        "--client_id",
        "your_stardog_cloud_voicebox_app_id"
      ]
    }
  }
}
```

---

## Remote Setup (Beta)

You can configure remote MCP access for tools like Cursor and Claude Desktop. 
The server requires your Voicebox API token for authentication. This needs to be provisioned in the headers against the key `x-sdc-api-key`.

### Integrating with Cursor

Add the following to your Cursor configuration:

```json
{
  "mcpServers": {
    "vbx-cloud-mcp": {
      "url": "http://0.0.0.0:7001/mcp",
      "headers": {
        "x-sdc-api-key": "your_stardog_cloud_voicebox_api_token",
        "x-sdc-client-id": "your_stardog_cloud_voicebox_app_client_id",
        "x-sd-auth-token": "optional_stardog_auth_token_override"
      }
    }
  }
}
```
See [Cursor MCP documentation](https://docs.cursor.com/en/context/mcp#using-mcp-json) for more details.

**Note:** The `x-sd-auth-token` header is an optional bearer token to override the default Stardog token for Voicebox. This is useful when connecting via SSO (e.g., Microsoft Entra) to supply a custom SSO token for Stardog authentication.

### Integrating with Claude

Sample configuration for Claude Desktop:

```json
{
  "mcpServers": {
    "vbx-cloud-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:7001/mcp",
        "--header",
        "x-sdc-api-key: your_stardog_cloud_voicebox_api_token",
        "--header",
        "x-sdc-client-id: your_stardog_cloud_voicebox_app_client_id",
        "--header",
        "x-sd-auth-token: optional_stardog_auth_token_override"
      ]
    }
  }
}
```
See [Claude Remote MCP documentation](https://docs.anthropic.com/claude/remote-mcp) for more info.

**Note:** The `x-sd-auth-token` header is an optional bearer token to override the default Stardog token for Voicebox. This is useful when connecting via SSO (e.g., Microsoft Entra) to supply a custom SSO token for Stardog authentication.

---

## Local Development

To set up a development environment, use the provided Makefile commands:

1. **Install dependencies and set up the environment:**
   ```bash
   make install-dev
   ```
2. **Format code:**
   ```bash
   make format
   ```
3. **Run SAST checks:**
   ```bash
   make ci
   ```
4. **Run tests:**
   ```bash
   make test
   ```
5. **Clean up build artifacts and environment:**
   ```bash
   make clean
   ```
For more commands and usage, run:
```bash
make help
```
