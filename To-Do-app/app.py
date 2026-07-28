from flask import Flask, render_template_string, request, redirect, url_for
import json
import os

app = Flask(__name__)

# The JSON file location is read from an environment variable, defaulting to todos.json
TODO_FILE = os.getenv("TODO_FILE", "todos.json")

def load_todos():
    """Load todos from the JSON file. Return empty list if file doesn't exist."""
    if not os.path.exists(TODO_FILE):
        return []
    try:
        with open(TODO_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_todos(todos):
    """Write the updated list of todos to the JSON file."""
    # Ensure the parent directory exists if it doesn't
    parent_dir = os.path.dirname(TODO_FILE)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=4)

# Embedded HTML Template for a clean, single-file beginner project
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>To-Do App</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 500px;
            margin: 50px auto;
            padding: 25px;
            background-color: #f8f9fa;
            color: #333;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            color: #495057;
            margin-bottom: 25px;
        }
        form {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
        }
        form input[type="text"] {
            flex: 1;
            padding: 12px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 16px;
        }
        form button {
            padding: 12px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        form button:hover {
            background-color: #0056b3;
        }
        .todo-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background-color: white;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .completed {
            text-decoration: line-through;
            color: #6c757d;
        }
        .actions {
            display: flex;
            gap: 12px;
        }
        .btn-toggle {
            color: #28a745;
            text-decoration: none;
            font-weight: 600;
        }
        .btn-toggle:hover {
            text-decoration: underline;
        }
        .btn-delete {
            color: #dc3545;
            text-decoration: none;
            font-weight: 600;
        }
        .btn-delete:hover {
            text-decoration: underline;
        }
        .empty-text {
            text-align: center;
            color: #868e96;
            font-style: italic;
        }
    </style>
</head>
<body>
    <h1>My To-Do List</h1>
    
    <!-- Add Form -->
    <form action="/add" method="POST">
        <input type="text" name="title" placeholder="What do you need to do?" required autocomplete="off">
        <button type="submit">Add Task</button>
    </form>
    
    <!-- Todo List items -->
    <div>
        {% for todo in todos %}
            <div class="todo-item">
                <span class="{% if todo.completed %}completed{% endif %}">{{ todo.title }}</span>
                <div class="actions">
                    <a href="/toggle/{{ todo.id }}" class="btn-toggle">
                        {% if todo.completed %}Undo{% else %}Complete{% endif %}
                    </a>
                    <a href="/delete/{{ todo.id }}" class="btn-delete">Delete</a>
                </div>
            </div>
        {% else %}
            <p class="empty-text">No tasks created yet! Add one above.</p>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    todos = load_todos()
    return render_template_string(HTML_TEMPLATE, todos=todos)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    if title:
        todos = load_todos()
        # Find next ID
        next_id = max([todo["id"] for todo in todos], default=0) + 1
        new_todo = {
            "id": next_id,
            "title": title,
            "completed": False
        }
        todos.append(new_todo)
        save_todos(todos)
    return redirect(url_for("index"))

@app.route("/toggle/<int:todo_id>")
def toggle(todo_id):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["completed"] = not todo["completed"]
            break
    save_todos(todos)
    return redirect(url_for("index"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todos = load_todos()
    todos = [todo for todo in todos if todo["id"] != todo_id]
    save_todos(todos)
    return redirect(url_for("index"))

if __name__ == "__main__":
    # Runs the server on port 5000 and accepts traffic from all network interfaces
    app.run(host="0.0.0.0", port=9000)
