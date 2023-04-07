import os
from pathlib import Path

import yaml

PATH_ROOT = Path(__file__).parent.parent.parent

def write_yaml_file(data, filename):
    with open(filename, 'w') as outfile:
        yaml.dump(data, outfile)

def parse_multiline_string(string):
    dic = {}
    for line in string.splitlines():
        line = line.replace(r"\\", "")
        if ":" in line:
            key, line = line.split(":", 1)
            key = key.strip()
            dic[key] = ""
            line = line.strip()
            if "]" in line:
                line = line.split("]", 1)[1][1:-1]
        dic[key] += line
    for key in dic:
        dic[key] = [val.strip() for val in dic[key].split("&") if val.strip()]

    return dic


def get_sections(text):
    sections = []
    in_section = False
    section_lines = []
    for line in text.split("\n"):
        if line.strip() == "\\begin{recipedef}":
            in_section = True
            section_lines = []
        elif line.strip() == "\\end{recipedef}":
            in_section = False
            sections.append('\n'.join(section_lines))
        elif in_section:
            section_lines.append(line)
    return sections


class RecipeSectionReader:
    def __init__(self, text=None, filename=None):
        if filename is not None and text is None:
            text = open(filename, "r").read()

        self.filename = filename
        self.text = text
        self.recipe_texts = get_sections(text)
        self.dicts = {}
        for text in self.recipe_texts:
            dic = parse_multiline_string(text)
            name = dic.get("Recipe name", dic.get("Name", ["<untitled>"]))[0]
            self.dicts[name] = dic

    def writeto(self, dirname="."):
        if not os.path.exists(dirname):
            os.mkdir(dirname)

        fname = os.path.basename(self.filename).replace(".tex", ".yaml")
        file_path = os.path.join(dirname, fname)
        write_yaml_file(self.dicts, file_path)

    def write_individual(self, dirname="."):
        if not os.path.exists(dirname):
            os.mkdir(dirname)

        for key in self.dicts.keys():
            if "\REC{" in key:
                fname = key.replace("\REC{", "REC_").replace("}", "") + ".yaml"
            elif "\DRL{" in key:
                fname = key.replace("\DRL{", "FUNC_").replace("}", "") + ".yaml"
            file_path = os.path.join(dirname, fname)
            write_yaml_file(self.dicts[key], file_path)

    def __repr__(self):
        text = ""
        for name in self.dicts.keys():
            text += f"--- {name} ---\n\n"
            for key, value in self.dicts[name].items():
                text += f"{key} :\n"
                text += "    - "+'\n    - '.join(value)+"\n"
            text += "\n\n"

        return text


ocz = "Recipes_Imaging_LM.tex"
wka = "LSS_drl_functions.tex"

rec = RecipeSectionReader(filename=PATH_ROOT / wka)
print(rec)
# rec.writeto("functions")
#rec.write_individual("recipes")

