from flask import Flask,render_template,request,url_for,flash,redirect,session,jsonify
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
    #user_connection = sqlite3.connect("userInfo.db")
    # 使从数据库取出的每条数据都可以当作字典使用
    #user_connection.row_factory = sqlite3.Row
    #return user_connection
    try:
        conn = sqlite3.connect('userInfo.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None
    
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
send_by = 'your_email@example.com' 
send_by_password = 'your_email_password'
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
    smtp.login(send_by,send_by_password)
    smtp.sendmail(send_by,send_to,message.as_string())
    print('发送成功！')
    print(content)
# 主函数（获取+发送
def send_email_code(send_to):
    verificate_code = code()
    content = str("【验证码】您的验证码是：") + verificate_code + ".如非本人操作，请忽略本条邮件."
    try:
        send_email(send_to=send_to,content=content)
        return verificate_code
    except Exception as error:
        #print("发送验证码失败",error)
        return False
# 储存验证码
def store_verification_code(email, verificate_code): 
    email = email.lower()  # 转换为小写 
    with get_userInfo_connection() as conn:  
        cursor = conn.cursor()  
         # 检查邮箱是否已经存在
        cursor.execute("SELECT email, verificate_code FROM userInfo WHERE email = ?", (email,))
        record = cursor.fetchone()
        if record is None:
            # 插入新记录
            cursor.execute('''
                INSERT INTO userInfo (email, verificate_code, verificate_code_created, username)
                VALUES (?, ?, ?, ?)
            ''', (email, verificate_code, datetime.datetime.now().isoformat(), "temp_username"))
        else:
            # 更新现有记录
            cursor.execute('''
                UPDATE userInfo
                SET verificate_code = ?, verificate_code_created = ?
                WHERE email = ?
            ''', (verificate_code, datetime.datetime.now().isoformat(), email))              
        conn.commit()
        print(f"验证码存储成功: {verificate_code}，时间: {datetime.datetime.now()}")

# 对比验证
def verify_code(email, input_verificate_code):  
    email = request.form.get('email').lower() # 转换为小写
    with get_userInfo_connection() as conn:
        cursor = conn.cursor() 
        print(f"正在验证邮箱: {email}")  
        cursor.execute("SELECT verificate_code , verificate_code_created FROM userInfo WHERE email = ?", (email,))  
        record = cursor.fetchone()   
        if record is None: 
            print(f"邮箱 {email} 没有找到记录")
            return False  
        verificate_code, created_time = record 
        print(f"数据库中的验证码: {verificate_code}，时间: {created_time}")
        #if verificate_code_created:
            #verificate_code_created = datetime.datetime.fromisoformat(verificate_code_created)
        #return input_verificate_code == verificate_code
        if input_verificate_code != verificate_code:
            #print(f"验证码错误: {input_verificate_code} != {verificate_code}")
            return False
        # 检查验证码是否过期，例如：验证码有效期为10分钟
        #if datetime.datetime.now() - created_time > datetime.timedelta(minutes=10):
            #print(f"验证码已过期")
            #return False
        return True
   
@app.route('/verificate_code', methods=['POST'])
def verificate_code():
    email = request.form.get('email')
    if email:
        verificate_code = send_email_code(send_to=email)
        store_verification_code(email, verificate_code)
        return jsonify({'success': True, 'message': '验证码发送成功'}), 200
    else:
        return jsonify({'success': False, 'message': '邮箱不能为空'}), 400  

@app.route('/sign_up',methods=('GET','POST')) # 注册
def sign_up():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        input_verificate_code = request.form.get('input_verificate_code')
        print(f"收到的验证码: {input_verificate_code}")
        if not username:
            flash('用户名不能为空')
        elif not password:
            flash('密码不能为空')
        elif not email:
            flash('邮箱不能为空')
        elif not input_verificate_code:
            flash('验证码不能为空')
        else:
            if verify_code(email, input_verificate_code):
                with get_userInfo_connection() as user_connection:
                    user_cursor = user_connection.cursor()
                    user_cursor.execute("SELECT username, password FROM userInfo WHERE email = ?", (email,))
                    existing_user = user_cursor.fetchone()
                    if existing_user:
                        existing_username, existing_password = existing_user
                        if existing_username and existing_password:
                            # 用户已存在且已设置用户名和密码
                            flash('用户已存在，请直接登录')
                            return redirect(url_for('login'))          
                        else:
                            # 邮箱存在但用户名和密码未设置
                            user_cursor.execute("UPDATE userInfo SET username = ?, password = ? WHERE email = ?", 
                                                (username, password, email))
                            user_connection.commit()
                            session['username'] = username
                            session['logged_in'] = True
                            flash('注册成功！')
                            return redirect(url_for('index'))    
            else:
                flash('验证码错误!')
    return render_template('sign_up.html')       

@app.route('/login',methods=('GET','POST')) # 登录
def login():
    if request.method == "POST":
        user_connection = get_userInfo_connection()  
        cursor = user_connection.cursor()
        email = request.form['email'] # 接收form表单传参
        password = request.form['password']
        if not email:
            flash('邮箱不能为空')
        elif not password:
            flash('密码不能为空')
        else:
            # 对比！！！！！
            cursor.execute("SELECT * FROM userInfo WHERE email = ?", (email,))  
            existing_user = cursor.fetchone() 
            username = existing_user['username']
            if existing_user['email'] == email and existing_user['password'] == password: 
                flash('登录成功！')  
                user_connection.close()  
                session['username'] = username
                session['logged_in'] = True
                return redirect(url_for('index'))    
            else:  
                flash('邮箱或密码错误')  
    return render_template('login.html')
    
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('您已成功退出登录')
    return redirect(url_for('login'))

@app.route('/reset_password',methods=('GET','POST')) # 重置密码
def reset_password():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        input_verificate_code = request.form.get('input_verificate_code') 
        print(f"收到的验证码: {input_verificate_code}")
        if not email:
            flash('邮箱不能为空')
        elif not input_verificate_code:
            flash('验证码不能为空')
        elif not password:
            flash('密码不能为空')
        else:
            if verify_code(email, input_verificate_code):
                with get_userInfo_connection() as user_connection:
                    user_cursor = user_connection.cursor()
                    user_cursor.execute("UPDATE userInfo SET  password = ? WHERE email = ?", 
                                        ( password, email))
                    user_connection.commit()
                    # 查询更新后的用户信息
                    user_cursor.execute("SELECT * FROM userInfo WHERE email = ?", (email,))
                    updated_user = user_cursor.fetchone()
                    #print(f"更新之后的用户信息: {updated_user}")
                     # 更新 session 并重定向到登录页面
                    session['logged_in'] = True
                    session['username'] = updated_user[4] # 用户名在 userInfo 表的第4列
                    flash('重置成功！')
                    return redirect(url_for('login'))    
            else:
                flash('验证码错误!')
    return render_template('reset_password.html')  


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


app.run(port=5000, debug=True)