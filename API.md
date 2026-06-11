# Mr. Fridge — API Reference

> **Base URL (local):** `http://127.0.0.1:8000`  
> **Interactive Docs:** `http://127.0.0.1:8000/docs` (Swagger UI)  
> **Alternative Docs:** `http://127.0.0.1:8000/redoc` (ReDoc)

All request and response bodies use **JSON**. Timestamps follow ISO 8601 (UTC).

---

## Table of Contents

- [Health Check](#-health-check)
- [Camera — Vision AI](#-camera--vision-ai)
  - [POST /camera/scan](#post-camerascan)
- [Inventory](#-inventory)
  - [POST /inventory/add](#post-inventoryadd)
  - [GET /inventory/{fridge_id}/items](#get-inventoryfridge_iditems)
  - [GET /inventory/{fridge_id}/categorized](#get-inventoryfridge_idcategorized)
  - [DELETE /inventory/delete/{item_id}](#delete-inventorydeletitem_id)
- [Recipe](#-recipe)
  - [POST /recipe/generate](#post-recipegenerate)
- [Settings](#-settings)
  - [GET /settings/api-key](#get-settingsapi-key)
  - [POST /settings/api-key](#post-settingsapi-key)
  - [DELETE /settings/api-key](#delete-settingsapi-key)
- [Error Handling](#-error-handling)
- [Data Models](#-data-models)

---

## 🟢 Health Check

### `GET /`

Returns a simple status message to verify the backend is running.

**Response `200 OK`**
```json
{
  "message": "Welcome to the Mr.Fridge Backend! (Async Version Active)"
}
```

---

## 📷 Camera — Vision AI

### `POST /camera/scan`

Accepts a **base64-encoded JPEG image** and uses **GPT-4o Vision** to identify the food item in the frame. The image is automatically compressed to 512×512 px before being sent to the OpenAI API to minimize latency and cost.

**Request Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `base64_image` | `string` | ✅ | Base64-encoded JPEG image (no `data:` prefix needed) |

```json
{
  "base64_image": "/9j/4AAQSkZJRgABAQAA..."
}
```

**Response `200 OK`**

| Field | Type | Description |
|---|---|---|
| `name` | `string` | Identified item name (e.g. `"Tomato"`) |
| `category` | `string` | Auto-assigned category (e.g. `"Vegetable"`) |

```json
{
  "name": "Tomato",
  "category": "Vegetable"
}
```

**Category mapping** (rule-based, applied after AI identification):

| Category | Example Items |
|---|---|
| `Dairy` | Milk, Yogurt, Cheese, Butter, Cream |
| `Fruit` | Apple, Banana, Orange, Strawberry, Grape |
| `Vegetable` | Tomato, Cucumber, Pepper, Broccoli, Carrot |
| `Meat & Fish` | Chicken, Ground Beef, Fish, Sausage |
| `Staples` | Egg, Bread, Pasta, Rice, Flour |
| `Beverage` | Juice, Soda, Water |
| `Other` | Anything that doesn't match above |

**Error Responses**

| Status | Condition |
|---|---|
| `400 Bad Request` | `base64_image` field is empty |
| `400 Bad Request` | OpenAI API key is missing or invalid |
| `500 Internal Server Error` | Unexpected server-side error |

```json
{
  "detail": "base64_image field cannot be empty."
}
```

---

## 📦 Inventory

All inventory endpoints operate on a **fridge** identified by `fridge_id`. The default fridge created at startup has `fridge_id = 1`.

---

### `POST /inventory/add`

Adds a new food item to the specified fridge's inventory.

**Request Body**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `fridge_id` | `integer` | ✅ | — | Target fridge identifier |
| `name` | `string` | ✅ | — | Item name (auto title-cased, trimmed) |
| `category` | `string` | ❌ | `"Other"` | Item category |

```json
{
  "fridge_id": 1,
  "name": "tomato",
  "category": "Vegetable"
}
```

**Response `200 OK`**

```json
{
  "status": "success",
  "message": "Tomato has been added to the inventory."
}
```

> **Note:** The `name` field is automatically normalized to Title Case (e.g. `"green apple"` → `"Green Apple"`).

**Error Responses**

| Status | Condition |
|---|---|
| `422 Unprocessable Entity` | Missing required fields or wrong types |

---

### `GET /inventory/{fridge_id}/items`

Returns **all items** in the specified fridge as a flat list. Primarily used by the Inventory screen and Home screen to display and manage items.

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `fridge_id` | `integer` | Fridge identifier |

**Response `200 OK`**

An array of item objects:

| Field | Type | Description |
|---|---|---|
| `id` | `integer` | Unique item ID (used for deletion) |
| `name` | `string` | Item name |
| `category` | `string` | Item category (`"Other"` if null) |

```json
[
  { "id": 1, "name": "Tomato",    "category": "Vegetable" },
  { "id": 2, "name": "Milk",      "category": "Dairy" },
  { "id": 3, "name": "Chicken",   "category": "Meat & Fish" }
]
```

Returns `[]` (empty array) if the fridge has no items.

---

### `GET /inventory/{fridge_id}/categorized`

Returns items **grouped by category**. This endpoint is optimized with a **60-second in-memory cache** — the cache is invalidated automatically whenever an item is added or deleted.

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `fridge_id` | `integer` | Fridge identifier |

**Response `200 OK`**

A dictionary mapping category names to lists of item names:

```json
{
  "Dairy":       ["Cheese", "Milk", "Yogurt"],
  "Fruit":       ["Apple", "Banana"],
  "Meat & Fish": ["Chicken"],
  "Vegetable":   ["Carrot", "Tomato"]
}
```

Returns `{}` (empty object) if the fridge has no items.

> **Used by:** Recipe screen — populates the ingredient selection list.

---

### `DELETE /inventory/delete/{item_id}`

Permanently removes an item from the inventory by its ID.

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `item_id` | `integer` | ID of the item to delete |

**Response `200 OK`**

```json
{
  "status": "success",
  "message": "Item (id=42) has been deleted."
}
```

**Error Responses**

| Status | Condition |
|---|---|
| `404 Not Found` | No item found with the given `item_id` |

```json
{
  "detail": "Item not found."
}
```

---

## 🍳 Recipe

### `POST /recipe/generate`

Sends the selected ingredients to **GPT-4o** and streams back a creative, step-by-step recipe using **Server-Sent Events (SSE)**. The response is streamed token-by-token for a real-time feel.

**Request Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `ingredients` | `string[]` | ✅ | List of ingredient names to cook with |

```json
{
  "ingredients": ["Tomato", "Cheese", "Egg", "Pasta"]
}
```

**Response `200 OK`** — `Content-Type: text/event-stream`

The response body is a plain text stream. Each chunk is a fragment of the recipe text:

```
Tomato Egg Pasta Bake

Prep time: ~20 minutes

Ingredients:
- 2 tomatoes
- 1 cup pasta (cooked)
...
```

> **Client guidance:** Consume the stream with `requests.iter_content()` or similar. The frontend uses this approach in `api_client.generate_recipe_stream()`.

**Edge cases**

| Condition | Behavior |
|---|---|
| Empty `ingredients` list | Stream yields: `"You must select at least one ingredient to generate a recipe."` |
| OpenAI API error | Stream yields an error message: `"\n[Error: ...]"` |

---

## ⚙️ Settings

Manage the OpenAI API key used by the backend. The key is persisted to `backend/.env` and takes effect immediately without restarting the server.

---

### `GET /settings/api-key`

Returns the current API key status. **The key value itself is never exposed** — only a masked version is returned.

**Response `200 OK`**

| Field | Type | Description |
|---|---|---|
| `status` | `string` | Always `"ok"` |
| `has_key` | `boolean` | Whether a valid key is configured |
| `masked_key` | `string` | Last 4 chars only, e.g. `"sk-...X4bF"` or `"—"` |
| `message` | `string` | Human-readable status message |

```json
{
  "status": "ok",
  "has_key": true,
  "masked_key": "sk-...X4bF",
  "message": "API key is configured."
}
```

---

### `POST /settings/api-key`

Sets or replaces the OpenAI API key. The key is written to `backend/.env` and all in-memory clients are re-initialized immediately.

**Request Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `api_key` | `string` | ✅ | Your OpenAI API key (must be ≥ 20 characters) |

```json
{
  "api_key": "sk-proj-..."
}
```

**Response `200 OK`**

```json
{
  "status": "ok",
  "has_key": true,
  "masked_key": "sk-...X4bF",
  "message": "API key saved successfully!"
}
```

**Error Responses**

| Status | Condition |
|---|---|
| `400 Bad Request` | `api_key` is empty |
| `400 Bad Request` | `api_key` is shorter than 20 characters |

```json
{
  "detail": "API key cannot be empty."
}
```

---

### `DELETE /settings/api-key`

Removes the stored API key. After this call, camera scanning and recipe generation will fail until a new key is provided.

**Response `200 OK`**

```json
{
  "status": "ok",
  "has_key": false,
  "masked_key": "—",
  "message": "API key has been deleted."
}
```

---

## ❌ Error Handling

The API uses two global exception handlers:

### Application Errors (`MrFridgeException`)

Intentionally raised errors with structured context:

```json
{
  "status": "error",
  "error_type": "ValidationError",
  "message": "A human-readable description of what went wrong."
}
```

### Unexpected Errors

```json
{
  "status": "fatal_error",
  "error_type": "InternalServerError",
  "message": "An unexpected error occurred on the server.",
  "details": "<exception details — visible in development>"
}
```

> **Standard HTTP errors** (e.g. `404`, `422`) use FastAPI's default response format with a `"detail"` field.

---

## 📐 Data Models

### `Fridge`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `INTEGER` | PK, auto-increment | Unique fridge identifier |
| `name` | `VARCHAR` | NOT NULL | Display name |
| `created_at` | `DATETIME` | default: now (UTC) | Creation timestamp |

### `Item`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `INTEGER` | PK, auto-increment | Unique item identifier |
| `fridge_id` | `INTEGER` | FK → `fridges.id` CASCADE | Owner fridge |
| `name` | `VARCHAR` | NOT NULL, indexed | Item name (Title Case) |
| `category` | `VARCHAR` | nullable | Category label |
| `added_at` | `DATETIME` | default: now (UTC) | When the item was added |

### Request Schemas

**`ItemCreateRequest`**
```json
{
  "fridge_id": 1,
  "name": "Milk",
  "category": "Dairy"
}
```

**`RecipeGenerateRequest`**
```json
{
  "ingredients": ["Milk", "Egg", "Butter"]
}
```

**`ScanRequest`** *(camera)*
```json
{
  "base64_image": "<base64 string>"
}
```

**`ApiKeyRequest`** *(settings)*
```json
{
  "api_key": "sk-proj-..."
}
```

---

## 🔒 Security Notes

- The OpenAI API key is stored in `backend/.env`. **Never commit `.env` to version control** — it is listed in `.gitignore`.
- The `GET /settings/api-key` endpoint intentionally returns only the last 4 characters of the key (`masked_key`) to prevent accidental exposure.
- A key is considered valid if it is longer than 20 characters and does not start with `"sk-test"`.
