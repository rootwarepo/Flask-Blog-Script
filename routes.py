from flask import render_template, url_for, redirect, request, session, make_response, jsonify
from sqlalchemy import desc, or_
from werkzeug.utils import secure_filename
from models import db, User, Category, BlogPost
import os
from datetime import datetime
from app import app, POSTS_PER_PAGE, UPLOAD_FOLDER
from utils import allowed_file
from slugify import slugify

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    blog_posts = BlogPost.query.filter_by(is_published='Yes').order_by(desc(BlogPost.date)).paginate(page=page, per_page=POSTS_PER_PAGE)

    popular_posts = BlogPost.query.filter_by(is_published='Yes').order_by(desc(BlogPost.total_views)).limit(3)
    latest_posts = BlogPost.query.filter_by(is_published='Yes').order_by(desc(BlogPost.date)).limit(3)
    
    theme = request.cookies.get('themePreference')
    
    return render_template('index.html', blog_posts=blog_posts, popular_posts=popular_posts, latest_posts=latest_posts, theme=theme)

@app.route('/search')
def search():
    theme = request.cookies.get('themePreference')
    popular_posts = BlogPost.query.filter_by(is_published='Yes').order_by(BlogPost.total_views.desc()).limit(3)

    search_term = request.args.get('q', '').lower()

    page = request.args.get('page', 1, type=int)
    search_results = BlogPost.query.filter(or_(BlogPost.title.ilike(f"%{search_term}%"), BlogPost.content.ilike(f"%{search_term}%"))).paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)

    return render_template('search_results.html', blog_posts=search_results, popular_posts=popular_posts, theme=theme)

@app.route('/login', methods=['GET', 'POST'])
def login():
    theme = request.cookies.get('themePreference')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            article_ids = [article.id for article in user.articles]
        else:
            return render_template('login.html', error='Geçersiz kullanıcı adı veya şifre.', theme=theme)

        user_data = {
            'id': user.id,
            'username': user.username,
            'password': user.password,
            'full_name': user.full_name,
            'email': user.email,
            'role': user.role,
            'profile_picture': user.profile_picture,
            'about': user.about,
            'articles': article_ids
        }
        if user:
            session['user'] = user_data
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Geçersiz kullanıcı adı veya şifre.')

    return render_template('login.html', theme=theme)

@app.route('/register', methods=['GET', 'POST'])
def register():
    theme = request.cookies.get('themePreference')
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = first_name + ' ' + last_name

        user = User.query.filter_by(username=username).first()
        if not user:
            new_user = User(username=username, email=email, full_name=full_name, password=password, role='user', profile_picture="https://static.thenounproject.com/png/5572537-200.png", about="Hakkında içeriğinizi düzenleyebilirsiniz.")
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html', theme=theme)

@app.route('/articles')
def articles():
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('q', '').lower()
    search_by = request.args.get('searchBy', '').lower()

    theme = request.cookies.get('themePreference')
    if 'user' in session:
        user = session['user']
        if user['role'] == 'user':
            query = BlogPost.query.filter_by(author_id=user['id'])
        elif user['role'] == 'admin':
            query = BlogPost.query

        if search_term:
            if search_by == 'author':
                query = query.filter(BlogPost.author_id == user['id'])
            elif search_by == 'title':
                query = query.filter(BlogPost.title.ilike(f'%{search_term}%'))
            elif search_by == 'content':
                query = query.filter(BlogPost.content.ilike(f'%{search_term}%'))
            elif search_by == 'date':
                query = query.filter(BlogPost.date.ilike(f'%{search_term}%'))

        per_page = 5
        user_posts = query.order_by(BlogPost.date.desc()).paginate(page=page, per_page=per_page)

        return render_template('articles.html', blog_posts=user_posts, user=user, theme=theme)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/categories')
def categories_page():
    theme = request.cookies.get('themePreference')
    categories = Category.query.all()
    popular_posts = BlogPost.query.filter_by(is_published='Yes').order_by(desc(BlogPost.total_views)).limit(3)
    return render_template('categories_page.html', categories=categories, popular_posts=popular_posts, theme=theme)

