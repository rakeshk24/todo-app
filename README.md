# Todo List Web App

A simple and elegant web-based todo list application built with Python Flask.

## Features

- ✅ **CRUD Operations**: Create, read, update, and delete todos
- 📋 **Todo List**: View all your todos in an organized list
- ⏰ **Deadlines**: Add optional deadlines to your todos
- ✔️ **Completion Tracking**: Mark todos as done with a checkbox
- 📝 **Descriptions**: Add detailed descriptions to your todos
- 🎨 **Modern UI**: Clean and responsive design

## Project Structure

```
sample/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── static/
│   └── style.css      # CSS styling
└── templates/
    ├── index.html     # Main todo list page
    └── edit.html      # Edit todo page
```

## Installation & Setup

### 1. Install Dependencies

```bash
cd sample
pip install -r requirements.txt
```

<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:b01ebdff8dfc54d24b55d73bcbc01f7682f7668be4a8f007beb03d1bf7e7c1c8 -->

### 2. Configure and run

Set `TODO_API_KEY` in your secret configuration to a newly generated, unique secret. The application refuses to start without it. The previously published key is compromised: replace it in every deployment and update clients; never reuse it.

HTTPS is required by default. Terminate TLS at a trusted ingress that rejects cleartext requests and blocks direct access to the application. If TLS terminates at a proxy, set `TRUSTED_PROXY_HOPS` to the exact number of trusted proxies setting `X-Forwarded-Proto`; the ingress must overwrite untrusted forwarded headers. Leave it unset for direct HTTPS.

For local development only, set `ALLOW_INSECURE_HTTP=1`, then run `python app.py` and open `http://localhost:5001`. Do not enable this option in deployed environments.

### REST API

<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:9521c60d08c9d114b509d6018364228304762e3b5816c82870c45940cc1a4b01 -->

Send the configured key in the `X-API-Key` header over HTTPS. Encode the exact key as UTF-8 bytes in the header; clients and proxies must preserve those bytes without normalization or re-encoding. Clients that cannot send UTF-8 header bytes should use an ASCII key.

<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:1fa40bc27f9b54f8b8afcfea163e8deaf2e07fced3d74f6276aadebb0059b7ea -->

`GET /api/todos` returns a newest-first JSON array; `page` and `per_page` are positive integers, defaulting to 1 and 20, with a maximum page size of 100. `POST /api/todos` requires string `title` and `description` fields (use an empty description if needed); `deadline` is optional and uses `YYYY-MM-DDTHH:MM`. Invalid input returns JSON with status 400.

`GET /api/todos/<todo_id>` retrieves one todo. For example, replace the host, ID, and key in `curl https://your-domain.example/api/todos/123 -H "X-API-Key: <your-key>"`. A missing todo returns status 404 with JSON `{"error": "Todo not found"}`.

<!-- /coderabbit-ai-generated:v1 -->

<!-- /coderabbit-ai-generated:v1 -->

<!-- /coderabbit-ai-generated:v1 -->

## Usage

### Add a Todo
1. Enter a title (required)
2. Optionally add a description
3. Optionally set a deadline
4. Click "Add Todo"

### Toggle Completion
- Click the checkbox next to a todo to mark it as done/undone

### Edit a Todo
- Click the "Edit" button on any todo to modify it

### Delete a Todo
- Click the "Delete" button to remove a todo

## Database

The app uses SQLite for persistent storage. The database file (`todos.db`) is automatically created when you first run the app.

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3
- **Styling**: Responsive CSS with gradient design

## Notes

- The app uses SQLite which is file-based and requires no additional setup
- All todos are saved to the database automatically
- The app includes form validation and error handling
