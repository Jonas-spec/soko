# SOKOHUB - Modern E-commerce Marketplace

A full-featured Django e-commerce platform with vendor management, product catalog, shopping cart, and Stripe payment integration.

## Features

- 🛍️ **Product Catalog** - Browse and search products by category
- 🏪 **Vendor Management** - Multi-vendor marketplace with approval system
- 🛒 **Shopping Cart** - Add products to cart and manage quantities
- 💳 **Stripe Payments** - Secure payment processing with Stripe
- 👤 **User Profiles** - Customer and vendor profiles
- 📦 **Order Management** - Track orders and order history
- 🎨 **Modern UI** - Beautiful, responsive design with Bootstrap 5
- 🔐 **Authentication** - User registration, login, and profile management

## Tech Stack

- **Backend**: Django 5.0+
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5, JavaScript
- **Payments**: Stripe
- **Deployment**: Heroku, Railway, DigitalOcean, AWS

## Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd SOKOHUB
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Configuration

### Stripe Setup

1. Create a Stripe account at https://stripe.com
2. Get your API keys from the Stripe Dashboard
3. Add to `.env` file:
   ```
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   ```

### Environment Variables

Create a `.env` file with:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

## Project Structure

```
SOKOHUB/
├── accounts/          # User authentication and profiles
├── products/          # Product catalog and categories
├── orders/            # Shopping cart and order management
├── vendor/            # Vendor dashboard and management
├── static/            # CSS, JavaScript, images
├── templates/         # HTML templates
├── media/             # User uploaded files
└── sokohub/           # Project settings
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy to Heroku

```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set SECRET_KEY=your-secret-key
heroku config:set STRIPE_PUBLISHABLE_KEY=pk_live_...
heroku config:set STRIPE_SECRET_KEY=sk_live_...
git push heroku main
heroku run python manage.py migrate
```

## Usage

### As a Customer
1. Register/Login
2. Browse products
3. Add products to cart
4. Checkout with Stripe
5. View order history

### As a Vendor
1. Register as vendor
2. Wait for admin approval
3. Access vendor dashboard
4. Add products
5. Manage orders

### As an Admin
1. Login to `/admin/`
2. Approve vendors
3. Manage products and orders
4. View analytics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using Django