@app.route('/category/<string:category_slug>/<string:post_slug>')
def blog_post(category_slug, post_slug):
    theme = request.cookies.get('themePreference')
    popular_posts = BlogPost.query.filter_by(is_published='Yes').order_by(desc(BlogPost.total_views)).limit(3)
    post = BlogPost.query.filter_by(slug=post_slug, category_slug=category_slug, is_published='Yes').first()
    if post:
        return render_template('blog_post.html', post=post, popular_posts=popular_posts, theme=theme)
    else:
        return render_template('not_found.html', theme=theme)
    
@app.route('/category/<string:category_slug>')
def category_posts(category_slug):
    page = request.args.get('page', 1, type=int)
    
    theme = request.cookies.get('themePreference')
    category = Category.query.filter_by(slug=category_slug).first()
    if not category:
        return render_template('not_found.html', popular_posts=[], theme=theme)
    
    popular_posts = BlogPost.query.filter_by(is_published='Yes').order_by(desc(BlogPost.total_views)).limit(3)
    category_posts = BlogPost.query.filter_by(category_slug=category_slug, is_published='Yes').paginate(page=page, per_page=5)
    return render_template('category_posts.html', category_slug=category.slug, blog_posts=category_posts, popular_posts=popular_posts, theme=theme)
    
@app.route('/edit_article/<string:post_slug>', methods=['GET', 'PUT'])
def edit_article(post_slug):
    if 'user' in session:
        user = session['user']
        theme = request.cookies.get('themePreference')
        categories = Category.query.all()

        post = BlogPost.query.filter_by(slug=post_slug).first()

        if post is None:
            return render_template('not_found.html', theme=theme)

        user = User.query.filter_by(username=session['user']['username']).first()
        if user.username != post.author.username and user.role != 'admin':
            return render_template('not_found.html', theme=theme)

        if request.method == 'PUT':
            post.title = request.form['title']
            post.slug = slugify(request.form['title'])
            post.category_slug = slugify(request.form['category'])
            post.content = request.form['content']
            if user.role == 'admin':
                post.is_published = request.form['is_published']
            else:
                post.is_published = 'Yes'
            if 'file' in request.files:
                file = request.files['file']
                if file.filename != '':
                    if post.image:
                        old_blog_posts_picture_path = os.path.join(app.config['UPLOAD_FOLDER'].replace('profile_pictures', 'blog_posts_pictures'), os.path.basename(post.image))
                        if os.path.exists(old_blog_posts_picture_path):
                            os.remove(old_blog_posts_picture_path)
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'].replace('profile_pictures', 'blog_posts_pictures'), filename)
                        file.save(file_path)
                        post.image = '/' + app.config['UPLOAD_FOLDER'].replace('profile_pictures', 'blog_posts_pictures') + '/' + filename

            db.session.commit()
        return render_template('edit_article.html', user=user, post=post, categories=categories, theme=theme)
    return redirect(url_for('login'))

@app.route('/delete_article/<string:post_slug>', methods=['DELETE'])
def delete_article(post_slug):
    if 'user' in session:
        user = session['user']

        post = BlogPost.query.filter_by(slug=post_slug).first()

        if not post or (user['username'] != post.author.username and user['role'] != 'admin'):
            return render_template('not_found.html')

        if request.method == 'DELETE':
            db.session.delete(post)
            db.session.commit()

            return redirect('/')

        theme = request.cookies.get('themePreference')
        return render_template('index.html', theme=theme)

    return redirect(url_for('login'))

