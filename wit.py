#upload176

import filecmp
import os
import random
import re
import shutil
import string
import sys

from time import gmtime, strftime

from graphviz import Digraph


def init():
    os.makedirs('.wit/images/')
    os.makedirs('.wit/staging_area/')
    modify_active_file("master", f"{os.getcwd()}\\.wit")
    with open(".wit/references.txt", "w") as file:
        file.write("HEAD=\nmaster=\n")


def copyanything(src, dst):
    try:
        print("coping 'src", src, "to dst", dst)
        shutil.copytree(src, dst)
    except NotADirectoryError:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)


# def create_commit_id_folder(commit_id):
#     os.makedirs('.wit/images/' + commit_id + '/')


def get_head_id(wit_folder):
    commit_id = "None"
    if os.path.isfile(f"{wit_folder}/references.txt"):
        with open(f"{wit_folder}/references.txt", "r") as file:
            # commit_id = file.read()
            result = re.search("HEAD=(.*)", file.read())
            commit_id = result.group(1)
    return commit_id


def get_branch_ref(branch, wit_folder):
    if os.path.isfile(f"{wit_folder}/references.txt"):
        with open(f"{wit_folder}/references.txt", "r") as file:
            result = re.search(f"{branch}=(.*)", file.read())
            if result is None:
                return
            branch_ref = result.group(1)
    return branch_ref


def get_master_id(wit_folder):
    commit_id = "None"
    if os.path.isfile(f"{wit_folder}/references.txt"):
        with open(f"{wit_folder}/references.txt", "r") as file:
            # commit_id = file.read()
            result = re.search("master=(.*)", file.read())
            commit_id = result.group(1)
    return commit_id


def create_metadata_file(commit_id, commit_msg, wit_folder):
    parent = get_head_id(wit_folder)
    str_date = strftime("%a %b %d %H:%M:%S %Y +03:00", gmtime())
    with open(f"{wit_folder}/images/{commit_id}.txt", "w") as file:
        file.write(f"parent={parent}\ndate={str_date}\nmessage={commit_msg}")
    file.close()


def copy_statging_area(commit_id, wit_folder):
    src = f"{wit_folder}\staging_area"
    dst = f"{wit_folder}\images\\{commit_id}\\"
    copyanything(src, dst)


def copy_branch_to_staging(dst_folder, wit_folder):
    src = f"{wit_folder}\images\\{dst_folder}\\"
    dst = f"{wit_folder}\staging_area"
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s)
        else:
            shutil.copy2(s, d)


def set_references(commit_id, wit_folder, master_id=None, is_commit=True, update_branch=None):
    print('update branch', update_branch)
    head_id = get_head_id(wit_folder)
    print('head_id', head_id)
    if master_id is None:
        master_id = get_master_id(wit_folder)
        print('master_id', master_id)
    if master_id == head_id and is_commit and update_branch is None or update_branch == "master":
        master_id = commit_id
    with open(f"{wit_folder}/references.txt") as file:
        lines = file.readlines()
        lines[0] = f"HEAD={commit_id}\n"
        lines[1] = f"master={master_id}\n"
        if update_branch is not None and update_branch != "master":
            lines[-1] = f"{update_branch}={commit_id}"
    with open(f"{wit_folder}/references.txt", "w") as f:
        f.writelines(lines)


def modify_active_file(branch_name, wit_folder):
    with open(f"{wit_folder}/activated.txt", "w") as file:
        file.write(f"{branch_name}")


def set_branch_references(branch_name, wit_folder):
    branch_line = f"{branch_name}={get_head_id(wit_folder)}"
    with open(f"{wit_folder}/references.txt", "a") as file:
        file.write("\n")
        file.write(branch_line)


def get_folder_and_files(folder):
    files_to_commit = "\n"
    for r, _d, f in os.walk(folder):
        for file in f:
            files_to_commit += os.path.join(r, file) + "\n"
    return files_to_commit


