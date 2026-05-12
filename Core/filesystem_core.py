# filesystem_core.py — Virtual Filesystem

import json
import os
import datetime

FS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fs.json")
FS_ROOT = "/home"


#  JSON helpers
def _load():
    if not os.path.exists(FS_FILE):
        default = {
            "cwd": "/home",
            "tree": {
                "/home": {
                    "type":     "dir",
                    "created":  _now(),
                    "modified": _now(),
                    "accessed": _now(),
                }
            }
        }
        _save(default)
        return default
    with open(FS_FILE, "r") as f:
        return json.load(f)


def _save(data):
    with open(FS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


#  Path helpers

def _resolve(cwd, path):
    if path == "~" or path == "":
        return FS_ROOT
    if path.startswith("/"):
        full = path
    else:
        full = cwd.rstrip("/") + "/" + path

    parts = []
    for p in full.split("/"):
        if p == "..":
            if parts:
                parts.pop()
        elif p and p != ".":
            parts.append(p)

    result = "/" + "/".join(parts)

    if not result.startswith(FS_ROOT):
        return FS_ROOT

    return result


def _children(tree, path):
    prefix = path.rstrip("/") + "/"
    result = []
    for k in tree:
        if k == path:
            continue
        if k.startswith(prefix):
            rest = k[len(prefix):]
            if "/" not in rest:
                result.append(k)
    return sorted(result)


def _basename(path):
    return path.split("/")[-1]


def _is_hidden(path):
    return _basename(path).startswith(".")


#  Public API

def get_cwd():
    return _load()["cwd"]


def pwd():
    return get_cwd()


def cd(path="~"):
    data = _load()
    target = _resolve(data["cwd"], path)
    tree   = data["tree"]

    if target not in tree:
        return False, f"cd: {path}: No such directory"
    if tree[target]["type"] != "dir":
        return False, f"cd: {path}: Not a directory"

    data["cwd"] = target
    _save(data)
    return True, target


def ls(flags=""):
    data    = _load()
    cwd     = data["cwd"]
    tree    = data["tree"]
    show_hidden = "-a" in flags
    long        = "-l" in flags

    children = _children(tree, cwd)

    if not show_hidden:
        children = [c for c in children if not _is_hidden(c)]

    if not children:
        return "(empty)"

    lines = []
    for c in children:
        node = tree[c]
        name = _basename(c)
        if long:
            t    = "d" if node["type"] == "dir" else "f"
            mod  = node.get("modified", "")
            size = len(node.get("content", "")) if node["type"] == "file" else "-"
            lines.append(f"{t}  {mod}  {str(size):>6}  {name}")
        else:
            suffix = "/" if node["type"] == "dir" else ""
            lines.append(name + suffix)

    return "\n".join(lines)


def mkdir(path, parents=False):
    data = _load()
    cwd  = data["cwd"]
    tree = data["tree"]
    path = path.replace(" ", "_")

    if parents:
        parts = path.split("/")
        current = cwd
        for part in parts:
            if not part:
                continue
            current = current.rstrip("/") + "/" + part
            if current not in tree:
                tree[current] = {"type": "dir", "created": _now(),
                                 "modified": _now(), "accessed": _now()}
        _save(data)
        return True, ""
    else:
        target = _resolve(cwd, path)
        if target in tree:
            return False, f"mkdir: {path}: Already exists"
        parent = "/".join(target.split("/")[:-1])
        if parent not in tree:
            return False, f"mkdir: {path}: Parent directory not found"
        tree[target] = {"type": "dir", "created": _now(),
                        "modified": _now(), "accessed": _now()}
        _save(data)
        return True, ""


def touch(path, flag=None, ref_file=None, date_str=None):
    data   = _load()
    cwd    = data["cwd"]
    tree   = data["tree"]
    target = _resolve(cwd, path)

    if target not in tree:
        if flag == "-c":
            return True, ""
        tree[target] = {
            "type":     "file",
            "content":  "",
            "created":  _now(),
            "modified": _now(),
            "accessed": _now(),
        }
    else:
        node = tree[target]
        now  = _now()
        if flag == "-a":
            node["accessed"] = now
        elif flag == "-m":
            node["modified"] = now
        elif flag == "-d" and date_str:
            node["modified"] = date_str
            node["accessed"] = date_str
        elif flag == "-r" and ref_file:
            ref_path = _resolve(cwd, ref_file)
            if ref_path in tree:
                node["modified"] = tree[ref_path]["modified"]
                node["accessed"] = tree[ref_path]["accessed"]
            else:
                return False, f"touch: {ref_file}: No such file"
        else:
            node["modified"] = now
            node["accessed"] = now

    _save(data)
    return True, ""


def stat(path):
    data   = _load()
    cwd    = data["cwd"]
    tree   = data["tree"]
    target = _resolve(cwd, path)

    if target not in tree:
        return False, f"stat: {path}: No such file or directory"

    node = tree[target]
    t    = "Directory" if node["type"] == "dir" else "File"
    size = len(node.get("content", "")) if node["type"] == "file" else "-"

    lines = [
        f"  File: {_basename(target)}",
        f"  Type: {t}",
        f"  Size: {size}",
        f"  Path: {target}",
        f"  Created:  {node.get('created',  '-')}",
        f"  Modified: {node.get('modified', '-')}",
        f"  Accessed: {node.get('accessed', '-')}",
    ]
    return True, "\n".join(lines)


def rm(path, flags=""):
    data   = _load()
    cwd    = data["cwd"]
    tree   = data["tree"]
    target = _resolve(cwd, path)

    if target not in tree:
        return False, f"rm: {path}: No such file or directory", False

    node = tree[target]

    if node["type"] == "dir" and "-r" not in flags:
        return False, f"rm: {path}: Is a directory (use rm -r)", False

    if "-i" in flags:
        return True, f"rm: remove '{_basename(target)}'? (y/n)", True

    keys_to_delete = [k for k in tree if k == target or k.startswith(target + "/")]
    for k in keys_to_delete:
        del tree[k]

    _save(data)

    msg = f"removed '{_basename(target)}'" if "-v" in flags else ""
    return True, msg, False


def rm_confirmed(path):
    """بتنفذ الـ rm بعد الـ confirmation"""
    data   = _load()
    cwd    = data["cwd"]
    tree   = data["tree"]
    target = _resolve(cwd, path)

    keys_to_delete = [k for k in tree if k == target or k.startswith(target + "/")]
    for k in keys_to_delete:
        del tree[k]
    _save(data)
    return f"removed '{_basename(target)}'"


def rmdir(path):
    data   = _load()
    cwd    = data["cwd"]
    tree   = data["tree"]
    target = _resolve(cwd, path)

    if target not in tree:
        return False, f"rmdir: {path}: No such directory"
    if tree[target]["type"] != "dir":
        return False, f"rmdir: {path}: Not a directory"
    if _children(tree, target):
        return False, f"rmdir: {path}: Directory not empty"

    del tree[target]
    _save(data)
    return True, ""


def cat(path):
    data   = _load()
    cwd    = data["cwd"]
    tree   = data["tree"]
    target = _resolve(cwd, path)

    if target not in tree:
        return False, f"cat: {path}: No such file"
    if tree[target]["type"] == "dir":
        return False, f"cat: {path}: Is a directory"

    content = tree[target].get("content", "")
    tree[target]["accessed"] = _now()
    _save(data)
    return True, content or "(empty)"


def write_file(path, content, append=False):
    data   = _load()
    cwd    = data["cwd"]
    tree   = data["tree"]
    target = _resolve(cwd, path)

    if target not in tree:
        return False, f"{path}: No such file"
    if tree[target]["type"] == "dir":
        return False, f"{path}: Is a directory"

    if append:
        tree[target]["content"] += content + "\n"
    else:
        tree[target]["content"] = content + "\n"

    tree[target]["modified"] = _now()
    _save(data)
    return True, ""


def mv(src, dst):
    data = _load()
    cwd  = data["cwd"]
    tree = data["tree"]

    src_path = _resolve(cwd, src)
    dst_path = _resolve(cwd, dst)

    if src_path not in tree:
        return False, f"mv: {src}: No such file or directory"

    if dst_path in tree and tree[dst_path]["type"] == "dir":
        dst_path = dst_path.rstrip("/") + "/" + _basename(src_path)

    if dst_path in tree:
        return False, f"mv: {dst}: Destination already exists"

    dst_parent = "/".join(dst_path.split("/")[:-1])
    if dst_parent not in tree:
        return False, f"mv: {dst}: No such directory"

    keys_to_move = [k for k in tree if k == src_path or k.startswith(src_path + "/")]

    for old_key in keys_to_move:
        new_key = dst_path + old_key[len(src_path):]
        tree[new_key] = tree.pop(old_key)

    if dst_parent in tree:
        tree[dst_parent]["modified"] = _now()

    _save(data)
    return True, ""


def find(name, start_path=None):
    data = _load()
    tree = data["tree"]

    if start_path is None:
        start_path = FS_ROOT

    results = []

    for path in tree:

        if path == FS_ROOT:
            continue


        if not path.startswith(start_path.rstrip("/") + "/") and path != start_path:
            continue


        if _basename(path) == name:
            results.append(path)

    if not results:
        return False, f"find: '{name}': No such file or directory"

    return True, "\n".join(results)



def get_tree_for_ui():
    data = _load()
    tree = data["tree"]

    def build(parent, depth):
        result = []
        for child in _children(tree, parent):
            node = tree[child]
            result.append({
                "path":  child,
                "name":  _basename(child),
                "type":  node["type"],
                "depth": depth,
            })
        return result

    return build(FS_ROOT, 0), data["cwd"]