@app.route('/new_article', methods=['GET', 'POST'])
def new_article():
    if 'user' in session:
        theme = request.cookies.get('themePreference')
        categories = Category.query.all()
        if request.method == 'POST':
            title = request.form['title']
            category = request.form['category']
            content = request.form['content']
            image = ''
            if 'file' in request.files:
                file = request.files['file']
                if file.filename == '':
                    pass
                else:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(UPLOAD_FOLDER.replace('profile_pictures', 'blog_posts_pictures'), filename)
                        file.save(file_path)
                    else:
                        return redirect(url_for('new_article'))
                    image = '/' + UPLOAD_FOLDER.replace('profile_pictures', 'blog_posts_pictures') + '/' + filename
            user = session.get('user', {})
            new_article = BlogPost(
                title=title,
                slug=slugify(title),
                date=datetime.now().strftime("%d %B %Y"),
                content=content,
                image=image,
                author_id=user['id'],
                category_slug=slugify(category),
                is_published="Yes",
                total_views=0
            )

            db.session.add(new_article)
            db.session.commit()

            return redirect(url_for('articles'))
        return render_template('new_article.html', categories=categories, theme=theme)
    return redirect(url_for('login'))

@app.route('/user/<string:username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    theme = request.cookies.get('themePreference')

    if user is None:
        return render_template('not_found.html')

    user_articles = BlogPost.query.filter_by(author_id=user.id).paginate(page=page, per_page=POSTS_PER_PAGE)

    return render_template('user_profile.html', user=user, blog_posts=user_articles, theme=theme)

@app.route('/edit_profile/<string:username>', methods=['GET', 'PUT'])
def edit_profile(username):
    page = request.args.get('page', 1, type=int)
    if 'user' in session:
        user = session['user']
        theme = request.cookies.get('themePreference')
    else:
        return render_template('not_found.html')
    
    user_data = User.query.filter_by(username=username).first()

    if user_data is None:
        return render_template('not_found.html')
    
    if user['username'] != username and user['role'] != 'admin':
        return render_template('not_found.html')
    
    user_articles = BlogPost.query.filter_by(author_id=user_data.id).paginate(page=page, per_page=5)

    if request.method == 'PUT':
        if 'file' not in request.files:
            return redirect(url_for('index'))
        
        file = request.files['file']
        if file.filename == '':
            pass
        else:
            if user_data.profile_picture:
                old_profile_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(user_data.profile_picture))
                if os.path.exists(old_profile_picture_path):
                    os.remove(old_profile_picture_path)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
                profile_picture = '/' + UPLOAD_FOLDER + '/' + filename
                user_data.profile_picture = profile_picture

        about = request.form['about']
        user_data.about = about
        
        db.session.commit()

        return {'message': 'Profil başarıyla güncellendi'}

    return render_template('edit_profile.html', user=user_data, blog_posts=user_articles, theme=theme)

@app.route('/get_users')
def get_users():
    user = session.get('user')
    if user is None:
        return render_template('not_found.html')

    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('q', '').lower()
    search_by = request.args.get('searchBy', '').lower()
    theme = request.cookies.get('themePreference')

    users_query = User.query

    if search_term:
        if search_by == 'username':
            users_query = users_query.filter(User.username.ilike(f'%{search_term}%'))
        elif search_by == 'full_name':
            users_query = users_query.filter(User.full_name.ilike(f'%{search_term}%'))
        elif search_by == 'about':
            users_query = users_query.filter(User.about.ilike(f'%{search_term}%'))
        elif search_by == 'role':
            users_query = users_query.filter(User.role.ilike(f'%{search_term}%'))

    users_pagination = users_query.paginate(page=page, per_page=5)

    return render_template('get_users.html', user=user, blog_posts=users_pagination, theme=theme)

@app.route('/get_categories')
def get_categories():
    user = session.get('user')
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('q', '').lower()
    search_by = request.args.get('searchBy', '').lower()
    theme = request.cookies.get('themePreference')

    if session.get('user') is None:
        return render_template('not_found.html')

    categories_query = Category.query

    if search_term:
        if search_by == 'name':
            categories_query = categories_query.filter(Category.name.ilike(f'%{search_term}%'))
        elif search_by == 'description':
            categories_query = categories_query.filter(Category.description.ilike(f'%{search_term}%'))

    current_categories = categories_query.paginate(page=page, per_page=POSTS_PER_PAGE)

    return render_template('get_categories.html', user=user, blog_posts=current_categories, theme=theme)