def check_and_get_wit_folder():
    current_folder = os.getcwd()
    result = False
    while current_folder != os.path.dirname(current_folder) and not result:
        result = does_contain_with_folder(current_folder)
        current_folder = os.path.dirname(current_folder)
    return result


def does_contain_with_folder(folder):
    if ".wit" in os.listdir(folder):
        return f"{folder}\.wit"
    else:
        return False


def print_not_staged(wit_folder):
    work_folder = wit_folder[:-5]
    staging_folder = f"{wit_folder}\staging_area"
    d1_contents = set(os.listdir(work_folder))
    d2_contents = set(os.listdir(staging_folder))
    common = list(d1_contents & d2_contents)
    common_files = [f
                    for f in common
                    if os.path.isfile(os.path.join(work_folder, f))]
    match, mismatch, errors = filecmp.cmpfiles(work_folder,
                                               staging_folder,
                                               common_files)
    return mismatch


def get_untracked_files(wit_folder):
    work_folder = wit_folder[:-5]
    staging_folder = f"{wit_folder}\staging_area"
    d1_contents = set()
    d2_contents = set()
    for subdir, _dirs, files in os.walk(work_folder):
        for file in files:
            if not subdir.__contains__(".wit"):
                d1_contents.add(subdir + os.sep + file)

    for subdir, _dirs, files in os.walk(staging_folder):
        for file in files:
            temp_subdir = subdir.replace(staging_folder, work_folder)
            d2_contents.add(temp_subdir + os.sep + file)

    return d1_contents - d2_contents


def copy_files_from_commit(commit_id, wit_folder):
    folder = f"{wit_folder}\images\{commit_id}"
    root_folder = wit_folder[:-5]
    print('ma')
    for r, _d, f in os.walk(folder):
        for file in f:
            file_path = f"{r}\\{file}"
            file_path_to_copy = file_path.replace(folder, root_folder)
            print(file_path_to_copy)
            shutil.copyfile(file_path, file_path_to_copy)


def get_activate_branch(wit_folder):
    with open(f"{wit_folder}/activated.txt", "r") as file:
        return file.read()


def get_commit_id_by_branch(checkout, wit_folder):
    if os.path.isfile(f"{wit_folder}/references.txt"):
        with open(f"{wit_folder}/references.txt", "r") as file:
            result = re.search(f"{checkout}=(.*)", file.read())
            branch_commit_id = result.group(1)
    return branch_commit_id


def get_parent_id(head_id, wit_folder):
    with open(f"{wit_folder}\images\{head_id}.txt", "r") as file:
        result = re.search("parent=(.*)", file.read())
        parent_id = result.group(1)
    return parent_id


def create_commit(msg_to_commit, wit_folder):
    generated_commit_id = ''.join(random.choice(string.digits + string.ascii_lowercase[:6]) for _ in range(40))
    print('commit_id', generated_commit_id)
    active_branch = get_activate_branch(wit_folder)
    head_id = get_head_id(wit_folder)
    update_branch = None
    if head_id == get_branch_ref(active_branch, wit_folder):
        update_branch = active_branch
        modify_active_file(generated_commit_id, wit_folder)
    create_metadata_file(generated_commit_id, msg_to_commit, wit_folder)
    set_references(generated_commit_id, wit_folder, update_branch=update_branch)
    copy_statging_area(generated_commit_id, wit_folder)


def is_folders_equal(head_id, wit_folder):
    head_folder = f"{wit_folder}\images\{head_id}"
    staging_folder = f"{wit_folder}\staging_area"
    d1_contents = set(os.listdir(head_folder))
    d2_contents = set(os.listdir(staging_folder))
    common = list(d1_contents & d2_contents)
    common_files = [f
                    for f in common
                    if os.path.isfile(os.path.join(wit_folder[:-4], f))]
    match, mismatch, errors = filecmp.cmpfiles(head_folder,
                                               staging_folder,
                                               common_files)
    return len(mismatch) == 0


if sys.argv[1] == "init":
    init()

