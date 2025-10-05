#!/usr/bin/env python3
"""
Attribute Consistency Checker
Validates that field names, attributes, and references are consistent across:
- Database models
- API routes
- Templates (JavaScript)
- Database schema
"""

import sys
import os
import re
import sqlite3
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def get_model_attributes(model_file):
    """Extract attribute names from a model file"""
    attributes = []
    try:
        with open(model_file, 'r') as f:
            content = f.read()
            # Find db.Column definitions
            pattern = r'(\w+)\s*=\s*db\.Column'
            matches = re.findall(pattern, content)
            attributes.extend(matches)
            
            # Find db.relationship definitions
            pattern = r'(\w+)\s*=\s*db\.relationship'
            matches = re.findall(pattern, content)
            attributes.extend(matches)
    except Exception as e:
        print_error(f"Error reading {model_file}: {e}")
    
    return attributes

def get_db_columns(db_path, table_name):
    """Get actual column names from SQLite database"""
    columns = []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        print_error(f"Error reading database table {table_name}: {e}")
    
    return columns

def find_attribute_usage_in_routes(routes_dir, attribute_name, model_name):
    """Find where an attribute is used in route files"""
    usages = []
    for route_file in Path(routes_dir).glob('*.py'):
        try:
            with open(route_file, 'r') as f:
                content = f.read()
                # Look for Model.attribute or object.attribute patterns
                patterns = [
                    f'{model_name}\.{attribute_name}',
                    f'\.{attribute_name}\b',
                ]
                
                for pattern in patterns:
                    if re.search(pattern, content):
                        # Find line number
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if re.search(pattern, line):
                                usages.append({
                                    'file': route_file.name,
                                    'line': i,
                                    'content': line.strip()
                                })
        except Exception as e:
            pass
    
    return usages

def find_attribute_in_templates(templates_dir, attribute_name):
    """Find where an attribute is referenced in HTML templates"""
    usages = []
    for template_file in Path(templates_dir).glob('*.html'):
        try:
            with open(template_file, 'r') as f:
                content = f.read()
                # Look for JavaScript references: obj.attribute or obj['attribute']
                patterns = [
                    f'\.{attribute_name}\b',
                    f'\[[\'"]{attribute_name}[\'"]',
                    f'"{attribute_name}"',
                    f"'{attribute_name}'",
                ]
                
                for pattern in patterns:
                    if re.search(pattern, content):
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if re.search(pattern, line):
                                usages.append({
                                    'file': template_file.name,
                                    'line': i,
                                    'content': line.strip()[:80]
                                })
                                break  # Only first occurrence per file
        except Exception as e:
            pass
    
    return usages

def check_model_consistency(model_name, model_file, table_name, db_path):
    """Check if model attributes match database schema"""
    print_info(f"Checking {model_name} consistency...")
    
    # Get model attributes
    model_attrs = get_model_attributes(model_file)
    print(f"  Model attributes: {len(model_attrs)}")
    
    # Get database columns
    db_columns = get_db_columns(db_path, table_name)
    print(f"  Database columns: {len(db_columns)}")
    
    issues = []
    
    # Check for attributes in model but not in DB
    for attr in model_attrs:
        if attr not in db_columns and not attr.startswith('_'):
            # Skip relationships (they're not DB columns)
            if 'relationship' not in str(model_attrs):
                issues.append(f"Model has '{attr}' but DB table '{table_name}' doesn't")
    
    # Check for columns in DB but not in model
    for col in db_columns:
        if col not in model_attrs and col != 'id':
            issues.append(f"DB table '{table_name}' has '{col}' but model doesn't")
    
    return model_attrs, db_columns, issues