@app.route('/new_category', methods=['GET', 'POST'])
def new_category():
    theme = request.cookies.get('themePreference')
    if session.get('user') is None:
        return render_template('not_found.html')
    if request.method == 'POST':
        name = request.form.get('name')
        slug = slugify(request.form.get('slug'))
        description = request.form.get('description')

        if request.method == 'POST':
            if 'file' not in request.files:
                return redirect(url_for('index'))
            
            file = request.files['file']
            
            if file.filename == '':
                pass
            else:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'].replace('profile_pictures', 'categories_pictures'), filename))
                
                    image = '/' + UPLOAD_FOLDER.replace('profile_pictures', 'categories_pictures') + '/' + filename

            new_category = Category(
                name=name,
                slug=slugify(slug),
                image=image,
                description=description
            )

            db.session.add(new_category)
            db.session.commit()

            return redirect(url_for('get_categories'))

    return render_template('new_category.html', theme=theme)

@app.route('/edit_category/<string:category_slug>', methods=['GET', 'PUT'])
def edit_category(category_slug):
    theme = request.cookies.get('themePreference')
    user = session.get('user')
    if user is None:
        return render_template('not_found.html', theme=theme)

    category = Category.query.filter_by(slug=category_slug).first()
    if category is None:
        return render_template('not_found.html', theme=theme)

    if request.method == 'PUT':
        category.name = request.form['name']
        category.slug = slugify(request.form['slug'])
        category.description = request.form['description']

        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                if category.image:
                    old_category_picture_path = os.path.join(app.config['UPLOAD_FOLDER'].replace('profile_pictures', 'categories_pictures'), os.path.basename(category.image))
                    if os.path.exists(old_category_picture_path):
                        os.remove(old_category_picture_path)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'].replace('profile_pictures', 'categories_pictures'), filename)
                    file.save(file_path)
                    category.image = '/' + UPLOAD_FOLDER.replace('profile_pictures', 'categories_pictures') + '/' + filename

        db.session.commit()

    return render_template('edit_category.html', category=category, theme=theme)

@app.route('/delete_user/<int:userId>', methods=['DELETE'])
def delete_user(userId):
    user = session.get('user')
    if user is None or user['role'] != 'admin':
        return render_template('not_found.html')
    
    user_to_delete = User.query.get(userId)
    if user_to_delete is None:
        return render_template('not_found.html')

    db.session.delete(user_to_delete)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'})

@app.route('/delete_category/<int:categoryId>', methods=['DELETE'])
def delete_category(categoryId):
    user = session.get('user')
    if user is None or user['role'] != 'admin':
        return render_template('not_found.html')
    
    category = Category.query.get(categoryId)
    if category is None:
        return render_template('not_found.html')

    db.session.delete(category)
    db.session.commit()

    return jsonify({'message': 'Category deleted successfully'})

@app.route('/cookie', methods=['POST'])
def update_cookie():
    theme = request.json.get('theme')
    if theme:
        response = make_response(jsonify({'status': 'success'}))
        response.set_cookie('themePreference', theme)
        return response
    else:
        return jsonify({'status': 'error', 'message': 'Theme data not provided'})

@app.route('/contact')
def contact():
    theme = request.cookies.get('themePreference')
    popular_posts = BlogPost.query.filter_by(is_published='Yes').order_by(desc(BlogPost.total_views)).limit(3)
    return render_template('contact.html', popular_posts=popular_posts, theme=theme)

@app.route('/about')
def about():
    theme = request.cookies.get('themePreference')
    popular_posts = BlogPost.query.filter_by(is_published='Yes').order_by(desc(BlogPost.total_views)).limit(3)
    return render_template('about.html', popular_posts=popular_posts, theme=theme)

@app.route('/dashboard')
def dashboard():
    theme = request.cookies.get('themePreference')
    if 'user' in session:
        user = session['user']
    return render_template('dashboard.html', user=user, theme=theme)