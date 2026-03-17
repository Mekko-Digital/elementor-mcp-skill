---
name: elementor-mcp
description: Build and manage Elementor pages on any WordPress site via MCP. Use when user asks to create pages, add widgets, update designs, manage templates, or modify any Elementor content. Reads connection from the project's .mcp.json automatically.
allowed-tools: Bash(bash *)
---

# Elementor MCP Skill (Universal)

Controls any WordPress site's Elementor page builder via its MCP server. Reads connection config from the project's `.mcp.json` automatically — works on any WordPress project.

## Setup for a New WordPress Project

Add a `.mcp.json` in the project root:
```json
{
  "mcpServers": {
    "elementor-mcp": {
      "type": "http",
      "url": "https://YOURSITE.com/wp-json/mcp/elementor-mcp-server",
      "headers": {
        "Authorization": "Basic BASE64_ENCODED_CREDENTIALS"
      }
    }
  }
}
```

Generate credentials: In WordPress, go to Users > Your Profile > Application Passwords. Create one, then base64-encode `username:password`.

**Add `.mcp.json` to `.gitignore`** (contains auth credentials).

## How to Call

The `SKILL_DIR` placeholder below refers to wherever you installed this skill (e.g. `~/.claude/skills/elementor-mcp`).

```bash
python SKILL_DIR/scripts/elementor-mcp.py --tool TOOL_NAME --params 'JSON' --pretty
```

**Always use `--pretty` for readable output.**

The script auto-detects the `.mcp.json` by searching the current directory and parents. To target a specific project:
```bash
python SKILL_DIR/scripts/elementor-mcp.py --project-dir /path/to/project --tool ...
```

If multiple MCP servers exist in `.mcp.json`, specify which one:
```bash
python SKILL_DIR/scripts/elementor-mcp.py --server elementor-mcp --tool ...
```

## Quick Reference

### List all tools
```bash
python SKILL_DIR/scripts/elementor-mcp.py --list
```

---

## Tool Categories & Usage

### 1. DISCOVERY (read-only)

| Tool | Params | Description |
|------|--------|-------------|
| `elementor-mcp-list-pages` | `post_type?`, `status?` | List all Elementor pages |
| `elementor-mcp-list-widgets` | `category?` | List all widget types |
| `elementor-mcp-list-templates` | `template_type?` | List saved templates |
| `elementor-mcp-get-page-structure` | `post_id` (int, req) | Get element tree of a page |
| `elementor-mcp-get-element-settings` | `post_id` (int, req), `element_id` (str, req) | Get settings of an element |
| `elementor-mcp-get-widget-schema` | `widget_type` (str, req) | Get full schema for a widget type |
| `elementor-mcp-get-container-schema` | (none) | Get container settings schema |
| `elementor-mcp-get-global-settings` | (none) | Get site-wide colors/typography |
| `elementor-mcp-find-element` | `post_id` (int, req), `widget_type?`, `element_type?`, `search_text?`, `setting_key?`, `setting_value?` | Search elements on a page |
| `elementor-mcp-list-dynamic-tags` | `group?` | List dynamic tags |
| `elementor-mcp-list-code-snippets` | `location?`, `status?` | List custom code snippets |

**Example - List all pages:**
```bash
python SKILL_DIR/scripts/elementor-mcp.py --tool elementor-mcp-list-pages --pretty
```

**Example - Get page structure:**
```bash
python SKILL_DIR/scripts/elementor-mcp.py --tool elementor-mcp-get-page-structure --params '{"post_id": 123}' --pretty
```

### 2. PAGE MANAGEMENT

| Tool | Key Params | Description |
|------|-----------|-------------|
| `elementor-mcp-create-page` | `title` (req), `status?` (draft/publish), `post_type?`, `template?`, `content?` | Create new page |
| `elementor-mcp-update-page-settings` | `post_id` (req), `settings` (req) | Update page settings |
| `elementor-mcp-delete-page-content` | `post_id` (req) | Clear all content from page |
| `elementor-mcp-export-page` | `post_id` (req) | Export page as JSON |
| `elementor-mcp-import-template` | `post_id` (req), `template_json` (req), `position?` | Import JSON template into page |

**Example - Create a draft page:**
```bash
python SKILL_DIR/scripts/elementor-mcp.py --tool elementor-mcp-create-page --params '{"title": "New Landing Page", "status": "draft"}' --pretty
```

### 3. BUILD FULL PAGE (single call)

