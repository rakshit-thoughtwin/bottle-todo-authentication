import bottle

app = bottle.Bottle()

users = {}

tasks = {}

def is_logged_in():
    session_cookie = bottle.request.get_cookie('session')
    return session_cookie is not None and session_cookie in users

def get_current_user():
    return bottle.request.get_cookie('session')

@app.route('/static/<filename>')
def serve_static(filename):
    return bottle.static_file(filename, root='./static/')


@app.route('/register')
def register():
    return bottle.template('register')

@app.route('/register', method='POST')
def do_register():
    username = bottle.request.forms.get('username')
    password = bottle.request.forms.get('password')

    if username in users:
        return 'Username already exists. Please choose a different one.'

    users[username] = password
    tasks[username] = []
    bottle.response.set_cookie('session', username, path='/')
    bottle.redirect('/')


@app.route('/login')
def login():
    return bottle.template('login')

@app.route('/login', method='POST')
def do_login():
    username = bottle.request.forms.get('username')
    password = bottle.request.forms.get('password')

    if users.get(username) == password:
        bottle.response.set_cookie('session', username, path='/')
        bottle.redirect('/')

    return 'Login failed.'


@app.route('/logout')
def logout():
    bottle.response.delete_cookie('session', path='/')
    bottle.redirect('/')


@app.route('/add', method='POST')
def add_task():
    if is_logged_in():
        username = get_current_user()
        task = bottle.request.forms.get('task')

        if task:
            user_tasks = tasks.get(username, [])
            user_tasks.append(task)
            tasks[username] = user_tasks

        bottle.redirect('/')
    else:
        bottle.redirect('/login')


@app.route('/delete/<task_index>')
def delete_task(task_index):
    if is_logged_in():
        username = get_current_user()
        user_tasks = tasks.get(username, [])

        try:
            task_index = int(task_index)
            if 0 <= task_index < len(user_tasks):
                del user_tasks[task_index]
                tasks[username] = user_tasks
        except ValueError:
            pass  

        bottle.redirect('/')

def render_template(template_name, **kwargs):
    kwargs['get_current_user'] = get_current_user
    return bottle.template(template_name, **kwargs)

@app.route('/')
def todo_list():
    if is_logged_in():
        username = get_current_user()
        user_tasks = tasks.get(username, [])
        return render_template('todo', user_tasks=user_tasks)
    else:
        bottle.redirect('/login')

if __name__ == '__main__':
    bottle.run(app, host='localhost', port=8080, reloader=True)
