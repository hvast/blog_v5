from flask import Flask,render_template,request,url_for,flash,redirect,session
import sqlite3,random,smtplib,datetime
from email.mime.text import MIMEText
from functools import wraps

# 定义博客系统的名称
app = Flask(__name__)
# 密钥
app.config['SECRET_KEY'] = 'This is a string used for encryption'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('您需要登录才能访问该页面。')
            return redirect(url_for('login'))  # 跳转到登录页面
        return f(*args, **kwargs)
    return decorated_function

# 定义函数，获得文章数据库链接
def get_db_connection():
    connection = sqlite3.connect("database.db")
    # 使从数据库取出的每条数据都可以当作字典使用
    connection.row_factory = sqlite3.Row
    return connection

# 根据post_id从数据库中获取post
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',(post_id,)).fetchone() # ？是占位符，需要将后面的元组填入其中
    connection.close()
    return post

# 定义函数，获得登录信息数据库链接
def get_userInfo_connection():
    user_connection = sqlite3.connect("userInfo.db")
    # 使从数据库取出的每条数据都可以当作字典使用
    user_connection.row_factory = sqlite3.Row
    return user_connection

# 根据username从数据库中获取uap
def get_user(username):   # 从数据库中查询用户名称和密码
    user_connection = get_userInfo_connection()
    user = user_connection.execute('SELECT * FROM userInfo WHERE username = ?',(username,)).fetchone() # ？是占位符，需要将后面的元组填入其中
    user_connection.close()
    return user

@app.route('/')
# 定义函数，一个函数代表一个网页页面
def welcome():
    return render_template('welcome.html')

# 邮箱验证码
send_by = ""
password = ""
mail_host = "smtp.qq.com"
port = 465

# 定义函数获取随机验证码
def code(n=4):
    s=''
    for i in range(n):
        number = random.randint(0,9)
        upper_alpha = chr(random.randint(65,90))
        lower_alpha = chr(random.randint(97,122))
        char = random.choice([number,upper_alpha,lower_alpha])
        s += str(char)
    return s
# 发送验证码
def send_email(send_to,content,subject='验证码'):
    message = MIMEText(content,'plain','utf-8')
    message['From'] = send_by
    message['To'] = send_to
    message['subject'] = subject
    smtp = smtplib.SMTP_SSL(mail_host,port,'utf-8')
    smtp.login(send_by,password)
    smtp.sendmail(send_by,send_to,message.as_string())
    print('发送成功！')
    print(content)
# 主函数（获取+发送
def send_email_code(send_to):
    verificate_code = code()
    content = str("【验证码】您的验证码是：") + verificate_code + ".如非本人操作，请忽略本条邮件"
    try:
        send_email(send_to=send_to,content=content)
        return verificate_code
    except Exception as error:
        print("发送验证码失败",error)
        return False
# 储存验证码
def store_verification_code(email, verificate_code):  
    with get_userInfo_connection() as conn:  
        cursor = conn.cursor()  
        #cursor.execute("DELETE FROM userInfo WHERE email = ?", (email,))  # 清除旧的验证码
        cursor.execute("UPDATE userInfo SET verificate_code = ?, verificate_code_created = ? WHERE email = ?", (verificate_code, datetime.datetime.now(), email))  
        conn.commit()
# 对比验证
def verify_code(email, input_verificate_code):  
    conn = sqlite3.connect('userInfo.db')  
    cursor = conn.cursor()  
    cursor.execute("SELECT verificate_code FROM userInfo WHERE email = ?", (email,))  
    record = cursor.fetchone()   
    if record is None:  
        return False  
    verificate_code = record[0] 
    if input_verificate_code == verificate_code:
        return True  
    else:  
        return False 
# 注册
def sign_up_user(username, password, email):
    with get_userInfo_connection() as conn:
        conn = get_userInfo_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO userInfo (username, password, email) VALUES (?, ?, ?)', (username, password, email))
        conn.commit()

   
@app.route('/verificate_code', methods=['POST'])
def verificate_code():
    email = request.form.get('email')
    if email:
        verificate_code = send_email_code(send_to=email)
        store_verification_code(email, verificate_code)
        flash(f"验证码发送成功，验证码为{verificate_code}.")
    else:
        flash("邮箱不能为空")
    return render_template('sign_up.html',email=email)

