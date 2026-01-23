
path = r'C:/Users/Santosh/Documents/New_project/templates/webapp/partials/item_row_final.html'
try:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for the bad pattern
    bad_patterns = ["val=='true'", "val==True"]
    new_content = content
    
    for pat in bad_patterns:
        if pat in content:
            print(f"Found bad pattern: {pat}")
            # Replace with spaces
            fixed = pat.replace("==", " == ")
            new_content = new_content.replace(pat, fixed)
            
    if content != new_content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("File updated successfully.")
    else:
        print("No syntax errors found (patterns not present).")
        
except Exception as e:
    print(f"Error: {e}")
