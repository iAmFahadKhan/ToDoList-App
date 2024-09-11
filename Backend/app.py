from flask import Flask,jsonify, request, send_from_directory
import psycopg2
hostname = 'localhost'
username = 'postgres'
database = 'postgres'
pwd = '2715'
port_id = 5432

app = Flask(__name__)

def create_connection():
    try:
        conn = psycopg2.connect(
            host=hostname,
            dbname=database,
            user=username,
            password=pwd,
            port=port_id
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def get_connection():
    global connection
    if not connection:
        connection = create_connection()
    return connection

connection = None

@app.route('/todos', methods=['GET', 'POST'])
def get_all_todos():
    conn = get_connection()
    if conn is None:
        return jsonify({'message': 'Database connection error'}), 500
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute('SELECT * FROM todos')
        todos = cursor.fetchall()
        return jsonify(todos)
    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({'message': 'Missing required field: task'}), 400
        cursor.execute('INSERT INTO todos (task) VALUES (%s)', (data['task'],))
        conn.commit()
        new_todo_id = cursor.fetchone()[0]
        return jsonify({'id': new_todo_id}), 201

@app.route('/todos/<int:todo_id>', methods=['GET', 'PUT', 'DELETE'])
def get_update_delete_todo(todo_id):
    conn = get_connection()
    if conn is None:
        return jsonify({'message': 'Database connection error'}), 500
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM todos WHERE id = %s', (todo_id,))
        todo = cursor.fetchone()
        if not todo:
            return jsonify({'message': 'Todo not found'}), 404
        if request.method == 'GET':
            return jsonify(todo)
        elif request.method == 'PUT':
            data = request.get_json()
            if not data or 'task' not in data or not data['task']:
                return jsonify({'message': 'Missing required field: task'}), 400
            cursor.execute('UPDATE todos SET task = %s WHERE id = %s', (data['task'], todo_id))
            conn.commit()
            return jsonify({'message': 'Todo updated'})
        elif request.method == 'DELETE':
            cursor.execute('DELETE FROM todos WHERE id = %s', (todo_id,))
            conn.commit()
            return jsonify({'message': 'Todo deleted'}), 204
    except ValueError:
        return jsonify({'message': 'Invalid todo_id'}), 400

@app.teardown_appcontext
def close_connection(exception):
    global connection
    if connection:
        connection.close()
        connection = None

@app.route('/')
def index():
    return send_from_directory('../public', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)


   
    