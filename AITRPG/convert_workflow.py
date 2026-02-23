import json
import requests
import sys

def convert_ui_to_api(ui_path, api_path, base_url="http://127.0.0.1:8188"):
    try:
        resp = requests.get(f"{base_url}/object_info")
        resp.raise_for_status()
        object_info = resp.json()
    except Exception as e:
        print(f"Failed to get object_info: {e}")
        return False
        
    with open(ui_path, "r", encoding="utf-8") as f:
        ui_data = json.load(f)
        
    if "nodes" not in ui_data:
        print("Not a UI format workflow.")
        return False

    api_dict = {}
    
    link_map = {}
    for link in ui_data.get("links", []):
        if isinstance(link, list) and len(link) >= 4:
            link_map[link[0]] = [str(link[1]), link[2]]

    for node in ui_data.get("nodes", []):
        nid = str(node["id"])
        ctype = node["type"]
        
        inputs = {}
        
        # Add linked inputs
        if "inputs" in node:
            for inp in node["inputs"]:
                iname = inp["name"]
                if "link" in inp and inp["link"] is not None:
                    link_id = inp["link"]
                    if link_id in link_map:
                        inputs[iname] = link_map[link_id]
                        
        # Add widget values
        if ctype in object_info:
            node_def = object_info[ctype]
            input_def = node_def.get("input", {})
            required = input_def.get("required", {})
            
            # Find which required inputs are widgets (i.e. not links)
            widget_names = []
            for k, v in required.items():
                # inputs in `required` that are not already linked
                if k not in inputs:
                    widget_names.append(k)
                    
            if "widgets_values" in node:
                w_vals = node["widgets_values"]
                for i, wname in enumerate(widget_names):
                    if i < len(w_vals):
                        # Some widgets like seed in KSampler are complex, but usually mapping by order works
                        inputs[wname] = w_vals[i]
        
        api_dict[nid] = {
            "class_type": ctype,
            "inputs": inputs
        }
        
    with open(api_path, "w", encoding="utf-8") as f:
        json.dump(api_dict, f, indent=2, ensure_ascii=False)
        
    print(f"Converted {ui_path} to {api_path}")
    return True

if __name__ == "__main__":
    convert_ui_to_api("HAYAME.json", "HAYAME_api.json")
    convert_ui_to_api("chara.json", "chara_api.json")
    convert_ui_to_api("ワークフロウ/TALOTTO.json", "TALOTTO_api.json")