if sys.argv[1] == "add":
    wit_folder = check_and_get_wit_folder()
    if wit_folder:
        src = f'{wit_folder[:-5]}\\{sys.argv[2]}'
        dst = f"{wit_folder}\staging_area\\{sys.argv[2]}"
        copyanything(src, dst)
    else:
        print("not wit folder")

if sys.argv[1] == "commit":
    wit_folder = check_and_get_wit_folder()
    if wit_folder:
        try:
            commit_msg = sys.argv[2]
            create_commit(commit_msg, wit_folder)
        except IndexError:
            print("dont forget commit msg")
    else:
        print("not wit folder")

if sys.argv[1] == "status":
    wit_folder = check_and_get_wit_folder()
    if wit_folder:
        print("commit id = ", get_head_id(wit_folder))
        print("Changes to be commited")
        print("-----------------------------")
        print(get_folder_and_files(f"{wit_folder}\staging_area"))
        print("Changes not staged for commit")
        print("-----------------------------")
        print('\n'.join(print_not_staged(wit_folder)))
        print("Untracked files")
        print("-----------------------------")
        print('\n'.join(get_untracked_files(wit_folder)))
        print("-----------------------------")
        print("commit id = ", get_head_id(wit_folder))
    else:
        print("not wit folder")

if sys.argv[1] == "checkout":
    wit_folder = check_and_get_wit_folder()
    if wit_folder:
        checkout = sys.argv[2]
        print("checked out to branch", checkout)
        if checkout == "master":
            commit_id = get_master_id(wit_folder)
        if len(checkout) < 40:
            commit_id = get_commit_id_by_branch(checkout, wit_folder)
            modify_active_file(checkout, wit_folder)
        else:
            commit_id = checkout
            modify_active_file("", wit_folder)
        copy_files_from_commit(commit_id, wit_folder)
        set_references(commit_id, wit_folder, is_commit=False)
    else:
        print("not wit folder")

if sys.argv[1] == "graph":
    wit_folder = check_and_get_wit_folder()
    if wit_folder:
        dot = Digraph(comment='wit graph')
        dot  # doctest: +ELLIPSIS
        head_id = get_head_id(wit_folder)
        master_id = get_master_id(wit_folder)
        if head_id == master_id:
            parent_id = get_parent_id(head_id, wit_folder)
            dot.node('A', 'Head')
            dot.node('B', 'master')
            dot.node('C', head_id)
            dot.node('D', parent_id)
            dot.edges(['AC', 'BC'])
            dot.edge('C', 'D', constraint='false')
        else:
            parent_id = get_parent_id(head_id, wit_folder)
            print('hcil', parent_id)
            dot.node('A', 'Head')
            dot.node('B', head_id)
            dot.edge('A', 'B', constraint='false')
            if parent_id != "None":
                dot.node('D', parent_id)
                dot.edge('B', 'D', constraint='false')
        print(dot.source)  # doctest: +NORMALIZE_WHITESPACE
        dot.render('test-output/round-table.gv', view=True)  # doctest: +SKIP
    else:
        print("not wit folder")

if sys.argv[1] == "branch":
    wit_folder = check_and_get_wit_folder()
    if wit_folder:
        branch_name = sys.argv[2]
        set_branch_references(branch_name, wit_folder)
        modify_active_file(branch_name, wit_folder)
    else:
        print("not wit folder")

if sys.argv[1] == "merge":
    wit_folder = check_and_get_wit_folder()
    if wit_folder:
        head_id = get_head_id(wit_folder)
        if is_folders_equal(head_id, wit_folder):
            print('merging')
            branch_name = sys.argv[2]
            copy_branch_to_staging(get_branch_ref(branch_name, wit_folder), wit_folder)
            create_commit(f"Merging branch {branch_name}", wit_folder)
    else:
        print("not wit folder")

if sys.argv[1] == "test":
    wit_folder = check_and_get_wit_folder()
    print(wit_folder)
    if wit_folder:
        print(wit_folder[:-5])
