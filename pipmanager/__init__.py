import tkinter as tk
from tkinter import ttk, messagebox
import sys, os, threading, subprocess, requests
from importlib.metadata import distributions
from datetime import datetime
from importlib.util import find_spec

class PipManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pip Package Manager")
        self.root.geometry("800x600")
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search frame
        self.search_frame = ttk.Frame(self.main_frame)
        self.search_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.search_button = ttk.Button(self.search_frame, text="Search PyPI", command=self.search_pypi)
        self.search_button.pack(side=tk.LEFT, padx=(5, 0))

        # Add "Search Local Packages" Button
        self.search_local_button = ttk.Button(self.search_frame, text="Search Local Packages", command=self.search_local_packages)
        self.search_local_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Package list frame
        self.list_frame = ttk.Frame(self.main_frame)
        self.list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for packages
        columns = ("Package", "Version", "Size", "Actions")
        self.tree = ttk.Treeview(self.list_frame, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=100)
        
        self.tree.column("Package", width=200)
        self.tree.column("Actions", width=200)
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.on_tree_item_double_click)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Load packages
        self.load_packages()
    
    def get_package_size(self, package_name):
        try:
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
            if response.status_code == 200:
                data = response.json()
                for url_info in data["urls"]:
                    if "size" in url_info:
                        size = url_info["size"]
                        return f"{size / 1024 / 1024:.1f} MB"
            return "N/A"
        except Exception as e:
            print(f"Error fetching size for {package_name}: {e}")
            return "N/A"
    
    def load_packages(self):
        self.status_var.set("Loading packages...")
        self.tree.delete(*self.tree.get_children())
        
        def load():
            try:
                for dist in distributions():
                    try:
                        package_name = dist.metadata['Name']
                        version = dist.version
                        size = self.get_package_size(package_name)
                        
                        # Insert package info into treeview with a placeholder for "Actions"
                        self.tree.insert("", tk.END, values=(package_name, version, size, "Update | Uninstall"))
                        
                    except Exception as pkg_error:
                        # Skip packages that cause errors during metadata retrieval
                        print(f"Error processing package {dist}: {pkg_error}")
                        continue
                
                self.status_var.set("Ready")
            except Exception as e:
                self.status_var.set(f"Error loading packages: {str(e)}")
        
        thread = threading.Thread(target=load)
        thread.daemon = True
        thread.start()

    def search_local_packages(self):
        query = self.search_var.get().strip().lower()
        if not query:
            self.load_packages()
            return

        self.status_var.set(f"Searching installed packages for '{query}'...")
        self.tree.delete(*self.tree.get_children())

        def search():
            try:
                for dist in distributions():
                    try:
                        package_name = dist.metadata.get("Name", "Unknown Package")
                        if query in package_name.lower():
                            version = dist.version
                            size = self.get_package_size(package_name)
                            self.tree.insert("", tk.END, values=(package_name, version, size, "Update | Uninstall"))
                    except Exception as pkg_error:
                        print(f"Error processing package {dist}: {pkg_error}")
                self.status_var.set("Search complete.")
            except Exception as e:
                self.status_var.set(f"Error during search: {str(e)}")

        thread = threading.Thread(target=search)
        thread.daemon = True
        thread.start()

    def sort_by_column(self, col):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children("")]
        is_numeric = col == "Size"
        
        if is_numeric:
            # Convert size values to floats for sorting
            data.sort(key=lambda x: float(x[0].replace(" MB", "").replace("N/A", "0")), reverse=True)
        else:
            data.sort(key=lambda x: x[0].lower())
        
        # Reorder rows in the Treeview
        for index, (_, child) in enumerate(data):
                self.tree.move(child, "", index)
    def on_tree_item_double_click(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        values = self.tree.item(selected_item, "values")
        package_name = values[0]

        # Create a new window
        child_window = tk.Toplevel(self.root)
        child_window.title(f"Manage Package: {package_name}")
        child_window.geometry("330x250")
        child_window.transient(self.root)  # Set as a child window

        child_window.after(10, lambda: child_window.grab_set())
        child_window.resizable(False, False)
        # Create a label
        label = ttk.Label(
            child_window,
            text=f"What would you like to do with '{package_name}'?",
            wraplength=330,
        )
        label.pack(pady=10, padx=10)
        # Create another label for installation date
        label1 = ttk.Label(
            child_window,
            text=f"Installation Date: {self.get_installation_date(package_name)}",
            wraplength=340,
        )
        label1.pack(pady=10, padx=10)
         # Create More info button
        info_button = ttk.Button(
            child_window,
            text="Display Info",
            command=lambda: [display_package_info(package_name), child_window.destroy()]
        )
        info_button.pack(fill=tk.X, padx=20, pady=5)
        # Create Update button
        update_button = ttk.Button(
            child_window,
            text="Update",
            command=lambda: [self.update_package(package_name), child_window.destroy()]
        )
        update_button.pack(fill=tk.X, padx=20, pady=5)

        # Create Uninstall button
        uninstall_button = ttk.Button(
            child_window,
            text="Uninstall",
            command=lambda: [self.uninstall_package(package_name), child_window.destroy()]
        )
        uninstall_button.pack(fill=tk.X, padx=20, pady=5)

        # Create Cancel button
        cancel_button = ttk.Button(
            child_window,
            text="Cancel",
            command=child_window.destroy
        )
        cancel_button.pack(fill=tk.X, padx=20, pady=5)
     
        def display_package_info(package_name):
        
            try:
                result = subprocess.run([sys.executable, "-m", "pip", "show", package_name], capture_output=True, text=True)
                if result.returncode == 0:
                    child_window.lower()
                    messagebox.showinfo(f"Details of {package_name}",result.stdout)
                else:
                    messagebox.showerror("Error", f"Failed to retrieve info for {package_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Error fetching package info: {str(e)}")

    def update_package(self, package_name):
        self.status_var.set(f"Updating {package_name}...")
        
        def update():
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_name])
                self.status_var.set(f"Successfully updated {package_name}")
                self.load_packages()
            except subprocess.CalledProcessError as e:
                self.status_var.set(f"Error updating {package_name}: {str(e)}")
                messagebox.showerror("Error", f"Failed to update {package_name}")
        
        thread = threading.Thread(target=update)
        thread.daemon = True
        thread.start()
    
    def uninstall_package(self, package_name):
        if messagebox.askyesno("Confirm Uninstall",
                              f"Are you sure you want to uninstall {package_name}?"):
            self.status_var.set(f"Uninstalling {package_name}...")
            
            def uninstall():
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package_name])
                    self.status_var.set(f"Successfully uninstalled {package_name}")
                    self.load_packages()
                except subprocess.CalledProcessError as e:
                    self.status_var.set(f"Error uninstalling {package_name}: {str(e)}")
                    messagebox.showerror("Error", f"Failed to uninstall {package_name}")
            
            thread = threading.Thread(target=uninstall)
            thread.daemon = True
            thread.start()
    
    def search_pypi(self):
        query = self.search_var.get().strip()
        if not query:
            return
        
        self.status_var.set(f"Searching PyPI for {query}...")
        
        def search():
            try:
                response = requests.get(f"https://pypi.org/pypi/{query}/json")

                if response.status_code == 200:
                    data = response.json()
                    if messagebox.askyesno("Package Found",
                                         f"Would you like to install {query} {data['info']['version']}?\nAuthor: {data['info']['author']}"):
                        self.install_package(query)
                else:
                    messagebox.showinfo("Not Found", f"Package '{query}' not found on PyPI")
                    self.status_var.set("Ready")
            except Exception as e:
                self.status_var.set(f"Error searching PyPI: {str(e)}")
                messagebox.showerror("Error", f"Failed to search PyPI: {str(e)}")
        
        thread = threading.Thread(target=search)
        thread.daemon = True
        thread.start()
    
    def install_package(self, package_name):
        self.status_var.set(f"Installing {package_name}...")
        
        def install():
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                self.status_var.set(f"Successfully installed {package_name}")
                self.load_packages()
            except subprocess.CalledProcessError as e:
                self.status_var.set(f"Error installing {package_name}: {str(e)}")
                messagebox.showerror("Error", f"Failed to install {package_name}")
        
        thread = threading.Thread(target=install)
        thread.daemon = True
        thread.start()
    # Return Installation date of packages
    def get_installation_date(self,package_name):

        try:
            # Locate the package directory
            spec = find_spec(package_name)
            if not spec or not spec.origin:
                return "null"
            
            # Get the directory path of the package
            package_dir = os.path.dirname(spec.origin)
            
            # Get the modification time of the package directory
            timestamp = os.path.getmtime(package_dir)
            install_date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            return install_date
        except Exception as e:
            return f"Error retrieving installation date: {e}"


if __name__ == "__main__":
    root = tk.Tk()
    app = PipManagerApp(root)
    root.mainloop()