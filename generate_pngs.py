import urllib.request
import json
import re
import os

def main():
    puml_path = r"c:\Users\ST\OneDrive\Documents\University work\SCD Lab\project\system_diagrams.puml"
    
    if not os.path.exists(puml_path):
        print("Could not find system_diagrams.puml")
        return
        
    with open(puml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(r'@startuml\n(.*?)\n@enduml', re.DOTALL)
    matches = pattern.findall(content)

    if not matches:
        print("No plantuml diagrams found in the file.")
        return

    names = ['use_case', 'class', 'sequence', 'activity', 'erd']
    out_dir = r"c:\Users\ST\OneDrive\Documents\University work\SCD Lab\project"

    for i, match in enumerate(matches):
        if i >= len(names):
            break
            
        print(f"Generating {names[i]}_diagram.png...", flush=True)
        payload = json.dumps({'diagram_source': f"@startuml\n{match}\n@enduml"})
        req = urllib.request.Request('https://kroki.io/plantuml/png', data=payload.encode('utf-8'), headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
        
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                png_data = response.read()
                out_path = os.path.join(out_dir, f'{names[i]}_diagram.png')
                with open(out_path, 'wb') as out_f:
                    out_f.write(png_data)
            print(f'Successfully saved {names[i]}_diagram.png')
        except Exception as e:
            print(f'Failed to save {names[i]}_diagram.png: {e}')

if __name__ == "__main__":
    main()
