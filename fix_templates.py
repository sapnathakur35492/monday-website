import os

paths = [
    r'c:\Users\Santosh\Desktop\New_project\templates\webapp\partials\item_row.html',
    r'c:\Users\Santosh\Desktop\New_project\templates\webapp\partials\item_row_final.html',
    r'c:\Users\Santosh\Desktop\New_project\templates\webapp\partials\item_row_fixed.html'
]

for p in paths:
    try:
        if not os.path.exists(p):
            print(f"File not found: {p}")
            continue
            
        with open(p, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = content
        if "val=='true'" in content:
            new_content = new_content.replace("val=='true'", "val == 'true'")
        if "val==True" in content:
            new_content = new_content.replace("val==True", "val == True")
            
        if new_content != content:
            with open(p, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed {p}")
        else:
            print(f"No changes needed for {p}")
            
    except Exception as e:
        print(f"Error processing {p}: {e}")
