import math
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from app import app, db
from models import AcademicYear, Subject, Book, PrintingPrice, AddOn, Employee, Order, OrderItem
from werkzeug.security import check_password_hash

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('يجب تسجيل الدخول للوصول لهذه الصفحة', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    """Decorator to require any authentication (admin or employee)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('يجب تسجيل الدخول للوصول لهذه الصفحة', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def is_admin():
    """Check if current user is admin"""
    # Check if logged in and if it's admin user
    employee_id = session.get('employee_id')
    if employee_id:
        employee = Employee.query.get(employee_id)
        return employee and employee.username == 'admin'
    return False

# Main routes
@app.route('/')
@login_required
def index():
    """Main landing page - redirect based on user role"""
    if is_admin():
        return redirect(url_for('admin_dashboard'))
    else:
        flash('ليس لديك صلاحية للوصول للموقع. يرجى التواصل مع المدير.', 'error')
        return redirect(url_for('admin_login'))

# Admin authentication routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check database for employee credentials
        employee = Employee.query.filter_by(username=username, is_active=True).first()
        
        if employee and check_password_hash(employee.password, password):
            # Update last login time and count
            employee.last_login = datetime.utcnow()
            employee.login_count = (employee.login_count or 0) + 1
            db.session.commit()
            
            session['admin_logged_in'] = True
            session['employee_id'] = employee.id
            session['employee_name'] = employee.full_name
            flash(f'مرحباً {employee.full_name}، تم تسجيل الدخول بنجاح', 'success')
            
            # Redirect based on user role
            if employee.username == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('employee_dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('employee_id', None)
    session.pop('employee_name', None)
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    years_count = AcademicYear.query.count()
    subjects_count = Subject.query.count()
    books_count = Book.query.count()
    
    # Get order statistics
    total_orders = Order.query.count()
    new_orders = Order.query.filter_by(status='new').count()
    in_progress_orders = Order.query.filter_by(status='in_progress').count()
    completed_orders = Order.query.filter_by(status='completed').count()
    
    # Get employee statistics
    total_employees = Employee.query.count()
    active_employees = Employee.query.filter_by(is_active=True).count()
    recent_employees = Employee.query.filter(Employee.last_login.isnot(None)).order_by(Employee.last_login.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         years_count=years_count,
                         subjects_count=subjects_count,
                         books_count=books_count,
                         total_orders=total_orders,
                         new_orders=new_orders,
                         in_progress_orders=in_progress_orders,
                         completed_orders=completed_orders,
                         total_employees=total_employees,
                         active_employees=active_employees,
                         recent_employees=recent_employees,
                         employee_name=session.get('employee_name', 'الموظف'))

@app.route('/admin/years')
@admin_required
def admin_years():
    """Manage academic years"""
    years = AcademicYear.query.all()
    return render_template('admin/years.html', years=years)

@app.route('/admin/years/add', methods=['POST'])
@admin_required
def add_year():
    """Add new academic year"""
    name = request.form.get('name')
    description = request.form.get('description', '')
    
    if name:
        year = AcademicYear(name=name, description=description)
        db.session.add(year)
        db.session.commit()
        flash('تم إضافة السنة الدراسية بنجاح', 'success')
    else:
        flash('يرجى إدخال اسم السنة الدراسية', 'error')
    
    return redirect(url_for('admin_years'))

@app.route('/admin/years/edit/<int:year_id>', methods=['POST'])
@admin_required
def edit_year(year_id):
    """Edit academic year"""
    year = AcademicYear.query.get_or_404(year_id)
    
    year.name = request.form.get('name', year.name)
    year.description = request.form.get('description', year.description)
    year.is_active = request.form.get('is_active') == 'on'
    
    db.session.commit()
    flash('تم تحديث السنة الدراسية بنجاح', 'success')
    
    return redirect(url_for('admin_years'))

@app.route('/admin/years/delete/<int:year_id>', methods=['POST'])
@admin_required
def delete_year(year_id):
    """Delete academic year"""
    year = AcademicYear.query.get_or_404(year_id)
    db.session.delete(year)
    db.session.commit()
    flash('تم حذف السنة الدراسية بنجاح', 'success')
    
    return redirect(url_for('admin_years'))

@app.route('/admin/subjects')
@admin_required
def admin_subjects():
    """Manage subjects"""
    subjects = Subject.query.join(AcademicYear).all()
    years = AcademicYear.query.filter_by(is_active=True).all()
    return render_template('admin/subjects.html', subjects=subjects, years=years)

@app.route('/admin/subjects/add', methods=['POST'])
@admin_required
def add_subject():
    """Add new subject"""
    name = request.form.get('name')
    description = request.form.get('description', '')
    year_id = request.form.get('year_id')
    
    if name and year_id:
        subject = Subject(name=name, description=description, year_id=year_id)
        db.session.add(subject)
        db.session.commit()
        flash('تم إضافة المادة بنجاح', 'success')
    else:
        flash('يرجى إدخال اسم المادة واختيار السنة الدراسية', 'error')
    
    return redirect(url_for('admin_subjects'))

@app.route('/admin/subjects/edit/<int:subject_id>', methods=['POST'])
@admin_required
def edit_subject(subject_id):
    """Edit subject"""
    subject = Subject.query.get_or_404(subject_id)
    
    subject.name = request.form.get('name', subject.name)
    subject.description = request.form.get('description', subject.description)
    subject.year_id = request.form.get('year_id', subject.year_id)
    subject.is_active = request.form.get('is_active') == 'on'
    
    db.session.commit()
    flash('تم تحديث المادة بنجاح', 'success')
    
    return redirect(url_for('admin_subjects'))

@app.route('/admin/subjects/delete/<int:subject_id>', methods=['POST'])
@admin_required
def delete_subject(subject_id):
    """Delete subject"""
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('تم حذف المادة بنجاح', 'success')
    
    return redirect(url_for('admin_subjects'))

@app.route('/admin/books')
@admin_required
def admin_books():
    """Manage books"""
    books = Book.query.join(Subject).join(AcademicYear).all()
    subjects = Subject.query.filter_by(is_active=True).all()
    return render_template('admin/books.html', books=books, subjects=subjects)

@app.route('/admin/books/add', methods=['POST'])
@admin_required
def add_book():
    """Add new book"""
    name = request.form.get('name')
    page_count = request.form.get('page_count')
    description = request.form.get('description', '')
    subject_id = request.form.get('subject_id')
    
    if name and page_count and subject_id:
        try:
            page_count = int(page_count)
            if page_count > 0:
                book = Book(name=name, page_count=page_count, description=description, subject_id=subject_id)
                db.session.add(book)
                db.session.commit()
                flash('تم إضافة الكتاب بنجاح', 'success')
            else:
                flash('عدد الصفحات يجب أن يكون أكبر من صفر', 'error')
        except ValueError:
            flash('يرجى إدخال رقم صحيح لعدد الصفحات', 'error')
    else:
        flash('يرجى إدخال جميع البيانات المطلوبة', 'error')
    
    return redirect(url_for('admin_books'))

@app.route('/admin/books/edit/<int:book_id>', methods=['POST'])
@admin_required
def edit_book(book_id):
    """Edit book"""
    book = Book.query.get_or_404(book_id)
    
    book.name = request.form.get('name', book.name)
    
    try:
        page_count = int(request.form.get('page_count', book.page_count))
        if page_count > 0:
            book.page_count = page_count
        else:
            flash('عدد الصفحات يجب أن يكون أكبر من صفر', 'error')
            return redirect(url_for('admin_books'))
    except ValueError:
        flash('يرجى إدخال رقم صحيح لعدد الصفحات', 'error')
        return redirect(url_for('admin_books'))
    
    book.description = request.form.get('description', book.description)
    book.subject_id = request.form.get('subject_id', book.subject_id)
    book.is_active = request.form.get('is_active') == 'on'
    
    db.session.commit()
    flash('تم تحديث الكتاب بنجاح', 'success')
    
    return redirect(url_for('admin_books'))

@app.route('/admin/books/delete/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    """Delete book"""
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('تم حذف الكتاب بنجاح', 'success')
    
    return redirect(url_for('admin_books'))

@app.route('/admin/settings')
@admin_required
def admin_settings():
    """Manage printing prices and add-ons"""
    printing_prices = PrintingPrice.query.all()
    addons = AddOn.query.all()
    return render_template('admin/settings.html', printing_prices=printing_prices, addons=addons)

@app.route('/admin/settings/printing-price/add', methods=['POST'])
@admin_required
def add_printing_price():
    """Add new printing price"""
    name = request.form.get('name')
    price_per_unit = request.form.get('price_per_unit')
    pages_per_unit = request.form.get('pages_per_unit')
    description = request.form.get('description', '')
    
    if name and price_per_unit and pages_per_unit:
        try:
            price_per_unit = float(price_per_unit)
            pages_per_unit = int(pages_per_unit)
            
            printing_price = PrintingPrice(
                name=name,
                price_per_unit=price_per_unit,
                pages_per_unit=pages_per_unit,
                description=description
            )
            db.session.add(printing_price)
            db.session.commit()
            flash('تم إضافة نوع الطباعة بنجاح', 'success')
        except ValueError:
            flash('يرجى إدخال أرقام صحيحة للسعر وعدد الصفحات', 'error')
    else:
        flash('يرجى إدخال جميع البيانات المطلوبة', 'error')
    
    return redirect(url_for('admin_settings'))

@app.route('/admin/settings/printing-price/edit/<int:price_id>', methods=['POST'])
@admin_required
def edit_printing_price(price_id):
    """Edit printing price"""
    printing_price = PrintingPrice.query.get_or_404(price_id)
    
    printing_price.name = request.form.get('name', printing_price.name)
    
    try:
        printing_price.price_per_unit = float(request.form.get('price_per_unit', printing_price.price_per_unit))
        printing_price.pages_per_unit = int(request.form.get('pages_per_unit', printing_price.pages_per_unit))
    except ValueError:
        flash('يرجى إدخال أرقام صحيحة للسعر وعدد الصفحات', 'error')
        return redirect(url_for('admin_settings'))
    
    printing_price.description = request.form.get('description', printing_price.description)
    printing_price.is_active = request.form.get('is_active') == 'on'
    
    db.session.commit()
    flash('تم تحديث نوع الطباعة بنجاح', 'success')
    
    return redirect(url_for('admin_settings'))

@app.route('/admin/settings/printing-price/delete/<int:price_id>', methods=['POST'])
@admin_required
def delete_printing_price(price_id):
    """Delete printing price"""
    printing_price = PrintingPrice.query.get_or_404(price_id)
    db.session.delete(printing_price)
    db.session.commit()
    flash('تم حذف نوع الطباعة بنجاح', 'success')
    
    return redirect(url_for('admin_settings'))

@app.route('/admin/settings/addon/add', methods=['POST'])
@admin_required
def add_addon():
    """Add new add-on"""
    name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description', '')
    
    if name and price:
        try:
            price = float(price)
            addon = AddOn(name=name, price=price, description=description)
            db.session.add(addon)
            db.session.commit()
            flash('تم إضافة الإضافة بنجاح', 'success')
        except ValueError:
            flash('يرجى إدخال رقم صحيح للسعر', 'error')
    else:
        flash('يرجى إدخال اسم الإضافة والسعر', 'error')
    
    return redirect(url_for('admin_settings'))

@app.route('/admin/settings/addon/edit/<int:addon_id>', methods=['POST'])
@admin_required
def edit_addon(addon_id):
    """Edit add-on"""
    addon = AddOn.query.get_or_404(addon_id)
    
    addon.name = request.form.get('name', addon.name)
    
    try:
        addon.price = float(request.form.get('price', addon.price))
    except ValueError:
        flash('يرجى إدخال رقم صحيح للسعر', 'error')
        return redirect(url_for('admin_settings'))
    
    addon.description = request.form.get('description', addon.description)
    addon.is_active = request.form.get('is_active') == 'on'
    
    db.session.commit()
    flash('تم تحديث الإضافة بنجاح', 'success')
    
    return redirect(url_for('admin_settings'))

@app.route('/admin/settings/addon/delete/<int:addon_id>', methods=['POST'])
@admin_required
def delete_addon(addon_id):
    """Delete add-on"""
    addon = AddOn.query.get_or_404(addon_id)
    db.session.delete(addon)
    db.session.commit()
    flash('تم حذف الإضافة بنجاح', 'success')
    
    return redirect(url_for('admin_settings'))

# User routes
@app.route('/user')
def user_select_year():
    """User interface - select academic year"""
    years = AcademicYear.query.filter_by(is_active=True).all()
    return render_template('user/select_year.html', years=years)

@app.route('/calculate')
@login_required
def calculate_redirect():
    """Redirect to book selection"""
    if not is_admin():
        flash('ليس لديك صلاحية للوصول لهذه الصفحة. يرجى التواصل مع المدير.', 'error')
        return redirect(url_for('admin_login'))
    return redirect(url_for('user_select_books'))

@app.route('/books')
@login_required
def user_select_books():
    """User interface to select books from all years"""
    # Allow both admin and employees to access cost calculation
    # (This is now allowed for all logged-in users)
    
    # Initialize cart if not exists
    if 'cart' not in session:
        session['cart'] = []
    
    years = AcademicYear.query.filter_by(is_active=True).all()
    years_with_books = []
    
    for year in years:
        subjects = Subject.query.filter_by(year_id=year.id, is_active=True).all()
        year_books = []
        for subject in subjects:
            books = Book.query.filter_by(subject_id=subject.id, is_active=True).all()
            for book in books:
                book.subject_name = subject.name
                book.year_name = year.name
                year_books.append(book)
        
        if year_books:
            years_with_books.append({
                'year': year,
                'books': year_books
            })
    
    return render_template('user/select_books.html', years_with_books=years_with_books)

@app.route('/cart/add/<int:book_id>')
@login_required
def add_to_cart(book_id):
    """Add book to cart - admin only"""
    if not is_admin():
        flash('ليس لديك صلاحية لإضافة الكتب. يرجى التواصل مع المدير.', 'error')
        return redirect(url_for('admin_login'))
    
    book = Book.query.get_or_404(book_id)
    
    if 'cart' not in session:
        session['cart'] = []
    
    # Check if book already in cart, if yes increase quantity
    for item in session['cart']:
        if item['id'] == book_id:
            # Handle old cart items that don't have quantity field
            if 'quantity' not in item:
                item['quantity'] = 1
            item['quantity'] += 1
            session.modified = True
            flash(f'تم زيادة كمية كتاب {book.name} (الكمية: {item["quantity"]})', 'success')
            return redirect(url_for('user_select_books'))
    
    # Add new book to cart
    subject = Subject.query.get(book.subject_id)
    year = AcademicYear.query.get(subject.year_id)
    
    session['cart'].append({
        'id': book_id,
        'name': book.name,
        'pages': book.page_count,
        'subject_name': subject.name,
        'year_name': year.name,
        'quantity': 1
    })
    session.modified = True
    
    flash(f'تم إضافة كتاب {book.name} للسلة', 'success')
    return redirect(url_for('user_select_books'))

@app.route('/cart/remove/<int:book_id>')
@login_required
def remove_from_cart(book_id):
    """Remove book from cart - admin only"""
    if not is_admin():
        flash('ليس لديك صلاحية لحذف الكتب. يرجى التواصل مع المدير.', 'error')
        return redirect(url_for('admin_login'))
    
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != book_id]
        session.modified = True
        flash('تم حذف الكتاب من السلة', 'success')
    
    return redirect(url_for('view_cart'))

@app.route('/cart')
@login_required
def view_cart():
    """View cart and calculate total cost - admin and employees"""
    # Allow both admin and employees to view cart for cost calculation
    
    if 'cart' not in session or not session['cart']:
        flash('السلة فارغة', 'info')
        return redirect(url_for('user_select_books'))
    
    printing_prices = PrintingPrice.query.filter_by(is_active=True).all()
    addons = AddOn.query.filter_by(is_active=True).all()
    
    return render_template('user/cart.html', 
                         cart=session['cart'],
                         printing_prices=printing_prices,
                         addons=addons)

@app.route('/cart/calculate', methods=['POST'])
def calculate_cart_cost():
    """Calculate total cost for all books in cart"""
    if 'cart' not in session or not session['cart']:
        flash('السلة فارغة', 'error')
        return redirect(url_for('user_select_books'))
    
    printing_price_id = request.form.get('printing_price_id')
    selected_addons = request.form.getlist('addons')
    
    printing_price = PrintingPrice.query.get_or_404(printing_price_id)
    
    # Calculate cost for each book
    books_details = []
    total_printing_cost = 0
    
    for cart_item in session['cart']:
        book = Book.query.get(cart_item['id'])
        quantity = cart_item.get('quantity', 1)
        units_needed = math.ceil(book.page_count / printing_price.pages_per_unit)
        printing_cost_per_copy = units_needed * printing_price.price_per_unit
        total_printing_cost_for_item = printing_cost_per_copy * quantity
        total_printing_cost += total_printing_cost_for_item
        
        books_details.append({
            'id': book.id,
            'name': book.name,
            'pages': book.page_count,
            'quantity': quantity,
            'units_needed': units_needed,
            'printing_cost_per_copy': printing_cost_per_copy,
            'total_printing_cost': total_printing_cost_for_item,
            'subject_name': cart_item['subject_name'],
            'year_name': cart_item['year_name']
        })
    
    # Calculate add-ons cost
    addons_cost = 0
    selected_addon_objects = []
    if selected_addons:
        selected_addon_objects = AddOn.query.filter(AddOn.id.in_(selected_addons)).all()
        addons_cost = sum(addon.price for addon in selected_addon_objects)
    
    # Total cost
    total_cost = total_printing_cost + addons_cost
    
    calculation_details = {
        'books_details': books_details,
        'printing_price': {
            'id': printing_price.id,
            'name': printing_price.name,
            'price_per_unit': printing_price.price_per_unit,
            'pages_per_unit': printing_price.pages_per_unit,
            'description': printing_price.description
        },
        'total_printing_cost': total_printing_cost,
        'selected_addons': [
            {
                'id': addon.id,
                'name': addon.name,
                'price': addon.price,
                'description': addon.description
            } for addon in selected_addon_objects
        ],
        'addons_cost': addons_cost,
        'total_cost': total_cost
    }
    
    # Store calculation in session for invoice printing
    session['last_calculation'] = calculation_details
    session.modified = True
    
    printing_prices = PrintingPrice.query.filter_by(is_active=True).all()
    addons = AddOn.query.filter_by(is_active=True).all()
    
    return render_template('user/cart.html', 
                         cart=session['cart'],
                         printing_prices=printing_prices,
                         addons=addons,
                         calculation=calculation_details)

@app.route('/invoice/print', methods=['POST'])
def print_invoice():
    """Generate printable invoice"""
    from datetime import datetime
    import json
    import qrcode
    import io
    import base64
    
    # Get calculation data from session
    calculation_data = session.get('last_calculation')
    if not calculation_data:
        flash('لا توجد بيانات حساب. يرجى حساب التكلفة أولاً.', 'error')
        return redirect(url_for('view_cart'))
    
    customer_name = request.form.get('customer_name', '')
    customer_phone = request.form.get('customer_phone', '')
    amount_paid_str = request.form.get('amount_paid', '0')
    try:
        amount_paid = float(amount_paid_str) if amount_paid_str else 0.0
    except ValueError:
        amount_paid = 0.0
    notes = request.form.get('notes', '')
    
    # Save order to database
    order = Order(
        customer_name=customer_name,
        customer_phone=customer_phone,
        total_cost=calculation_data['total_cost'],
        status='new',
        printing_type_id=calculation_data['printing_price']['id'],
        selected_addons=json.dumps([addon['id'] for addon in calculation_data['selected_addons']])
    )
    db.session.add(order)
    db.session.flush()  # Get the order ID
    
    # Save order items
    for book_detail in calculation_data['books_details']:
        order_item = OrderItem(
            order_id=order.id,
            book_id=book_detail['id'],
            quantity=book_detail['quantity'],
            unit_cost=book_detail['printing_cost_per_copy'],
            total_cost=book_detail['total_printing_cost']
        )
        db.session.add(order_item)
    
    db.session.commit()
    
    # Generate QR code for order tracking
    qr_url = request.url_root + f"order/{order.order_number}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64 for embedding in HTML
    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    invoice_data = {
        'order_id': order.order_number,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'customer_name': customer_name,
        'customer_phone': customer_phone,
        'amount_paid': amount_paid,
        'notes': notes,
        'calculation': calculation_data,
        'qr_code': qr_base64,
        'tracking_url': qr_url
    }
    
    # Clear cart after successful order
    session.pop('cart', None)
    session.pop('last_calculation', None)
    session.modified = True
    
    return render_template('user/invoice.html', invoice=invoice_data)

@app.route('/user/year/<int:year_id>')
def user_select_subject(year_id):
    """User interface - select subject"""
    year = AcademicYear.query.get_or_404(year_id)
    subjects = Subject.query.filter_by(year_id=year_id, is_active=True).all()
    return render_template('user/select_subject.html', year=year, subjects=subjects)

@app.route('/user/subject/<int:subject_id>')
def user_select_book(subject_id):
    """User interface - select book"""
    subject = Subject.query.get_or_404(subject_id)
    books = Book.query.filter_by(subject_id=subject_id, is_active=True).all()
    return render_template('user/select_book.html', subject=subject, books=books)

@app.route('/user/book/<int:book_id>')
def user_calculate_cost(book_id):
    """User interface - calculate printing cost"""
    book = Book.query.get_or_404(book_id)
    printing_prices = PrintingPrice.query.filter_by(is_active=True).all()
    addons = AddOn.query.filter_by(is_active=True).all()
    return render_template('user/calculate_cost.html', book=book, printing_prices=printing_prices, addons=addons)

@app.route('/user/calculate', methods=['POST'])
def calculate_cost():
    """Calculate printing cost based on selections"""
    book_id = request.form.get('book_id')
    printing_price_id = request.form.get('printing_price_id')
    selected_addons = request.form.getlist('addons')
    
    book = Book.query.get_or_404(book_id)
    printing_price = PrintingPrice.query.get_or_404(printing_price_id)
    
    # Calculate printing cost
    units_needed = math.ceil(book.page_count / printing_price.pages_per_unit)
    printing_cost = units_needed * printing_price.price_per_unit
    
    # Calculate add-ons cost
    addons_cost = 0
    selected_addon_objects = []
    if selected_addons:
        selected_addon_objects = AddOn.query.filter(AddOn.id.in_(selected_addons)).all()
        addons_cost = sum(addon.price for addon in selected_addon_objects)
    
    # Total cost
    total_cost = printing_cost + addons_cost
    
    calculation_details = {
        'book': book,
        'printing_price': printing_price,
        'units_needed': units_needed,
        'printing_cost': printing_cost,
        'selected_addons': selected_addon_objects,
        'addons_cost': addons_cost,
        'total_cost': total_cost
    }
    
    return render_template('user/calculate_cost.html', 
                         book=book, 
                         printing_prices=PrintingPrice.query.filter_by(is_active=True).all(),
                         addons=AddOn.query.filter_by(is_active=True).all(),
                         calculation=calculation_details)

# Admin Order Management Routes
@app.route('/admin/orders')
@login_required
def admin_orders():
    """Admin orders management"""
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = Order.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/orders.html', 
                         orders=orders, 
                         status_filter=status_filter,
                         employee_name=session.get('employee_name', 'الموظف'))

@app.route('/admin/orders/<order_number>')
@admin_required
def admin_order_detail(order_number):
    """View order details"""
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('admin/order_detail.html', 
                         order=order,
                         employee_name=session.get('employee_name', 'الموظف'))

@app.route('/admin/orders/<order_number>/status', methods=['POST'])
@admin_required
def update_order_status(order_number):
    """Update order status"""
    from datetime import datetime
    
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    new_status = request.form.get('status')
    
    if new_status in ['new', 'in_progress', 'completed']:
        order.status = new_status
        if new_status == 'completed':
            order.completed_at = datetime.utcnow()
        order.employee_id = session.get('employee_id')
        db.session.commit()
        flash(f'تم تحديث حالة الطلب إلى: {get_status_text(new_status)}', 'success')
    else:
        flash('حالة غير صحيحة', 'error')
    
    return redirect(url_for('admin_order_detail', order_number=order_number))

def get_status_text(status):
    """Get Arabic text for order status"""
    status_map = {
        'new': 'جديد',
        'in_progress': 'قيد التنفيذ',
        'completed': 'مكتمل'
    }
    return status_map.get(status, status)

# Order tracking for customers
@app.route('/order/<order_number>')
def track_order(order_number):
    """Customer order tracking page"""
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('user/track_order.html', order=order)

# Error handlers
# Employee management routes (admin only)
@app.route('/admin/employees')
@admin_required
def admin_employees():
    """Manage employees - admin only"""
    if not is_admin():
        flash('ليس لديك صلاحية لإدارة الموظفين. هذه الصفحة للمدير فقط.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    employees = Employee.query.order_by(Employee.created_at.desc()).all()
    return render_template('admin/employees.html', employees=employees)

@app.route('/admin/employees/add', methods=['POST'])
@admin_required
def add_employee():
    """Add new employee - admin only"""
    if not is_admin():
        flash('ليس لديك صلاحية لإضافة موظفين. هذه الصفحة للمدير فقط.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    username = request.form.get('username')
    full_name = request.form.get('full_name')
    phone = request.form.get('phone', '')
    password = request.form.get('password')
    
    if username and full_name and password:
        # Check if username already exists
        existing = Employee.query.filter_by(username=username).first()
        if existing:
            flash('اسم المستخدم موجود بالفعل، يرجى اختيار اسم آخر', 'error')
        else:
            hashed_password = generate_password_hash(password)
            employee = Employee(
                username=username,
                full_name=full_name,
                phone=phone,
                password=hashed_password
            )
            db.session.add(employee)
            db.session.commit()
            flash(f'تم إضافة الموظف {full_name} بنجاح', 'success')
    else:
        flash('يرجى إدخال جميع البيانات المطلوبة', 'error')
    
    return redirect(url_for('admin_employees'))

@app.route('/admin/employees/edit/<int:employee_id>', methods=['POST'])
@admin_required
def edit_employee(employee_id):
    """Edit employee - admin only"""
    if not is_admin():
        flash('ليس لديك صلاحية لتعديل الموظفين. هذه الصفحة للمدير فقط.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    employee = Employee.query.get_or_404(employee_id)
    
    employee.full_name = request.form.get('full_name', employee.full_name)
    employee.phone = request.form.get('phone', employee.phone)
    employee.is_active = request.form.get('is_active') == 'on'
    
    # Update password if provided
    new_password = request.form.get('password')
    if new_password:
        employee.password = generate_password_hash(new_password)
    
    db.session.commit()
    flash(f'تم تحديث بيانات {employee.full_name} بنجاح', 'success')
    
    return redirect(url_for('admin_employees'))

@app.route('/admin/employees/delete/<int:employee_id>', methods=['POST'])
@admin_required
def delete_employee(employee_id):
    """Delete employee - admin only"""
    if not is_admin():
        flash('ليس لديك صلاحية لحذف الموظفين. هذه الصفحة للمدير فقط.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    employee = Employee.query.get_or_404(employee_id)
    
    # Prevent deleting admin account
    if employee.username == 'admin':
        flash('لا يمكن حذف حساب المدير', 'error')
        return redirect(url_for('admin_employees'))
    
    db.session.delete(employee)
    db.session.commit()
    flash(f'تم حذف الموظف {employee.full_name} بنجاح', 'success')
    
    return redirect(url_for('admin_employees'))

# Employee dashboard for non-admin users
@app.route('/employee')
@login_required
def employee_dashboard():
    """Employee dashboard - limited access"""
    if is_admin():
        # Redirect admin to full dashboard
        return redirect(url_for('admin_dashboard'))
    
    # Employee can only see orders and basic stats
    total_orders = Order.query.count()
    new_orders = Order.query.filter_by(status='new').count()
    in_progress_orders = Order.query.filter_by(status='in_progress').count()
    completed_orders = Order.query.filter_by(status='completed').count()
    
    return render_template('employee/dashboard.html',
                         total_orders=total_orders,
                         new_orders=new_orders,
                         in_progress_orders=in_progress_orders,
                         completed_orders=completed_orders,
                         employee_name=session.get('employee_name', 'الموظف'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
