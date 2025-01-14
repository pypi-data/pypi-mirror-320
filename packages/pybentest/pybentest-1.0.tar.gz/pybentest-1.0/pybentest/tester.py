import os
import argparse
import subprocess
import sys
from glob import glob
import tkinter as tk
from importlib.util import find_spec
from tkinter import ttk


def detect_files(directory='.', module='', regex='**/test_*.py'):
    """Return a list of possible python pytest files in root (recursive)

    :param directory: Root directory of test files
    :param module: Locate test files in a python module instead of directory
    :param regex: Regex to match test files
    :return: List of files matching the regex
    """
    if module:
        spec = find_spec(module)
        if spec is None or spec.submodule_search_locations is None:
            raise ValueError(f"Module '{module}' not found or is not a package.")

        module_path = spec.submodule_search_locations[0]

        # Use glob to find all matching files
        file_paths = glob(f'{module_path}/{regex}', recursive=True)

        # Convert file paths to module names
        module_list = []
        for file_path in file_paths:
            relative_path = os.path.relpath(file_path, module_path)
            module_name = relative_path.replace(os.path.sep, '.')[:-3]  # Remove `.py` extension
            module_list.append(f"{module}.{module_name}")

        return module_list
    else:
        root_path = str(os.path.abspath(directory))
        matching = glob(regex, root_dir=root_path, recursive=True)
        return [os.path.join(root_path, i) for i in matching]


class PyBENTester:
    def __init__(self, parent_window,
                 root_dir='.',
                 module='',
                 regex='**/test_*.py',
                 prefix='pytest',
                 suffix=''):
        """Tester application helping find and execute test files

        :param parent_window: Parent window for the TK application
        :param root_dir: Root directory of test files
        :param module: Locate test files in a python module instead of directory
        :param regex: Regex to match test files
        :param prefix: python module to execute each test file with
        :param suffix: Arguments to pass to each test file execution
        """
        self.root_window = parent_window
        self.root_window.title("PyBEN Tester v1.0")
        self.root_dir = root_dir
        self.module = module
        self.regex = regex
        self.prefix = prefix
        self.suffix = suffix
        self.list_width = 100

        if self.module and self.prefix == 'pytest':
            self.prefix = 'pytest --pyargs'

        # Sample file list
        self.file_list = detect_files(directory=self.root_dir, module=self.module, regex=self.regex)

        self.selected_files = []

        # Create main frame for layout
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left list: Original file list
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        left_label = ttk.Label(left_frame, text="Available Files")
        left_label.pack()

        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=5)

        search_label = ttk.Label(search_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_files)

        self.left_listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE, height=15, width=self.list_width)
        self.left_listbox.pack(fill=tk.BOTH, expand=True)

        for file in self.file_list:
            self.left_listbox.insert(tk.END, file)

        move_to_selected_button = ttk.Button(left_frame, text="Move to Selected", command=self.move_to_selected)
        move_to_selected_button.pack(pady=5)

        # Right list: Selected files
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        right_label = ttk.Label(right_frame, text="Selected Files")
        right_label.pack()

        self.right_listbox = tk.Listbox(right_frame, selectmode=tk.EXTENDED, height=15, width=self.list_width)
        self.right_listbox.pack(fill=tk.BOTH, expand=True)

        # Buttons for moving selected files
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=5)

        move_to_available_button = ttk.Button(button_frame, text="Move to Available", command=self.move_to_available)
        move_to_available_button.pack(side=tk.LEFT, padx=5)

        move_up_button = ttk.Button(button_frame, text="Move Up", command=self.move_up)
        move_up_button.pack(side=tk.LEFT, padx=5)

        move_down_button = ttk.Button(button_frame, text="Move Down", command=self.move_down)
        move_down_button.pack(side=tk.LEFT, padx=5)

        action_button = ttk.Button(button_frame, text="Initiate Action", command=self.initiate_action)
        action_button.pack(side=tk.RIGHT, padx=5)

    def search_files(self, event):
        query = self.search_entry.get().lower()
        self.left_listbox.delete(0, tk.END)
        for file in self.file_list:
            if query in file.lower():
                self.left_listbox.insert(tk.END, file)

    def move_to_selected(self):
        selected_index = self.left_listbox.curselection()
        if selected_index:
            selected_file = self.file_list.pop(selected_index[0])
            self.selected_files.append(selected_file)

            self.left_listbox.delete(selected_index[0])
            self.right_listbox.insert(tk.END, selected_file)

    def move_to_available(self):
        selected_indices = list(self.right_listbox.curselection())[::-1]
        for index in selected_indices:
            selected_file = self.selected_files.pop(index)
            self.file_list.append(selected_file)

            self.right_listbox.delete(index)
            self.left_listbox.insert(tk.END, selected_file)

    def move_up(self):
        selected_indices = self.right_listbox.curselection()
        for index in selected_indices:
            if index > 0:
                self.selected_files[index], self.selected_files[index - 1] = self.selected_files[index - 1], \
                    self.selected_files[index]
                self.right_listbox.delete(index)
                self.right_listbox.insert(index - 1, self.selected_files[index - 1])
                self.right_listbox.select_set(index - 1)

    def move_down(self):
        selected_indices = list(self.right_listbox.curselection())[::-1]
        for index in selected_indices:
            if index < len(self.selected_files) - 1:
                self.selected_files[index], self.selected_files[index + 1] = self.selected_files[index + 1], \
                    self.selected_files[index]
                self.right_listbox.delete(index)
                self.right_listbox.insert(index + 1, self.selected_files[index + 1])
                self.right_listbox.select_set(index + 1)

    def initiate_action(self):
        selected_files = self.selected_files
        print("Selected files in order:", selected_files)
        for i in self.selected_files:
            main_args = [sys.executable, '-m'] + self.prefix.split() + [' ', i, ' '] + self.suffix.split()
            subprocess.run(main_args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', default='.', help="Root directory of test files",
                        required=False)
    parser.add_argument('-m', '--module', default='', required=False,
                        help='Locate test files in a python module instead of directory')
    parser.add_argument('-r', '--regex', default=f'**/test_*.py', help="Regex to match test files",
                        required=False)
    parser.add_argument('-p', '--prefix', default='pytest', required=False,
                        help="python module to execute each test file with")
    parser.add_argument('-a', '--args', default='', required=False,
                        help="Arguments to pass to each test file execution")
    args = parser.parse_args()

    root = tk.Tk()
    app = PyBENTester(parent_window=root,
                      root_dir=args.directory,
                      module=args.module,
                      regex=args.regex,
                      prefix=args.prefix,
                      suffix=args.args
                      )
    root.mainloop()