@app.route('/sign_up',methods=('GET','POST')) # 注册
def sign_up():
    email = request.args.get('email')
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        input_verificate_code = request.form.get('input_verificate_code')
        if not username:
            flash('用户名不能为空')
        elif not password:
            flash('密码不能为空')
        elif not email:
            flash('邮箱不能为空1')
        elif not input_verificate_code:
            flash('验证码不能为空')
        else:
            with get_userInfo_connection() as user_connection:
                user_cursor = user_connection.cursor()
                user_cursor.execute("SELECT * FROM userInfo WHERE email = ?", (email,))
                existing_email = user_cursor.fetchone()
                if existing_email:  
                    flash('用户已存在')
                elif not verify_code(email, input_verificate_code):
                    flash('验证码错误')
                else:
                    sign_up_user(username, password, email)
                    #session['username'] = username  
                    #session['logged_in'] = True  
                    flash('注册成功！')
                    # 重定向
                    return redirect(url_for('index'))
    return render_template('sign_up.html')       




@app.route('/login',methods=('GET','POST')) # 登录
def login():
    if request.method == "POST":
        user_connection = get_userInfo_connection()  
        cursor = user_connection.cursor()
        username = request.form['username'] # 接收form表单传参
        password = request.form['password']
        if not username:
            flash('用户名不能为空')
        elif not password:
            flash('密码不能为空')
        else:
            # 对比！！！！！
            cursor.execute("SELECT * FROM userInfo WHERE username = ?", (username,))  
            existing_user = cursor.fetchone()  
            if existing_user and existing_user['password'] == password: 
                flash('登录成功！')  
                user_connection.close()  
                session['username'] = username
                session['logged_in'] = True
                return redirect(url_for('index'))    
            else:  
                flash('账号或密码错误')  
    return render_template('login.html')
    
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('您已成功退出登录')
    return redirect(url_for('login'))

# 装饰器，表示调用内部网址，到达对应页面
@app.route('/index')
# 定义函数，一个函数代表一个网页页面
@login_required
def index():
    if 'logged_in' in session and session['logged_in']:  
        username = session['username']  
    else:  
        username=None

    # 获取分页参数
    per_page = int(request.args.get('per_page', 10))  # 默认每页显示10条
    page = int(request.args.get('page', 1))  # 默认当前页为1
    # 计算偏移量
    offset = (page - 1) * per_page
    # 拿到数据库链接
    connection = get_db_connection()
    # sql语句：取出posts表中的数据(按照created倒排序)
    posts = connection.execute("select * from posts order by created DESC LIMIT ? OFFSET ?",(per_page, offset)).fetchall()
    # 查询总记录数
    total_posts = connection.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    # 计算总页数
    total_pages = (total_posts + per_page - 1) // per_page
    # 指定当前页面要访问的index.html;将上行中的posts返回给index页面中的posts变量
    return render_template('index.html',posts=posts,username=username,page=page,total_pages=total_pages,per_page=per_page)

@app.route('/posts/<int:post_id>') # <>表示内部内容可变
@login_required
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

@app.route('/posts/new',methods=('GET','POST')) # 同时支持get和post请求
@login_required
def new():
    if 'logged_in' not in session or not session['logged_in']:  
        return redirect(url_for('login'))
    
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('标题不能为空')
        elif not content:
            flash('内容不能为空')
        else:
            connection = get_db_connection()
            connection.execute('insert into posts(title,content) values(?,?)',(title,content))
            # 修改数据库内容后需要提交
            connection.commit()
            connection.close()
            flash('文章保存成功！')
            # 重定向
            return redirect(url_for('index'))
    return render_template('new.html')

    
@app.route('/posts/<int:post_id>/edit',methods=('GET','POST'))
@login_required
def edit(post_id):
    post = get_post(post_id)

    if request.method =='POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('标题不能为空！')
        else:
            connection = get_db_connection()
            connection.execute('UPDATE posts SET title = ?,content = ?' 'WHERE id =?',(title,content,post_id))
            connection.commit()
            connection.close()
            flash('文章修改成功！')
            # 重定向
            return redirect(url_for('index'))
    return render_template('edit.html',post=post)

@app.route('/posts/<int:post_id>/delete',methods=('POST',)) # 后台增加或减少，一般用post，get容易被爬;post请求无法通过在上方输入链接直达对应页面
@login_required
def delete(post_id):
    post = get_post(post_id)
    connection = get_db_connection()
    connection.execute('DELETE FROM posts WHERE id =?',(post_id,))
    connection.commit()
    connection.close()
    flash('文章《"{}"》删除成功！'.format(post['title']))
    return redirect(url_for('index'))
