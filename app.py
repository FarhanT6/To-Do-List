import os
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import logging
from logging.handlers import RotatingFileHandler
import secrets

app = Flask(__name__)
# Generate a secure secret key for production
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

# Configure logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/todo.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Todo startup')

# Initialize SQLite database
def init_db():
    try:
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tasks 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      task TEXT NOT NULL, 
                      completed BOOLEAN NOT NULL DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
        app.logger.info('Database initialized successfully')
    except Exception as e:
        app.logger.error(f'Database initialization failed: {e}')
        raise

init_db()

@app.route('/')
def index():
    try:
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute('SELECT * FROM tasks ORDER BY created_at DESC')
        tasks = c.fetchall()
        conn.close()
        return render_template('index.html', tasks=tasks)
    except Exception as e:
        app.logger.error(f'Error fetching tasks: {e}')
        flash('Error loading tasks', 'error')
        return render_template('index.html', tasks=[])

@app.route('/add', methods=['POST'])
def add_task():
    task = request.form.get('task', '').strip()
    if not task:
        flash('Task cannot be empty', 'error')
        return redirect(url_for('index'))
    
    if len(task) > 500:  # Basic input validation
        flash('Task is too long (max 500 characters)', 'error')
        return redirect(url_for('index'))
    
    try:
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute('INSERT INTO tasks (task, completed) VALUES (?, ?)', (task, False))
        conn.commit()
        conn.close()
        app.logger.info(f'Task added: {task[:50]}...')
        flash('Task added successfully!', 'success')
    except Exception as e:
        app.logger.error(f'Error adding task: {e}')
        flash('Error adding task', 'error')
    
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    try:
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute('UPDATE tasks SET completed = ? WHERE id = ?', (True, task_id))
        conn.commit()
        conn.close()
        app.logger.info(f'Task completed: {task_id}')
        flash('Task marked as complete!', 'success')
    except Exception as e:
        app.logger.error(f'Error completing task: {e}')
        flash('Error updating task', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    try:
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
        app.logger.info(f'Task deleted: {task_id}')
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        app.logger.error(f'Error deleting task: {e}')
        flash('Error deleting task', 'error')
    
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)