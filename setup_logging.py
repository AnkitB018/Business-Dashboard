"""
Setup script for Business Dashboard logging system
Creates necessary directories and initializes logging configuration
"""

import os
import sys
from pathlib import Path


def create_log_directory():
    """Create logs directory if it doesn't exist"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    print(f"✓ Log directory created: {log_dir.absolute()}")
    
    # Create subdirectories for different log types
    subdirs = ["archive", "exports"]
    for subdir in subdirs:
        (log_dir / subdir).mkdir(exist_ok=True)
        print(f"✓ Created subdirectory: logs/{subdir}")


def create_gitignore_entries():
    """Add logging entries to .gitignore if they don't exist"""
    gitignore_path = Path(".gitignore")
    
    logging_entries = [
        "# Logging files",
        "logs/",
        "*.log",
        "log_viewer_exports/",
        ""
    ]
    
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            existing_content = f.read()
        
        if "# Logging files" not in existing_content:
            with open(gitignore_path, 'a') as f:
                f.write("\n" + "\n".join(logging_entries))
            print("✓ Added logging entries to .gitignore")
        else:
            print("✓ Logging entries already exist in .gitignore")
    else:
        print("⚠ .gitignore not found, please add logging directories manually")


def test_logging_import():
    """Test if logging configuration can be imported"""
    try:
        # Add current directory to path
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        from logger_config import BusinessDashboardLogger
        
        # Test logger creation
        logger = BusinessDashboardLogger()
        logger.main_logger.info("Logging system initialized successfully")
        
        print("✓ Logging system test successful")
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import logging configuration: {e}")
        return False
    except Exception as e:
        print(f"✗ Logging system test failed: {e}")
        return False


def create_sample_log():
    """Create a sample log entry for testing"""
    try:
        from logger_config import BusinessDashboardLogger
        
        logger = BusinessDashboardLogger()
        main_logger = logger.main_logger
        
        # Create sample entries
        main_logger.info("Business Dashboard started")
        main_logger.info("Database connection established")
        
        logger.log_user_activity("startup", "Application initialized", {"version": "1.0.0"})
        logger.log_performance("app_startup", 1250, {"modules_loaded": 5})
        
        print("✓ Sample log entries created")
        
    except Exception as e:
        print(f"✗ Failed to create sample log entries: {e}")


def main():
    """Main setup function"""
    print("Setting up Business Dashboard Logging System...")
    print("=" * 50)
    
    # Create directories
    create_log_directory()
    print()
    
    # Update .gitignore
    create_gitignore_entries()
    print()
    
    # Test logging system
    if test_logging_import():
        create_sample_log()
    print()
    
    print("Setup complete!")
    print("\nUsage:")
    print("1. Run your application normally - logging will be automatic")
    print("2. Use log_viewer.py to analyze logs: python log_viewer.py")
    print("3. Logs are saved in the 'logs/' directory")
    print("4. Log files are automatically rotated when they reach 10MB")
    
    print("\nFor production deployment:")
    print("- Include the entire 'logs/' directory in your package")
    print("- Ensure write permissions for the logs directory")
    print("- Use log_viewer.py for remote debugging support")


if __name__ == "__main__":
    main()