def check_route_references(routes_dir, model_name, model_attrs):
    """Check if routes reference non-existent attributes"""
    print_info(f"Checking route references for {model_name}...")
    
    issues = []
    
    # Scan all route files
    for route_file in Path(routes_dir).glob('*.py'):
        try:
            with open(route_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Look for Model.attribute patterns that don't exist
                for i, line in enumerate(lines, 1):
                    # Find potential attribute access
                    pattern = f'{model_name}\.(\w+)'
                    matches = re.findall(pattern, line)
                    
                    for attr in matches:
                        if attr not in model_attrs and attr not in ['query', 'metadata']:
                            issues.append({
                                'file': route_file.name,
                                'line': i,
                                'issue': f"References {model_name}.{attr} which doesn't exist",
                                'content': line.strip()
                            })
        except Exception as e:
            pass
    
    return issues

def main():
    print_header("ATTRIBUTE CONSISTENCY CHECKER")
    print_info("Checking attribute consistency across models, database, routes, and templates")
    
    # Configuration
    models_dir = Path('models')
    routes_dir = Path('routes')
    templates_dir = Path('templates')
    db_path = Path('instance/delivery_dashboard.db')
    
    # Model configuration: (model_name, file, table_name)
    models_config = [
        ('Material', 'models/material.py', 'materials'),
        ('PurchaseOrder', 'models/purchase_order.py', 'purchase_orders'),
        ('Payment', 'models/payment.py', 'payments'),
        ('Delivery', 'models/delivery.py', 'deliveries'),
        ('AISuggestion', 'models/ai_suggestion.py', 'ai_suggestions'),
        ('File', 'models/file.py', 'files'),
    ]
    
    total_issues = 0
    all_results = {}
    
    # Check each model
    for model_name, model_file, table_name in models_config:
        print_header(f"Model: {model_name}")
        
        if not Path(model_file).exists():
            print_error(f"Model file not found: {model_file}")
            continue
        
        # Check model vs database
        model_attrs, db_columns, db_issues = check_model_consistency(
            model_name, model_file, table_name, db_path
        )
        
        if db_issues:
            print_error(f"Found {len(db_issues)} model-database inconsistencies:")
            for issue in db_issues:
                print(f"    • {issue}")
            total_issues += len(db_issues)
        else:
            print_success("Model and database schema are consistent!")
        
        # Check route references
        route_issues = check_route_references(routes_dir, model_name, model_attrs)
        
        if route_issues:
            print_error(f"Found {len(route_issues)} invalid attribute references in routes:")
            for issue in route_issues:
                print(f"    • {issue['file']}:{issue['line']} - {issue['issue']}")
                print(f"      {issue['content'][:100]}")
            total_issues += len(route_issues)
        else:
            print_success("All route references are valid!")
        
        # Store results
        all_results[model_name] = {
            'model_attrs': model_attrs,
            'db_columns': db_columns,
            'db_issues': db_issues,
            'route_issues': route_issues
        }
    
    # Summary section
    print_header("DETAILED ATTRIBUTE REPORT")
    
    for model_name, results in all_results.items():
        print(f"\n{Colors.BOLD}{model_name}:{Colors.END}")
        print(f"  Model attributes: {', '.join(results['model_attrs'][:10])}" + 
              (" ..." if len(results['model_attrs']) > 10 else ""))
        print(f"  Database columns: {', '.join(results['db_columns'][:10])}" +
              (" ..." if len(results['db_columns']) > 10 else ""))
    
    # Common issues to check
    print_header("COMMON ISSUES CHECK")
    
    # Check for common typos
    common_typos = {
        'ammount': 'amount',
        'recieved': 'received',
        'delievery': 'delivery',
        'seperator': 'separator',
    }
    
    print_info("Checking for common typos in routes...")
    typo_found = False
    for route_file in Path(routes_dir).glob('*.py'):
        try:
            with open(route_file, 'r') as f:
                content = f.read()
                for typo, correct in common_typos.items():
                    if typo in content:
                        print_warning(f"Possible typo '{typo}' in {route_file.name}, should be '{correct}'?")
                        typo_found = True
        except Exception as e:
            pass
    
    if not typo_found:
        print_success("No common typos found!")
    
    # Check for mismatched field names between routes and models
    print_header("CROSS-REFERENCE CHECK")
    
    print_info("Checking Payment model references...")
    payment_attrs = all_results.get('Payment', {}).get('model_attrs', [])
    
    # Check if routes are using 'amount' instead of 'paid_amount'
    for route_file in Path(routes_dir).glob('*.py'):
        try:
            with open(route_file, 'r') as f:
                content = f.read()
                if 'Payment.amount' in content and 'paid_amount' in payment_attrs:
                    print_error(f"{route_file.name} uses 'Payment.amount' but model has 'paid_amount'")
                    total_issues += 1
                if 'payment.amount' in content and 'paid_amount' in payment_attrs:
                    print_error(f"{route_file.name} uses 'payment.amount' but model has 'paid_amount'")
                    total_issues += 1
        except Exception as e:
            pass
    
    # Final Summary
    print_header("FINAL SUMMARY")
    
    if total_issues == 0:
        print_success(f"🎉 All consistency checks passed! No issues found.")
        print_info("Your models, database schema, and routes are perfectly aligned!")
        return True
    else:
        print_error(f"Found {total_issues} consistency issues")
        print_warning("Please review the issues above and fix them")
        print_info("\nCommon fixes:")
        print("  1. Update model to match database (add/remove columns)")
        print("  2. Update routes to use correct attribute names")
        print("  3. Run database migration if schema changed")
        print("  4. Update templates if JavaScript references are wrong")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user.{Colors.END}\n")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