The most powerful tool - builds a complete page from a declarative structure:

```bash
python SKILL_DIR/scripts/elementor-mcp.py --tool elementor-mcp-build-page --params '{
  "title": "Landing Page",
  "status": "draft",
  "structure": [
    {
      "type": "container",
      "settings": {"flex_direction": "column", "padding": {"top": "60", "bottom": "60", "left": "20", "right": "20", "unit": "px"}},
      "children": [
        {"type": "widget", "widget_type": "heading", "settings": {"title": "Welcome", "header_size": "h1", "align": "center"}},
        {"type": "widget", "widget_type": "text-editor", "settings": {"editor": "<p>Your content here</p>", "align": "center"}}
      ]
    }
  ]
}' --pretty
```

### 4. CONTAINERS (layout)

| Tool | Key Params | Description |
|------|-----------|-------------|
| `elementor-mcp-add-container` | `post_id` (req), `parent_id?`, `position?`, `settings?` | Add container |
| `elementor-mcp-update-container` | `post_id` (req), `element_id` (req), `settings` (req) | Update container |

**Container settings:** `flex_direction`, `flex_wrap`, `justify_content`, `align_items`, `gap`, `content_width`, `padding`, `margin`, `background_*`, `border_*`, `min_height`, `container_type` (flex/grid)

**Example - Add a flex row container:**
```bash
python SKILL_DIR/scripts/elementor-mcp.py --tool elementor-mcp-add-container --params '{"post_id": 123, "settings": {"flex_direction": "row", "justify_content": "space-between", "gap": {"size": 20, "unit": "px"}}}' --pretty
```

### 5. COMMON WIDGETS

#### Heading
```bash
--tool elementor-mcp-add-heading --params '{
  "post_id": 123, "parent_id": "abc123",
  "title": "Hello World", "header_size": "h2", "align": "center",
  "title_color": "#333333",
  "typography_typography": "custom", "typography_font_size": {"size": 36, "unit": "px"}
}'
```

#### Text Editor (rich text)
```bash
--tool elementor-mcp-add-text-editor --params '{
  "post_id": 123, "parent_id": "abc123",
  "editor": "<p>Rich <strong>HTML</strong> content</p>",
  "align": "center", "text_color": "#666666"
}'
```

#### Image
```bash
--tool elementor-mcp-add-image --params '{
  "post_id": 123, "parent_id": "abc123",
  "image": {"url": "https://example.com/photo.jpg"},
  "image_size": "large", "align": "center"
}'
```

#### Button
```bash
--tool elementor-mcp-add-button --params '{
  "post_id": 123, "parent_id": "abc123",
  "text": "Get Started", "link": {"url": "/contact"},
  "size": "lg", "align": "center",
  "button_text_color": "#FFFFFF", "background_color": "#2563EB"
}'
```

#### Icon Box
```bash
--tool elementor-mcp-add-icon-box --params '{
  "post_id": 123, "parent_id": "abc123",
  "title_text": "Fast Delivery",
  "description_text": "We deliver within 24 hours",
  "selected_icon": {"value": "fas fa-truck", "library": "fa-solid"}
}'
```

#### Form (Pro)
```bash
--tool elementor-mcp-add-form --params '{
  "post_id": 123, "parent_id": "abc123",
  "form_name": "Contact Form",
  "form_fields": [
    {"field_type": "text", "field_label": "Name", "required": "true"},
    {"field_type": "email", "field_label": "Email", "required": "true"},
    {"field_type": "textarea", "field_label": "Message"}
  ],
  "button_text": "Send",
  "submit_actions": ["email"],
  "email_to": "you@example.com"
}'
```

### 6. MORE WIDGETS (all follow same pattern: post_id + parent_id + settings)

