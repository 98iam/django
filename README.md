# Inventory Management System

A Django-based inventory management system that helps track products, categories, and stock levels with an integrated AI chat assistant.

## Prerequisites

Before you begin, ensure you have the following installed and available:

- **Python 3.8+** - The programming language used
- **PostgreSQL** - The database (or you can configure SQLite for development)
- **Google Gemini API Key** - For the AI chat assistant feature (get it from [Google AI Studio](https://aistudio.google.com/))
- **Git** - For cloning the repository
- **pip** - Python package manager
- **virtualenv** - Recommended for creating isolated Python environments

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/inventory-management.git
cd inventory-management

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# If you encounter any dependency issues, try installing with the --no-deps flag and then install dependencies separately
# pip install --no-deps -r requirements.txt

# Copy example environment file and edit with your values
cp .env.example .env
# Edit .env with your database credentials and Gemini API key

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Start development server
python manage.py runserver
```

Then visit http://localhost:8000 in your browser.

## Features

- Product management with detailed information (including add, edit, and delete functionality)
- Category organization
- Stock level tracking with status indicators
- Admin interface for easy management
- Secure authentication system with Supabase integration
- Multi-user support with data isolation
- Dashboard analytics with interactive charts (sales trends, inventory value, product performance)
- Dark mode support for better visibility
- Customizable reports
- Export functionality (CSV, Excel, PDF)
- Dashboard widget customization
- AI Chat Assistant powered by Google Gemini (with direct chat interface)

## Tech Stack

- Python 3.12
- Django 5.2
- PostgreSQL (Supabase)
- Bootstrap 5.3
- Font Awesome 6.0
- Chart.js for data visualization
- Google Generative AI (Gemini) for AI chat assistant

## Environment Configuration

The `.env` file should contain the following variables:

```
# Django settings
DEBUG=True
SECRET_KEY=your_secret_key_here

# Database settings
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432

# Gemini API settings
GEMINI_API_KEY=your_gemini_api_key_here
# Uncomment and set this if you want to specify a particular model
# GEMINI_MODEL=gemini-1.5-flash
```

## Database Setup

This project uses PostgreSQL with Supabase by default, but you can modify the settings in your `.env` file to use any database supported by Django:

- For **SQLite** (simple local development):
  ```
  # No additional settings needed, Django will use SQLite by default if PostgreSQL is not configured
  ```

- For **PostgreSQL** (recommended for production):
  ```
  DB_NAME=your_db_name
  DB_USER=your_db_user
  DB_PASSWORD=your_db_password
  DB_HOST=your_db_host
  DB_PORT=5432
  ```

- For **Supabase** (as used in this project):
  1. Create a Supabase account at [supabase.com](https://supabase.com/)
  2. Create a new project and get your database credentials
  3. Add them to your `.env` file as shown above

## Usage

1. Access the admin interface at `http://localhost:8000/admin`
2. Log in with your credentials
3. Start managing your inventory!

### Using the AI Chat Assistant

1. Make sure you've set up your Gemini API key in the `.env` file
2. Click on the robot icon in the navigation bar to open the chat sidebar
3. The chat interface will open directly, showing a new or existing chat session
4. Type your questions about inventory management or how to use the system
5. You can chat directly in the sidebar or open the chat in a full page by clicking the menu (⋮) and selecting "Open in full page"
6. To start a new chat, click the "New Chat" button at the top of the sidebar

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Analytics Features

The system includes comprehensive analytics capabilities:

- **Sales Trends**: Interactive charts showing sales over time (daily, weekly, monthly)
- **Inventory Value Tracking**: Monitor how your inventory value changes over time
- **Product Performance Metrics**: Identify your best and worst-selling products
- **Dashboard Integration**: All charts are available directly on the dashboard for quick insights
- **Customizable Reports**: Create and save custom reports for your specific needs
- **Data Export**: Export data in various formats (CSV, Excel, PDF)

## User Experience

- **Dark Mode**: Toggle between light and dark themes for comfortable viewing in different environments
- **Responsive Design**: Works well on desktop and mobile devices
- **User-specific Data**: Each user sees only their own inventory and analytics data
- **Dashboard Customization**: Drag-and-drop interface to reorder and toggle dashboard widgets
- **Personalized Settings**: User preferences are saved and applied across sessions
- **User Profile Management**: Update personal information, profile picture, and account preferences
- **Notification Preferences**: Configure email notifications for low stock alerts and order updates
- **Security Settings**: Change password and manage account security
- **AI Chat Assistant**: Get help and insights from an AI assistant powered by Google Gemini

## AI Chat Assistant

The system includes an AI chat assistant powered by Google Gemini:

1. **Setup**:
   - Get a Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)
   - Add your API key to the `.env` file: `GEMINI_API_KEY=your_api_key_here`
   - By default, the system uses the `gemini-1.5-flash` model
   - Optionally specify a different model: `GEMINI_MODEL=gemini-1.5-pro`

2. **Features**:
   - Chat with the AI assistant about inventory management
   - Get help with using the system
   - Create multiple chat sessions
   - View chat history
   - Rename and delete chat sessions
   - Access user-specific inventory data (the AI only shows products belonging to the current user)
   - Get detailed product information, inventory summaries, and sales analytics
   - Chat directly in the sidebar or expand to a full-page view
   - Direct chat interface that opens immediately when clicking the chat icon

3. **How It Works**:
   - The AI assistant has access to your inventory data in real-time
   - It can answer questions about your products, stock levels, categories, and sales
   - All data is filtered by user, so each user only sees their own inventory information
   - The system uses mock data as a fallback if there are any issues accessing the database

## Troubleshooting

### Database Connection Issues

- If you're having trouble connecting to PostgreSQL, make sure your database credentials are correct in the `.env` file
- For local development, you can switch to SQLite by removing or commenting out the database settings in your `.env` file

### AI Chat Assistant Issues

- If the AI chat is not working, check that your Gemini API key is valid and correctly set in the `.env` file
- Make sure you have internet access as the AI chat requires API calls to Google's servers
- If you get model-related errors, try specifying a different model by uncommenting and setting the `GEMINI_MODEL` variable in your `.env` file
- If the AI doesn't show your products, make sure you're logged in and have added products to your account
- The AI will use mock data as a fallback if there are database connection issues
- If you get a "Failed to fetch" error, try refreshing the page or checking your internet connection

### Static Files Not Loading

- Make sure you've run `python manage.py collectstatic`
- Check that `DEBUG=True` in your `.env` file during development

### Dependency Installation Issues

- If you encounter conflicts during installation, try using a fresh virtual environment
- For specific package issues, you can install them individually:
  ```
  pip install package-name==version
  ```
- Some packages might require system-level dependencies. On Ubuntu/Debian:
  ```
  sudo apt-get install python3-dev libpq-dev
  ```
  On Windows, you might need to install Visual C++ Build Tools
- If you're having issues with psycopg2-binary, you can try using psycopg2 instead (requires PostgreSQL to be installed)

## Version Control

This project uses Git for version control. To initialize the repository and make your first commit:

```bash
# Initialize Git repository
git init

# Add all files to staging
git add .

# Make initial commit
git commit -m "Initial commit: Inventory Management System with AI Chat"

# Add a remote repository (replace with your own repository URL)
git remote add origin https://github.com/yourusername/inventory-management.git

# Push to remote repository
git push -u origin main
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
