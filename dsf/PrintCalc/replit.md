# Overview

This is a comprehensive web application for calculating printing costs of educational textbooks, built with Python Flask. The application serves Arabic-speaking educational institutions and provides a dual interface: a public-facing calculator for users to estimate printing costs and a complete admin panel for managing academic data and pricing configurations. The system supports hierarchical navigation through academic years → subjects → books, with detailed cost calculations based on printing types, page counts, and additional services.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **RTL Support**: Full Arabic language support with right-to-left layout
- **Responsive Design**: Mobile-first approach using Bootstrap grid system
- **Interactive Elements**: JavaScript enhancements for form validation and user experience
- **Navigation Structure**: Hierarchical breadcrumb navigation for user workflows

## Backend Architecture
- **Framework**: Flask web framework with modular route organization
- **Database ORM**: SQLAlchemy with declarative base for database operations
- **Application Structure**: 
  - `app.py` - Main application factory and configuration
  - `models.py` - Database models and relationships
  - `routes.py` - Request handling and business logic
  - `main.py` - Application entry point
- **Error Handling**: Flash messaging system for user feedback
- **Security**: Session management with configurable secret keys

## Data Model Design
- **Hierarchical Structure**: Academic Years → Subjects → Books relationship
- **Pricing System**: Flexible printing price configurations with per-unit calculations
- **Add-on Services**: Configurable additional services (covers, binding, etc.)
- **Active/Inactive States**: Soft deletion support for all entities

## Database Schema
- **Academic Years**: Container for subjects by educational level
- **Subjects**: Academic subjects tied to specific years
- **Books**: Individual textbooks with page counts and metadata
- **Printing Prices**: Configurable printing types with unit-based pricing
- **Add-ons**: Additional services with fixed or variable pricing

## Cost Calculation Engine
- **Page-based Calculations**: Pricing based on page count and printing type
- **Unit Conversion**: Automatic calculation of printing units from page counts
- **Add-on Integration**: Optional additional services in cost breakdown
- **Real-time Calculations**: Dynamic cost updates based on user selections

# External Dependencies

## Core Framework Dependencies
- **Flask**: Primary web framework for request handling
- **SQLAlchemy**: Database ORM for data persistence and relationships
- **Werkzeug**: WSGI utilities and development server

## Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive design and components
- **Font Awesome**: Icon library for UI enhancement
- **Custom CSS**: Application-specific styling for Arabic RTL support

## Database
- **SQLite**: Local file-based database for data storage
- **Automatic Initialization**: Database and tables created on first run
- **Data Directory**: Organized file structure for database storage

## Development and Deployment
- **PythonAnywhere**: Target deployment platform with specific configurations
- **ProxyFix**: Middleware for proper header handling in hosted environments
- **Logging**: Built-in Python logging for debugging and monitoring

## Browser Compatibility
- **Modern Browsers**: Supports current versions of major browsers
- **JavaScript Features**: Enhanced user experience with progressive enhancement
- **Mobile Responsive**: Touch-friendly interface for mobile devices