| Tool | Key Settings |
|------|-------------|
| `elementor-mcp-add-video` | `video_type`, `youtube_url` / `vimeo_url` |
| `elementor-mcp-add-icon` | `selected_icon` ({value, library}), `view`, `primary_color` |
| `elementor-mcp-add-spacer` | `space` ({size, unit}) |
| `elementor-mcp-add-divider` | `style`, `weight`, `color`, `width` |
| `elementor-mcp-add-accordion` | `tabs` ([{tab_title, tab_content}]) |
| `elementor-mcp-add-tabs` | `tabs` ([{tab_title, tab_content}]), `type` (horizontal/vertical) |
| `elementor-mcp-add-toggle` | `tabs` ([{tab_title, tab_content}]) |
| `elementor-mcp-add-counter` | `ending_number`, `prefix`, `suffix`, `title` |
| `elementor-mcp-add-progress` | `title`, `percent`, `progress_type` |
| `elementor-mcp-add-testimonial` | `testimonial_content`, `testimonial_name`, `testimonial_job` |
| `elementor-mcp-add-social-icons` | `social_icon_list` ([{social_icon, link}]) |
| `elementor-mcp-add-icon-list` | `icon_list` ([{text, selected_icon, link}]) |
| `elementor-mcp-add-image-box` | `image`, `title_text`, `description_text` |
| `elementor-mcp-add-image-carousel` | `carousel` ([{url, id}]), `slides_to_show` |
| `elementor-mcp-add-google-maps` | `address`, `zoom`, `height` |
| `elementor-mcp-add-alert` | `alert_type`, `alert_title`, `alert_description` |
| `elementor-mcp-add-star-rating` | `rating`, `rating_scale` |
| `elementor-mcp-add-html` | `html` (raw HTML string) |
| `elementor-mcp-add-shortcode` | `shortcode` |
| `elementor-mcp-add-menu-anchor` | `anchor` |

### 7. PRO WIDGETS

| Tool | Key Settings |
|------|-------------|
| `elementor-mcp-add-posts-grid` | `posts_post_type`, `posts_per_page`, `columns` |
| `elementor-mcp-add-countdown` | `countdown_type`, `due_date` (Y-m-d H:i) |
| `elementor-mcp-add-price-table` | `heading`, `price`, `currency_symbol`, `features_list`, `button_text` |
| `elementor-mcp-add-flip-box` | `title_text_a`, `title_text_b`, `flip_effect` |
| `elementor-mcp-add-animated-headline` | `headline_style`, `before_text`, `highlighted_text`/`rotating_text` |
| `elementor-mcp-add-call-to-action` | `title`, `description`, `button`, `link` |
| `elementor-mcp-add-slides` | `slides` ([{heading, description, button_text, background_image}]) |
| `elementor-mcp-add-testimonial-carousel` | `slides` ([{content, image, name, title}]) |
| `elementor-mcp-add-price-list` | `price_list` ([{title, price, item_description}]) |
| `elementor-mcp-add-gallery` | `gallery` ([{id, url}]), `gallery_layout` |
| `elementor-mcp-add-blockquote` | `blockquote_content`, `author_name` |
| `elementor-mcp-add-lottie` | `source_external_url`, `trigger` |
| `elementor-mcp-add-hotspot` | `image`, `hotspot` (array of hotspot points) |
| `elementor-mcp-add-nav-menu` | `menu_name`, `layout` |
| `elementor-mcp-add-loop-grid` | `template_id`, `columns`, `posts_per_page` |
| `elementor-mcp-add-loop-carousel` | `template_id`, `slides_to_show` |
| `elementor-mcp-add-nested-tabs` | `tabs_direction` |
| `elementor-mcp-add-nested-accordion` | `title_tag`, `faq_schema` |
| `elementor-mcp-add-share-buttons` | `share_buttons` ([{button, text}]) |
| `elementor-mcp-add-table-of-contents` | `title`, `headings_by_tags` |
| `elementor-mcp-add-media-carousel` | `slides`, `skin`, `effect` |

### 8. WOOCOMMERCE WIDGETS

| Tool | Key Settings |
|------|-------------|
| `elementor-mcp-add-wc-products` | `columns`, `rows`, `orderby`, `order` |
| `elementor-mcp-add-wc-add-to-cart` | `product_id`, `show_quantity` |
| `elementor-mcp-add-wc-cart` | (none) |
| `elementor-mcp-add-wc-checkout` | (none) |
| `elementor-mcp-add-wc-menu-cart` | `icon`, `items_indicator` |

### 9. ELEMENT OPERATIONS

| Tool | Key Params | Description |
|------|-----------|-------------|
| `elementor-mcp-update-element` | `post_id`, `element_id`, `settings` | Update any element |
| `elementor-mcp-update-widget` | `post_id`, `element_id`, `settings` | Update widget settings |
| `elementor-mcp-batch-update` | `post_id`, `operations` ([{element_id, settings}]) | Batch update multiple elements |
| `elementor-mcp-remove-element` | `post_id`, `element_id` | Delete element |
| `elementor-mcp-duplicate-element` | `post_id`, `element_id` | Duplicate element |
| `elementor-mcp-move-element` | `post_id`, `element_id`, `target_parent_id`, `position` | Move element |
| `elementor-mcp-reorder-elements` | `post_id`, `container_id`, `element_ids` (ordered array) | Reorder children |

