from bottle import static_file, abort, error, redirect, route, request, response, template


@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)


@route('/object/<id:int>')
def callback(id):
    assert isinstance(id, int)


@route('/show/<name:re:[a-z]+>')
def callback(name):
    assert name.isalpha()


@route('/static/<path:path>')
def callback(path):
    return static_file(path, ...)


@route('/login')
def login():
    return '''
        <form action="/login" method="post">
            Username: <input name="username" type="text" />
            Password: <input name="password" type="password" />
            <input value="Login" type="submit" />
        </form>
    '''


@route('/login', method='POST')
def do_login():
    username = request.forms.username
    password = request.forms.password
    if check_login(username, password):
        return "<p>Your login information was correct.</p>"
    else:
        return "<p>Login failed.</p>"


@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='/path/to/your/static/files')


@route('/download/<filename>')
def download(filename):
    return static_file(filename, root='/path/to/static/files', download=f"download-{filename}")


@route('/iso')
def get_iso():
    response.charset = 'ISO-8859-15'
    return u'This will be sent with ISO-8859-15 encoding.'


@route('/latin9')
def get_latin():
    response.content_type = 'text/html; charset=latin9'
    return u'ISO-8859-15 is also known as latin9.'


@error(404)
def error404(error):
    return 'Nothing here, sorry'


@route('/restricted')
def restricted():
    abort(401, "Sorry, access denied.")


@route('/wiki/<page>')
def wiki(page):
    response.set_header('Content-Language', 'en')
    ...


@route('/wrong/url')
def wrong():
    redirect("/right/url")


@route('/hello')
def hello_again():
    if request.get_cookie("visited"):
        return "Welcome back! Nice to see you again"
    else:
        response.set_cookie("visited", "yes")
        return "Hello there! Nice to meet you"


@route('/login')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    if check_login(username, password):
        response.set_cookie("account", username, secret='some-secret-key')
        return template("<p>Welcome {{name}}! You are now logged in.</p>", name=username)
    else:
        return "<p>Login failed.</p>"


@route('/restricted')
def restricted_area():
    username = request.get_cookie("account", secret='some-secret-key')
    if username:
        return template("Hello {{name}}. Welcome back.", name=username)
    else:
        return "You are not logged in. Access denied."


@route('/hello')
def hello():
    name = request.cookies.username or 'Guest'
    return template('Hello {{name}}', name=name)


@route('/is_ajax')
def is_ajax():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return 'This is an AJAX request'
    else:
        return 'This is a normal request'


@route('/counter')
def counter():
    count = int(request.cookies.get('counter', '0'))
    count += 1
    response.set_cookie('counter', str(count))
    return 'You visited this page %d times' % count


@route('/forum')
def display_forum():
    forum_id = request.query.id
    page = request.query.page or '1'
    return template('Forum ID: {{id}} (page {{page}})', id=forum_id, page=page)


@route('/upload', method='POST')
def do_upload():
    category = request.forms.category
    upload = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)
    if ext not in ('.png', '.jpg', '.jpeg'):
        return 'File extension not allowed.'

    save_path = get_save_path_for_category(category)
    upload.save(save_path)  # appends upload.filename automatically
    return 'OK'


@route('/my_ip')
def show_ip():
    ip = request.environ.get('REMOTE_ADDR')
    # or ip = request.get('REMOTE_ADDR')
    # or ip = request['REMOTE_ADDR']
    return template("Your IP is: {{ip}}", ip=ip)


@route('/hello')
@route('/hello/<name>')
def hello(name='World'):
    return template('hello_template', name=name)


@route('/hello')
@route('/hello/<name>')
@view('hello_template')
def hello(name='World'):
    return dict(name=name)
