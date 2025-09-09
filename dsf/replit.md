# Overview

This is a comprehensive web application for calculating printing costs of educational textbooks, built with Python Flask. The application serves Arabic-speaking educational institutions and provides a complete printing cost management system with both user-facing calculators and administrative controls. It features hierarchical navigation through academic years, subjects, and books, with flexible pricing configurations and multi-book cart functionality for calculating total printing costs.

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

## Authentication System
- **Admin Authentication**: Simple username/password authentication for administrative access
- **Session Management**: Flask session-based admin state tracking
- **Access Control**: Decorator-based route protection for admin functions

## User Interface Features
- **Multi-step Workflow**: Guided navigation through year → subject → book selection
- **Shopping Cart**: Multi-book selection with cart management
- **Invoice Generation**: Print-friendly invoice formatting
- **Responsive Layout**: Mobile-optimized interface with Bootstrap components

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM and connection management
- **PostgreSQL**: Primary database system (configurable via environment)
- **Werkzeug**: WSGI utilities and middleware

## Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI enhancement
- **Custom CSS/JS**: Application-specific styling and interactions

## Production Environment
- **PythonAnywhere**: Target deployment platform
- **ProxyFix**: WSGI middleware for reverse proxy compatibility
- **Environment Variables**: Configuration management for database URLs and secrets

## Database Features
- **Connection Pooling**: Automatic connection management with pre-ping
- **Migration Support**: SQLAlchemy table creation and schema management
- **Default Data**: Automatic initialization of pricing and configuration data