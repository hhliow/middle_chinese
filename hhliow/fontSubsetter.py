import json
import subprocess
import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading

class FontSubsetTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Font Subset Tool")
        self.root.geometry("600x500")
        
        # Variables
        self.font_path = tk.StringVar()
        self.json_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.characters = set()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Font Subset Tool", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Font file selection
        ttk.Label(main_frame, text="Font File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.font_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="Browse", command=self.select_font_file).grid(row=1, column=2, pady=5)
        
        # Text file selection
        ttk.Label(main_frame, text="Text File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.json_path, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="Browse", command=self.select_text_file).grid(row=2, column=2, pady=5)
        
        # Output file selection
        ttk.Label(main_frame, text="Output File:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_path, width=50).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="Browse", command=self.select_output_file).grid(row=3, column=2, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(20, 10))
        
        self.remove_kerning = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Remove kerning (smaller file size)", 
                       variable=self.remove_kerning).grid(row=0, column=0, sticky=tk.W)
        
        self.remove_hinting = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Remove hinting (smaller file size)", 
                       variable=self.remove_hinting).grid(row=1, column=0, sticky=tk.W)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(buttons_frame, text="Preview Characters", command=self.preview_characters).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Create Subset Font", command=self.create_subset).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Install fonttools", command=self.install_fonttools).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Log text area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.log("Font Subset Tool loaded. Select your files to get started.")
    
    def log(self, message):
        """Add message to log area"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def select_font_file(self):
        """Select font file"""
        filename = filedialog.askopenfilename(
            title="Select Font File",
            filetypes=[
                ("Font files", "*.ttf *.ttc *.otf"),
                ("TrueType Font", "*.ttf"),
                ("TrueType Collection", "*.ttc"),
                ("OpenType Font", "*.otf"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.font_path.set(filename)
            self.log(f"Selected font: {os.path.basename(filename)}")
            
            # Auto-suggest output filename
            if not self.output_path.get():
                path = Path(filename)
                suggested_output = path.parent / f"{path.stem}_subset{path.suffix}"
                self.output_path.set(str(suggested_output))
    
    def select_text_file(self):
        """Select text file"""
        filename = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[
                ("Text files", "*.txt *.json *.csv *.xml *.html *.md"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.json_path.set(filename)
            self.log(f"Selected text file: {os.path.basename(filename)}")
    
    def select_output_file(self):
        """Select output file"""
        filename = filedialog.asksaveasfilename(
            title="Save Subset Font As",
            defaultextension=".ttf",
            filetypes=[
                ("TrueType Font", "*.ttf"),
                ("OpenType Font", "*.otf"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.output_path.set(filename)
            self.log(f"Output will be saved as: {os.path.basename(filename)}")
    
    def extract_text_from_file(self, file_path):
        """Extract all unique characters from any text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.log(f"Successfully loaded text file")
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                self.log(f"Successfully loaded text file (latin-1 encoding)")
            except Exception as e:
                self.log(f"Error reading file: {e}")
                return set()
        except Exception as e:
            self.log(f"Error reading file: {e}")
            return set()
        
        # Extract all unique characters
        all_chars = set(content)
        ascii_chars = set(chr(i) for i in range(1, 128))
        self.log(f"Found {len(all_chars)} unique characters")
        return all_chars | ascii_chars
    
    def preview_characters(self):
        """Preview characters that will be included"""
        if not self.json_path.get():
            messagebox.showerror("Error", "Please select a text file first")
            return
        
        self.characters = self.extract_text_from_file(self.json_path.get())
        
        if not self.characters:
            messagebox.showwarning("Warning", "No characters found in text file")
            return
        
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Character Preview")
        preview_window.geometry("500x400")
        
        # Character display
        ttk.Label(preview_window, text=f"Found {len(self.characters)} unique characters:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Text area with characters
        char_frame = ttk.Frame(preview_window)
        char_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        char_text = tk.Text(char_frame, wrap=tk.WORD, font=("Arial", 14))
        char_scrollbar = ttk.Scrollbar(char_frame, orient=tk.VERTICAL, command=char_text.yview)
        char_text.configure(yscrollcommand=char_scrollbar.set)
        
        char_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        char_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert characters (sorted for better readability)
        sorted_chars = sorted(self.characters)
        char_text.insert(tk.END, ''.join(sorted_chars))
        char_text.config(state=tk.DISABLED)
        
        # Sample text
        sample_frame = ttk.LabelFrame(preview_window, text="Sample Text", padding="10")
        sample_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        sample_chars = sorted_chars[:50]  # First 50 characters
        sample_text = ''.join(sample_chars)
        ttk.Label(sample_frame, text=sample_text, font=("Arial", 16)).pack()
        
        ttk.Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=10)
    
    def install_fonttools(self):
        """Install fonttools package"""
        def install():
            self.progress.start()
            self.log("Installing fonttools...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "fonttools"])
                self.log("fonttools installed successfully")
                messagebox.showinfo("Success", "fonttools installed successfully!")
            except subprocess.CalledProcessError as e:
                self.log(f"Error installing fonttools: {e}")
                messagebox.showerror("Error", f"Failed to install fonttools: {e}")
            except Exception as e:
                self.log(f"Unexpected error: {e}")
                messagebox.showerror("Error", f"Unexpected error: {e}")
            finally:
                self.progress.stop()
        
        # Run in thread to prevent GUI freezing
        threading.Thread(target=install, daemon=True).start()
    
    def create_subset(self):
        """Create subset font"""
        # Validate inputs
        if not self.font_path.get():
            messagebox.showerror("Error", "Please select a font file")
            return
        
        if not self.json_path.get():
            messagebox.showerror("Error", "Please select a JSON file")
            return
        
        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify an output file")
            return
        
        if not os.path.exists(self.font_path.get()):
            messagebox.showerror("Error", "Font file does not exist")
            return
        
        if not os.path.exists(self.json_path.get()):
            messagebox.showerror("Error", "JSON file does not exist")
            return
        
        def subset():
            self.progress.start()
            try:
                # Extract characters if not already done
                if not self.characters:
                    self.characters = self.extract_text_from_file(self.json_path.get())
                
                if not self.characters:
                    messagebox.showerror("Error", "No characters found in text file")
                    return
                
                # Build pyftsubset command
                char_string = ''.join(sorted(self.characters))
                cmd = [
                    sys.executable, '-m', 'fontTools.subset',
                    self.font_path.get(),
                    f'--text={char_string}',
                    f'--output-file={self.output_path.get()}'
                ]
                
                # Add optional parameters
                if self.remove_kerning.get():
                    cmd.append('--layout-features-=kern')
                
                if self.remove_hinting.get():
                    cmd.append('--no-hinting')
                
                cmd.append('--glyph-names')  # Keep glyph names for debugging
                
                self.log(f"Running fontTools.subset with {len(self.characters)} characters...")
                self.log(f"Command: python -m fontTools.subset [font] [options]")
                
                # Run the command
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    # Success - show file size comparison
                    original_size = os.path.getsize(self.font_path.get())
                    subset_size = os.path.getsize(self.output_path.get())
                    reduction = ((original_size - subset_size) / original_size) * 100
                    
                    self.log("Subset font created successfully!")
                    self.log(f"  Original: {original_size:,} bytes ({original_size/1024/1024:.1f} MB)")
                    self.log(f"  Subset:   {subset_size:,} bytes ({subset_size/1024:.1f} KB)")
                    self.log(f"  Reduction: {reduction:.1f}%")
                    
                    messagebox.showinfo("Success", 
                                      f"Subset font created successfully!\n\n"
                                      f"Original: {original_size/1024/1024:.1f} MB\n"
                                      f"Subset: {subset_size/1024:.1f} KB\n"
                                      f"Reduction: {reduction:.1f}%")
                else:
                    error_msg = result.stderr or "Unknown error"
                    self.log(f"Error creating subset: {error_msg}")
                    
                    if "not found" in error_msg.lower() or "command not found" in error_msg.lower() or "No module named" in error_msg:
                        messagebox.showerror("Error", 
                                           "fonttools not found!\n\n"
                                           "Please install fonttools first by clicking the 'Install fonttools' button.")
                    else:
                        messagebox.showerror("Error", f"Failed to create subset font:\n\n{error_msg}")
                        
            except subprocess.TimeoutExpired:
                self.log("Operation timed out (large font or many characters)")
                messagebox.showerror("Error", "Operation timed out. The font might be too large or have too many characters.")
            except FileNotFoundError:
                self.log("fonttools not installed or not accessible")
                messagebox.showerror("Error", "fonttools not found!\n\nPlease install fonttools first.")
            except Exception as e:
                self.log(f"Unexpected error: {e}")
                messagebox.showerror("Error", f"Unexpected error:\n\n{e}")
            finally:
                self.progress.stop()
        
        # Run in thread to prevent GUI freezing
        threading.Thread(target=subset, daemon=True).start()

def main():
    root = tk.Tk()
    app = FontSubsetTool(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
