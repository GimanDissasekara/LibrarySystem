# Library Management System

## Installation
To install the required dependencies, run the following commands:
```bash
pip install fuzzywuzzy
pip install python-Levenshtein
pip install Pillow
```

## Data Structure

### Student Table
| school_id | name       | class |
|-----------|-----------|-------|
| S001      | John Doe  | 10th  |
| S002      | Jane Smith | 11th  |
| S003      | Mike Johnson | 9th  |

### Book Data
| barcode | title            | topic        | is_purchased |
|---------|------------------|-------------|--------------|
| B001    | Python Basics    | Programming | 0            |
| B002    | Python Basics    | Programming | 0            |
| B003    | Advanced Python  | Programming | 0            |

## Key Improvements

### Modern UI Design
- Added a color scheme with primary, secondary, and accent colors
- Created a professional header with logo space
- Improved spacing and alignment of all elements
- Added emoji icons to tab labels for better visual cues

### Enhanced User Experience
- Added a status bar to show system messages
- Improved form layouts with better labeling and spacing
- Added help tabs with instructions
- Added confirmation dialogs for important actions
- Improved search results display with colored text for better readability

### Better Error Handling
- Added more comprehensive validation
- Better error messages with suggestions
- File backup before CSV updates
- Automatic package installation check

### Additional Features
- Added documentation link
- Version information
- Window centering on startup
- Better keyboard support (Enter key for search)

### Visual Improvements
- Custom styled widgets
- Better typography with custom fonts
- Visual separators between sections
- Improved text formatting in results

### Robustness
- Better handling of missing files
- Backup system for CSV files
- More comprehensive database operations

## Required Files
To use this system, ensure the following files are available:

- `studentdetails.csv` with columns: `school_id`, `name`, `class`
- `bookdata.csv` with columns: `barcode`, `title`, `topic`, `is_purchased`

### Optional (Recommended)
- `library_icon.ico` for window icon
- `library_logo.png` for header logo

> The system will automatically install required Python packages if they are missing.

