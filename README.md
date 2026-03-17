# Elementor MCP Skill for Claude Code

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that lets Claude build, edit, and manage [Elementor](https://elementor.com/) pages on any WordPress site through natural language.

Powered by the [MCP Tools for Elementor](https://github.com/msrbuilds/elementor-mcp) WordPress plugin.

## What It Does

Instead of manually dragging widgets in the Elementor editor, you tell Claude what you want and it builds it:

- "Create a landing page with a hero section, features grid, and contact form"
- "Add a pricing table to the services page"
- "Change the header background to dark blue and update the font to Inter"
- "Build a testimonial carousel with 3 slides"

Claude handles all 97 Elementor MCP tools — pages, containers, widgets, templates, popups, WooCommerce, global styles, custom code, and more.

## Why a Skill Instead of Using the MCP Server Directly?

This skill was generated from the [MCP Tools for Elementor](https://github.com/msrbuilds/elementor-mcp) server. The MCP server exposes **97 tools** with **385KB+ of schema data**. When Claude Code connects to the MCP server directly, it needs to discover, fetch, and parse all of that schema data **every single conversation** — burning thousands of tokens just on tool discovery before any real work begins.

This skill solves that by pre-documenting every tool, parameter, and workflow pattern in a compact SKILL.md file. Claude reads the skill once and jumps straight to building — **no discovery overhead, no wasted tokens, no repeated schema parsing**.

| | Direct MCP Connection | This Skill |
|---|---|---|
| Token cost per session | High (385KB+ schema fetched each time) | Low (compact skill file) |
| First tool call speed | Slow (discover + parse + plan) | Fast (already knows all tools) |
| Workflow patterns | Must figure out each time | Pre-documented |
| Works offline from MCP schema | No | Yes (skill has all tool docs) |

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (CLI or VS Code extension)
- Python 3.8+
- curl (available on macOS, Linux, and Windows with Git Bash)
- WordPress site with:
  - [MCP Tools for Elementor](https://github.com/msrbuilds/elementor-mcp) plugin installed and activated
  - [Application Password](https://make.wordpress.org/core/2020/11/05/application-passwords-integration-guide/) created for API access

## Installation

### 1. Clone the skill into your Claude skills directory

**macOS / Linux:**
```bash
git clone https://github.com/Mekko-Digital/elementor-mcp-skill.git ~/.claude/skills/elementor-mcp
```

**Windows:**
```bash
git clone https://github.com/Mekko-Digital/elementor-mcp-skill.git %USERPROFILE%\.claude\skills\elementor-mcp
```

### 2. Set up your WordPress site

Install and activate the [MCP Tools for Elementor](https://github.com/msrbuilds/elementor-mcp) plugin on your WordPress site.

### 3. Create an Application Password

1. In WordPress admin, go to **Users > Your Profile**
2. Scroll to **Application Passwords**
3. Enter a name (e.g., "Claude Code") and click **Add New Application Password**
4. Copy the generated password

### 4. Create `.mcp.json` in your project root

```json
{
  "mcpServers": {
    "elementor-mcp": {
      "type": "http",
      "url": "https://yoursite.com/wp-json/mcp/elementor-mcp-server",
      "headers": {
        "Authorization": "Basic BASE64_ENCODED_CREDENTIALS"
      }
    }
  }
}
```

To generate the Base64 credentials:

```bash
echo -n "your_username:your_application_password" | base64
```

### 5. Add `.mcp.json` to `.gitignore`

```
.mcp.json
```

This file contains your credentials — never commit it.

## Usage

Once installed, the skill activates automatically when you ask Claude to work with Elementor. Just open Claude Code in your WordPress project directory and start asking:

```
> List all my Elementor pages
> Show me the structure of the Home page
> Create a new landing page with a hero section and CTA button
> Add a contact form to page ID 130
> Update the global colors to use a blue theme
```

### Manual CLI usage

You can also use the wrapper script directly:

```bash
# List all Elementor pages
python ~/.claude/skills/elementor-mcp/scripts/elementor-mcp.py --tool elementor-mcp-list-pages --pretty

# Get page structure
python ~/.claude/skills/elementor-mcp/scripts/elementor-mcp.py --tool elementor-mcp-get-page-structure --params '{"post_id": 8}' --pretty

# Build a complete page
python ~/.claude/skills/elementor-mcp/scripts/elementor-mcp.py --tool elementor-mcp-build-page --params '{
  "title": "My Page",
  "status": "draft",
  "structure": [
    {
      "type": "container",
      "settings": {"flex_direction": "column"},
      "children": [
        {"type": "widget", "widget_type": "heading", "settings": {"title": "Hello World", "align": "center"}}
      ]
    }
  ]
}' --pretty

# List all available tools
python ~/.claude/skills/elementor-mcp/scripts/elementor-mcp.py --list
```

### Multi-site support

The script auto-detects the `.mcp.json` from your current directory. If you have multiple MCP servers configured:

```bash
python ~/.claude/skills/elementor-mcp/scripts/elementor-mcp.py --server my-other-site --tool elementor-mcp-list-pages --pretty
```

Or point to a different project:

```bash
python ~/.claude/skills/elementor-mcp/scripts/elementor-mcp.py --project-dir /path/to/other/project --tool elementor-mcp-list-pages --pretty
```

## Available Tools (97 total)

| Category | Tools | Description |
|----------|-------|-------------|
| **Discovery** | 11 | List pages, widgets, templates; get schemas, settings, structure |
| **Page Management** | 5 | Create, update, delete, export, import pages |
| **Page Builder** | 1 | Build complete page from declarative JSON structure |
| **Containers** | 2 | Add and update flex/grid layout containers |
| **Common Widgets** | 20 | Heading, text, image, button, icon, spacer, divider, accordion, tabs, etc. |
| **Pro Widgets** | 21 | Forms, posts grid, countdown, price table, slides, gallery, lottie, etc. |
| **WooCommerce** | 5 | Products grid, add-to-cart, cart, checkout, menu cart |
| **Element Operations** | 7 | Update, remove, duplicate, move, reorder, batch update |
| **Templates & Theme** | 6 | Save/apply templates, theme builder, dynamic tags, conditions |
| **Popups** | 2 | Create popups, set triggers and conditions |
| **Global Design** | 2 | Update site-wide colors and typography |
| **Images & Media** | 4 | Search stock images, sideload, upload SVG icons |
| **Custom Code** | 4 | Add JS, CSS, code snippets to pages or site-wide |

See [SKILL.md](SKILL.md) for complete parameter documentation and examples for every tool.

## How It Works

```
You (natural language) --> Claude Code --> Skill (SKILL.md) --> Python wrapper --> MCP Server --> WordPress/Elementor
```

1. You describe what you want in plain English
2. Claude reads the SKILL.md to understand available tools and parameters
3. The Python wrapper handles MCP session management (initialize, session ID, JSON-RPC)
4. Your WordPress site's MCP plugin executes the Elementor operations
5. Results come back as JSON

The wrapper reads connection details from `.mcp.json` in your project, so the same skill works across all your WordPress sites.

## Project Structure

```
elementor-mcp-skill/
  SKILL.md               # Claude Code skill definition (tool docs + examples)
  scripts/
    elementor-mcp.py     # MCP session wrapper (reads .mcp.json, calls tools via curl)
  README.md              # This file
  LICENSE                # MIT License
```

## Troubleshooting

**"No .mcp.json found"**
Make sure you have a `.mcp.json` in your project root (or a parent directory) and that you're running Claude Code from within that project.

**"No session ID in response"**
The MCP server didn't return a session header. Check that:
- The MCP Tools for Elementor plugin is activated
- Your URL is correct (`/wp-json/mcp/elementor-mcp-server`)
- Your credentials are valid

**"curl failed"**
Ensure `curl` is available in your PATH. On Windows, Git Bash includes curl.

**Connection timeout**
The default timeout is 30 seconds (60 for tool calls). If your server is slow, the script will retry automatically on the next call.

## Contributing

Contributions welcome! Some ideas:

- Add support for more MCP transports (SSE, stdio)
- Cache session IDs across calls for faster sequential operations
- Add a `--dry-run` mode that shows what would be sent
- Support for additional WordPress MCP plugins

## License

MIT

## Credits

- [MCP Tools for Elementor](https://github.com/msrbuilds/elementor-mcp) by MSR Builds — the WordPress plugin that exposes Elementor as MCP tools
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) by Anthropic — the AI coding assistant that uses this skill
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) — the open protocol connecting AI to tools