### 10. TEMPLATES & THEME BUILDER

```bash
# Save element as template
--tool elementor-mcp-save-as-template --params '{"post_id": 123, "title": "My Header", "template_type": "container"}'

# Apply template to page
--tool elementor-mcp-apply-template --params '{"post_id": 123, "template_id": 456}'

# Create theme template (header/footer/single/archive)
--tool elementor-mcp-create-theme-template --params '{"title": "Site Header", "template_type": "header"}'

# Set display conditions
--tool elementor-mcp-set-template-conditions --params '{"post_id": 789, "conditions": [["include", "general"]]}'

# Set dynamic tag on element
--tool elementor-mcp-set-dynamic-tag --params '{"post_id": 123, "element_id": "abc", "setting_key": "title", "tag_name": "post-title"}'
```

### 11. POPUPS

```bash
# Create popup
--tool elementor-mcp-create-popup --params '{"title": "Welcome Popup"}'

# Configure popup triggers/conditions
--tool elementor-mcp-set-popup-settings --params '{"post_id": 123, "triggers": {"on_page_load": true}, "conditions": [["include", "general"]]}'
```

### 12. GLOBAL DESIGN

```bash
# Update global colors
--tool elementor-mcp-update-global-colors --params '{"colors": [{"_id": "primary", "title": "Primary", "color": "#2563EB"}]}'

# Update global typography
--tool elementor-mcp-update-global-typography --params '{"typography": [{"_id": "primary", "title": "Primary", "typography_font_family": "Inter"}]}'
```

### 13. IMAGES & MEDIA

```bash
# Search free images (Openverse/CC)
--tool elementor-mcp-search-images --params '{"query": "mountain landscape", "page_size": 5}'

# Download image to Media Library
--tool elementor-mcp-sideload-image --params '{"url": "https://example.com/photo.jpg", "title": "Mountain", "alt_text": "Mountain landscape"}'

# Search + add image in one step
--tool elementor-mcp-add-stock-image --params '{"post_id": 123, "parent_id": "abc", "query": "modern office"}'

# Upload SVG icon
--tool elementor-mcp-upload-svg-icon --params '{"svg_content": "<svg>...</svg>", "title": "Custom Icon"}'
```

### 14. CUSTOM CODE

```bash
# Add JS to a page
--tool elementor-mcp-add-custom-js --params '{"post_id": 123, "parent_id": "abc", "js": "console.log(\"hello\");", "wrap_dom_ready": true}'

# Add CSS to element or page
--tool elementor-mcp-add-custom-css --params '{"post_id": 123, "element_id": "abc", "css": "selector { color: red; }"}'

# Add site-wide code snippet
--tool elementor-mcp-add-code-snippet --params '{"title": "GA4 Tracking", "code": "<script>...</script>", "location": "head", "status": "publish"}'
```

---

## Workflow Patterns

### Pattern 1: Inspect before editing
1. `list-pages` to find the page
2. `get-page-structure` to see elements
3. `get-element-settings` to inspect specific element
4. `update-element` or `update-widget` to modify

### Pattern 2: Build a new page
1. Use `build-page` for complete pages in a single call
2. Or: `create-page` -> `add-container` -> add widgets step by step

### Pattern 3: Discover widget options
1. `get-widget-schema --params '{"widget_type": "heading"}'` to see all available settings
2. Then use those settings in `add-heading` or `add-widget`

### Pattern 4: Typography (applies to all widgets with text)
Set `typography_typography` to `"custom"` first, then set individual properties:
```json
{
  "typography_typography": "custom",
  "typography_font_family": "Inter",
  "typography_font_size": {"size": 18, "unit": "px"},
  "typography_font_weight": "600",
  "typography_line_height": {"size": 1.6, "unit": "em"}
}
```

### Pattern 5: Responsive sizing
Objects with `size`+`unit` format:
```json
{"size": 20, "unit": "px"}
```

### Pattern 6: Links
```json
{"url": "https://example.com", "is_external": "true", "nofollow": "false"}
```

### Pattern 7: Icons (Font Awesome)
```json
{"value": "fas fa-check", "library": "fa-solid"}
```
Libraries: `fa-solid`, `fa-regular`, `fa-brands`
