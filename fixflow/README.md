# Team Fix Flow Task Management System

A modern, interactive task management system built with Streamlit for Skyroot Aerospace. Features role-based access control, task assignment, progress tracking, and advanced data visualizations.

## Features

- **Role-based Access Control**: Super Admin, Admin, and Technician roles
- **Interactive Dashboards**: Modern visualizations using Plotly and Altair
- **Task Management**: Assign, track, and complete tasks with image uploads
- **Field Configuration**: Dynamic form field management
- **Advanced Analytics**: Multiple chart types and progress tracking

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Default Credentials

- **Super Admin**: `superadmin` / `superadmin123`
- **Admin**: Create through Super Admin panel
- **Technician**: Create through Admin panel

## Visualization Features

The Technician Task Overview includes:

1. **Interactive Dashboard**: Multiple charts with hover tooltips
2. **Bar Charts**: Enhanced Altair visualizations
3. **Pie Charts**: Individual technician task breakdowns
4. **Progress Bars**: Real-time completion tracking
5. **Data Tables**: Detailed statistics with formatting

## Technologies Used

- **Streamlit**: Web application framework
- **Plotly**: Interactive charts and dashboards
- **Altair**: Declarative statistical visualizations
- **Pandas**: Data manipulation and analysis
- **bcrypt**: Secure password hashing

## Usage

1. Start with the welcome page
2. Choose your login type
3. Navigate through role-specific dashboards
4. Use the enhanced visualizations for task insights
5. Configure fields as needed through the admin panel

## File Structure

- `app.py`: Main application file
- `requirements.txt`: Python dependencies
- `config.json`: Configuration settings
- `users.json`: User data storage
- `tasks.json`: Task data storage

## Team Members
Anjali Garrepalli
Spandana Akkala
