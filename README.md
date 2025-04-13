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

- Product management with detailed information
- Category organization
- Stock level tracking with status indicators
- Admin interface for easy management
- Secure authentication system with Supabase integration
- Multi-user support with data isolation
- Dashboard analytics with interactive charts
- Dark mode support for better visibility
- Customizable reports
- Export functionality (CSV, Excel, PDF)
- Dashboard widget customization
- AI Chat Assistant powered by Google Gemini

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
3. Create a new chat session or select an existing one
4. Type your questions about inventory management or how to use the system
5. You can chat directly in the sidebar or open the chat in a full page by clicking the menu (⋮) and selecting "Open in full page"

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Analytics Features

The system includes comprehensive analytics capabilities:

- **Sales Trends**: Interactive charts showing sales over time (daily, weekly, monthly)
- **Inventory Value Tracking**: Monitor how your inventory value changes over time
- **Product Performance Metrics**: Identify your best and worst-selling products
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

## Troubleshooting

### Database Connection Issues

- If you're having trouble connecting to PostgreSQL, make sure your database credentials are correct in the `.env` file
- For local development, you can switch to SQLite by removing or commenting out the database settings in your `.env` file

### AI Chat Assistant Issues

- If the AI chat is not working, check that your Gemini API key is valid and correctly set in the `.env` file
- Make sure you have internet access as the AI chat requires API calls to Google's servers
- If you get model-related errors, try specifying a different model by uncommenting and setting the `GEMINI_MODEL` variable in your `.env` file

### Static Files Not Loading

- Make sure you've run `python manage.py collectstatic`
- Check that `DEBUG=True` in your `.env` file during development

## License

[MIT](https://choosealicense.com/licenses/mit/)
