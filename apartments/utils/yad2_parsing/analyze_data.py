import json
import os
import sys

def analyze_apartment_data(file_path):
    """
    Analyze apartment data to check for null or empty values in each field.
    
    Args:
        file_path: Path to the processed apartments JSON file
    """
    print(f"Analyzing apartment data in {file_path}")
    
    try:
        # Read the processed apartments
        with open(file_path, 'r', encoding='utf-8') as f:
            apartments = json.load(f)
        
        total_apartments = len(apartments)
        print(f"Total apartments: {total_apartments}")
        
        if total_apartments == 0:
            print("No apartments found in the file.")
            return
        
        # Get all keys from the first apartment
        all_keys = set()
        for apt in apartments:
            all_keys.update(apt.keys())
        
        # Initialize counters for each key
        null_counts = {key: 0 for key in all_keys}
        empty_counts = {key: 0 for key in all_keys}
        
        # Count null and empty values for each key
        for apt in apartments:
            for key in all_keys:
                # Check if key exists
                if key not in apt:
                    null_counts[key] += 1
                    continue
                
                value = apt.get(key)
                
                # Check for null values
                if value is None:
                    null_counts[key] += 1
                
                # Check for empty strings or lists
                elif (isinstance(value, str) and value == "") or \
                     (isinstance(value, list) and len(value) == 0):
                    empty_counts[key] += 1
        
        # Print results
        print("\nAnalysis Results:")
        print("-" * 60)
        print(f"{'Field':<25} {'Null Count':<15} {'Empty Count':<15} {'Total Missing':<15} {'% Missing':<10}")
        print("-" * 60)
        
        for key in sorted(all_keys):
            total_missing = null_counts[key] + empty_counts[key]
            percent_missing = (total_missing / total_apartments) * 100
            
            print(f"{key:<25} {null_counts[key]:<15} {empty_counts[key]:<15} {total_missing:<15} {percent_missing:.2f}%")
        
        print("-" * 60)
        
        # Print summary of value distributions for important fields
        analyze_field_values(apartments, 'number_of_rooms')
        analyze_field_values(apartments, 'total_price')
        analyze_field_values(apartments, 'area')
        analyze_field_values(apartments, 'type')
        
    except Exception as e:
        print(f"Error analyzing data: {e}")

def analyze_field_values(apartments, field):
    """
    Analyze the distribution of values for a specific field.
    
    Args:
        apartments: List of apartment dictionaries
        field: Field to analyze
    """
    print(f"\nValue distribution for '{field}':")
    
    # Count occurrences of each value
    value_counts = {}
    for apt in apartments:
        value = apt.get(field)
        
        # Convert numeric values to ranges for better grouping
        if field == 'number_of_rooms' and isinstance(value, (int, float)):
            value = f"{int(value)} rooms"
        elif field == 'total_price' and isinstance(value, (int, float)):
            # Group prices into ranges
            if value < 1000:
                value = "< 1,000"
            elif value < 2000:
                value = "1,000 - 1,999"
            elif value < 3000:
                value = "2,000 - 2,999"
            elif value < 4000:
                value = "3,000 - 3,999"
            elif value < 5000:
                value = "4,000 - 4,999"
            else:
                value = "5,000+"
        
        if value in value_counts:
            value_counts[value] += 1
        else:
            value_counts[value] = 1
    
    # Sort by count (descending)
    sorted_values = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Print top 10 values
    print(f"{'Value':<25} {'Count':<10} {'Percentage':<10}")
    print("-" * 45)
    
    total = len(apartments)
    for value, count in sorted_values[:10]:  # Show top 10
        percent = (count / total) * 100
        value_str = str(value)[:24]  # Truncate long values
        print(f"{value_str:<25} {count:<10} {percent:.2f}%")
    
    # If there are more values, show a summary
    if len(sorted_values) > 10:
        remaining_count = sum(count for _, count in sorted_values[10:])
        remaining_percent = (remaining_count / total) * 100
        print(f"{'Other values':<25} {remaining_count:<10} {remaining_percent:.2f}%")

if __name__ == "__main__":
    # Path to the processed apartments file
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed_apartments.json')
    
    # Run the analysis
    analyze_apartment_data(file_path)
