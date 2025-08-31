"""
Log Viewer and Analysis Tool for Business Dashboard
Helps developers and support staff analyze application logs for debugging
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import re


class LogViewer:
    """GUI tool for viewing and analyzing Business Dashboard logs"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Business Dashboard - Log Viewer & Analyzer")
        self.root.geometry("1200x800")
        
        # Log directory
        self.log_dir = Path("logs")
        
        # Current log data
        self.current_logs = []
        self.filtered_logs = []
        
        self.create_gui()
        self.load_available_logs()
    
    def create_gui(self):
        """Create the GUI interface"""
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Top controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Log file selection
        ttk.Label(controls_frame, text="Log File:").pack(side="left", padx=(0, 5))
        self.log_file_var = tk.StringVar()
        self.log_file_combo = ttk.Combobox(controls_frame, textvariable=self.log_file_var, width=30)
        self.log_file_combo.pack(side="left", padx=(0, 10))
        self.log_file_combo.bind("<<ComboboxSelected>>", self.on_log_file_selected)
        
        # Refresh button
        ttk.Button(controls_frame, text="Refresh", command=self.load_available_logs).pack(side="left", padx=(0, 10))
        
        # Filter controls
        ttk.Label(controls_frame, text="Filter:").pack(side="left", padx=(10, 5))
        self.filter_var = tk.StringVar()
        self.filter_var.trace("w", self.on_filter_changed)
        filter_entry = ttk.Entry(controls_frame, textvariable=self.filter_var, width=20)
        filter_entry.pack(side="left", padx=(0, 10))
        
        # Level filter
        ttk.Label(controls_frame, text="Level:").pack(side="left", padx=(10, 5))
        self.level_var = tk.StringVar(value="ALL")
        level_combo = ttk.Combobox(controls_frame, textvariable=self.level_var, 
                                  values=["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], width=10)
        level_combo.pack(side="left", padx=(0, 10))
        level_combo.bind("<<ComboboxSelected>>", self.on_filter_changed)
        
        # Clear filter button
        ttk.Button(controls_frame, text="Clear Filter", command=self.clear_filter).pack(side="left", padx=(10, 0))
        
        # Stats frame
        stats_frame = ttk.LabelFrame(main_frame, text="Log Statistics", padding=10)
        stats_frame.pack(fill="x", pady=(0, 10))
        
        self.stats_label = ttk.Label(stats_frame, text="No logs loaded")
        self.stats_label.pack(anchor="w")
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Raw log view
        self.create_raw_log_tab()
        
        # Structured log view (for JSON logs)
        self.create_structured_log_tab()
        
        # Error analysis tab
        self.create_error_analysis_tab()
        
        # Performance analysis tab
        self.create_performance_tab()
    
    def create_raw_log_tab(self):
        """Create raw log viewing tab"""
        raw_frame = ttk.Frame(self.notebook)
        self.notebook.add(raw_frame, text="Raw Logs")
        
        # Create text widget with scrollbar
        self.raw_text = scrolledtext.ScrolledText(raw_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.raw_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Context menu
        self.create_context_menu(self.raw_text)
    
    def create_structured_log_tab(self):
        """Create structured log viewing tab"""
        struct_frame = ttk.Frame(self.notebook)
        self.notebook.add(struct_frame, text="Structured View")
        
        # Create treeview for structured data
        columns = ("Timestamp", "Level", "Module", "Function", "Message")
        self.log_tree = ttk.Treeview(struct_frame, columns=columns, show="headings", height=15)
        
        # Define column headings and widths
        for col in columns:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(struct_frame, orient="vertical", command=self.log_tree.yview)
        h_scrollbar = ttk.Scrollbar(struct_frame, orient="horizontal", command=self.log_tree.xview)
        self.log_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack widgets
        self.log_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        struct_frame.grid_rowconfigure(0, weight=1)
        struct_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click to show details
        self.log_tree.bind("<Double-1>", self.show_log_details)
    
    def create_error_analysis_tab(self):
        """Create error analysis tab"""
        error_frame = ttk.Frame(self.notebook)
        self.notebook.add(error_frame, text="Error Analysis")
        
        # Error summary
        summary_frame = ttk.LabelFrame(error_frame, text="Error Summary", padding=10)
        summary_frame.pack(fill="x", padx=5, pady=5)
        
        self.error_summary_label = ttk.Label(summary_frame, text="No errors to analyze")
        self.error_summary_label.pack(anchor="w")
        
        # Error details
        details_frame = ttk.LabelFrame(error_frame, text="Error Details", padding=10)
        details_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.error_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.error_text.pack(fill="both", expand=True)
    
    def create_performance_tab(self):
        """Create performance analysis tab"""
        perf_frame = ttk.Frame(self.notebook)
        self.notebook.add(perf_frame, text="Performance")
        
        # Performance summary
        summary_frame = ttk.LabelFrame(perf_frame, text="Performance Summary", padding=10)
        summary_frame.pack(fill="x", padx=5, pady=5)
        
        self.perf_summary_label = ttk.Label(summary_frame, text="No performance data to analyze")
        self.perf_summary_label.pack(anchor="w")
        
        # Slow operations
        slow_frame = ttk.LabelFrame(perf_frame, text="Slow Operations (>1000ms)", padding=10)
        slow_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.slow_ops_text = scrolledtext.ScrolledText(slow_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.slow_ops_text.pack(fill="both", expand=True)
    
    def create_context_menu(self, text_widget):
        """Create context menu for text widgets"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Copy", command=lambda: text_widget.event_generate("<<Copy>>"))
        context_menu.add_command(label="Select All", command=lambda: text_widget.tag_add("sel", "1.0", "end"))
        context_menu.add_separator()
        context_menu.add_command(label="Save Selection", command=lambda: self.save_selection(text_widget))
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        text_widget.bind("<Button-3>", show_context_menu)
    
    def load_available_logs(self):
        """Load list of available log files"""
        if not self.log_dir.exists():
            self.log_file_combo['values'] = ["No log directory found"]
            return
        
        log_files = []
        for file_path in self.log_dir.glob("*.log*"):
            if file_path.is_file():
                # Add file with size and modification date
                size = file_path.stat().st_size
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                log_files.append(f"{file_path.name} ({size} bytes, {mod_time.strftime('%Y-%m-%d %H:%M')})")
        
        if not log_files:
            log_files = ["No log files found"]
        
        self.log_file_combo['values'] = log_files
        if log_files and "No log files" not in log_files[0]:
            self.log_file_combo.current(0)
            self.on_log_file_selected()
    
    def on_log_file_selected(self, event=None):
        """Handle log file selection"""
        selected = self.log_file_var.get()
        if not selected or "No log" in selected:
            return
        
        # Extract filename from the display string
        filename = selected.split(" (")[0]
        file_path = self.log_dir / filename
        
        if not file_path.exists():
            messagebox.showerror("Error", f"Log file not found: {filename}")
            return
        
        try:
            self.load_log_file(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load log file: {str(e)}")
    
    def load_log_file(self, file_path):
        """Load and parse log file"""
        self.current_logs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse as JSON logs first
            if self.try_parse_json_logs(content):
                pass  # JSON parsing successful
            else:
                # Parse as regular text logs
                self.parse_text_logs(content)
            
            self.filtered_logs = self.current_logs.copy()
            self.update_displays()
            self.analyze_logs()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read log file: {str(e)}")
    
    def try_parse_json_logs(self, content):
        """Try to parse logs as JSON format"""
        try:
            lines = content.strip().split('\n')
            json_logs = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        log_entry = json.loads(line)
                        json_logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
            
            if json_logs:
                self.current_logs = json_logs
                return True
            return False
            
        except Exception:
            return False
    
    def parse_text_logs(self, content):
        """Parse regular text logs"""
        lines = content.split('\n')
        
        # Pattern for log lines: timestamp | level | module | function:line | message
        log_pattern = re.compile(r'^([\d-]+\s+[\d:]+)\s*\|\s*(\w+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*(.+)$')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            match = log_pattern.match(line)
            if match:
                timestamp, level, module, function, message = match.groups()
                self.current_logs.append({
                    'timestamp': timestamp.strip(),
                    'level': level.strip(),
                    'module': module.strip(),
                    'function': function.strip(),
                    'message': message.strip(),
                    'raw_line': line
                })
            else:
                # Add as raw entry if doesn't match pattern
                self.current_logs.append({
                    'timestamp': '',
                    'level': 'UNKNOWN',
                    'module': '',
                    'function': '',
                    'message': line,
                    'raw_line': line
                })
    
    def on_filter_changed(self, *args):
        """Handle filter changes"""
        self.apply_filters()
        self.update_displays()
    
    def apply_filters(self):
        """Apply current filters to logs"""
        filter_text = self.filter_var.get().lower()
        level_filter = self.level_var.get()
        
        self.filtered_logs = []
        
        for log_entry in self.current_logs:
            # Level filter
            if level_filter != "ALL" and log_entry.get('level', '').upper() != level_filter:
                continue
            
            # Text filter
            if filter_text:
                searchable_text = (
                    log_entry.get('message', '') + ' ' +
                    log_entry.get('module', '') + ' ' +
                    log_entry.get('function', '')
                ).lower()
                
                if filter_text not in searchable_text:
                    continue
            
            self.filtered_logs.append(log_entry)
    
    def clear_filter(self):
        """Clear all filters"""
        self.filter_var.set("")
        self.level_var.set("ALL")
        self.filtered_logs = self.current_logs.copy()
        self.update_displays()
    
    def update_displays(self):
        """Update all display widgets"""
        self.update_raw_display()
        self.update_structured_display()
        self.update_stats()
    
    def update_raw_display(self):
        """Update raw log display"""
        self.raw_text.delete(1.0, tk.END)
        
        for log_entry in self.filtered_logs:
            raw_line = log_entry.get('raw_line', str(log_entry))
            self.raw_text.insert(tk.END, raw_line + '\n')
        
        # Color-code by level
        self.colorize_logs()
    
    def update_structured_display(self):
        """Update structured log display"""
        # Clear existing items
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        
        # Add filtered logs
        for log_entry in self.filtered_logs:
            values = (
                log_entry.get('timestamp', ''),
                log_entry.get('level', ''),
                log_entry.get('module', ''),
                log_entry.get('function', ''),
                log_entry.get('message', '')[:100] + ('...' if len(log_entry.get('message', '')) > 100 else '')
            )
            self.log_tree.insert('', 'end', values=values)
    
    def update_stats(self):
        """Update statistics display"""
        total_logs = len(self.current_logs)
        filtered_logs = len(self.filtered_logs)
        
        if total_logs == 0:
            self.stats_label.config(text="No logs loaded")
            return
        
        # Count by level
        level_counts = {}
        for log_entry in self.filtered_logs:
            level = log_entry.get('level', 'UNKNOWN')
            level_counts[level] = level_counts.get(level, 0) + 1
        
        stats_text = f"Total: {total_logs} | Filtered: {filtered_logs} | "
        stats_text += " | ".join([f"{level}: {count}" for level, count in level_counts.items()])
        
        self.stats_label.config(text=stats_text)
    
    def colorize_logs(self):
        """Add color coding to raw log display"""
        # Define colors for different log levels
        colors = {
            'ERROR': 'red',
            'CRITICAL': 'red',
            'WARNING': 'orange',
            'INFO': 'blue',
            'DEBUG': 'gray'
        }
        
        # Configure tags
        for level, color in colors.items():
            self.raw_text.tag_config(level, foreground=color)
        
        # Apply tags
        content = self.raw_text.get(1.0, tk.END)
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            for level, color in colors.items():
                if f'| {level} |' in line:
                    start = f"{i+1}.0"
                    end = f"{i+1}.end"
                    self.raw_text.tag_add(level, start, end)
                    break
    
    def analyze_logs(self):
        """Analyze logs for errors and performance issues"""
        self.analyze_errors()
        self.analyze_performance()
    
    def analyze_errors(self):
        """Analyze errors in logs"""
        errors = [log for log in self.current_logs if log.get('level') in ['ERROR', 'CRITICAL']]
        
        if not errors:
            self.error_summary_label.config(text="No errors found")
            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(tk.END, "No errors to display")
            return
        
        # Group errors by type
        error_types = {}
        for error in errors:
            error_msg = error.get('message', '')
            # Simple error grouping by first few words
            error_type = ' '.join(error_msg.split()[:3]) if error_msg else 'Unknown'
            if error_type not in error_types:
                error_types[error_type] = []
            error_types[error_type].append(error)
        
        # Update summary
        summary = f"Total Errors: {len(errors)} | Unique Types: {len(error_types)}"
        self.error_summary_label.config(text=summary)
        
        # Update details
        self.error_text.delete(1.0, tk.END)
        for error_type, error_list in error_types.items():
            self.error_text.insert(tk.END, f"\\n=== {error_type} ({len(error_list)} occurrences) ===\\n")
            for error in error_list[:5]:  # Show first 5 of each type
                self.error_text.insert(tk.END, f"{error.get('timestamp', '')} | {error.get('message', '')}\\n")
            if len(error_list) > 5:
                self.error_text.insert(tk.END, f"... and {len(error_list) - 5} more\\n")
            self.error_text.insert(tk.END, "\\n")
    
    def analyze_performance(self):
        """Analyze performance metrics in logs"""
        # Look for performance-related logs
        perf_logs = []
        slow_ops = []
        
        for log in self.current_logs:
            message = log.get('message', '')
            if 'ms' in message or 'duration' in message.lower():
                perf_logs.append(log)
                
                # Extract duration if possible
                duration_match = re.search(r'(\\d+(?:\\.\\d+)?)\\s*ms', message)
                if duration_match:
                    duration = float(duration_match.group(1))
                    if duration > 1000:  # Slow operation > 1 second
                        slow_ops.append((log, duration))
        
        if not perf_logs:
            self.perf_summary_label.config(text="No performance data found")
            self.slow_ops_text.delete(1.0, tk.END)
            self.slow_ops_text.insert(tk.END, "No performance data to display")
            return
        
        # Update summary
        summary = f"Performance Logs: {len(perf_logs)} | Slow Operations: {len(slow_ops)}"
        self.perf_summary_label.config(text=summary)
        
        # Update slow operations
        self.slow_ops_text.delete(1.0, tk.END)
        if slow_ops:
            slow_ops.sort(key=lambda x: x[1], reverse=True)  # Sort by duration
            for log, duration in slow_ops:
                self.slow_ops_text.insert(tk.END, 
                    f"{log.get('timestamp', '')} | {duration:.2f}ms | {log.get('message', '')}\\n")
        else:
            self.slow_ops_text.insert(tk.END, "No slow operations detected")
    
    def show_log_details(self, event):
        """Show detailed view of selected log entry"""
        selection = self.log_tree.selection()
        if not selection:
            return
        
        item = self.log_tree.item(selection[0])
        index = self.log_tree.index(selection[0])
        
        if index < len(self.filtered_logs):
            log_entry = self.filtered_logs[index]
            self.show_detail_window(log_entry)
    
    def show_detail_window(self, log_entry):
        """Show detailed log entry in new window"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Log Entry Details")
        detail_window.geometry("600x400")
        
        # Create text widget
        text_widget = scrolledtext.ScrolledText(detail_window, wrap=tk.WORD, font=("Consolas", 10))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Display formatted log entry
        if isinstance(log_entry, dict):
            formatted_json = json.dumps(log_entry, indent=2, default=str)
            text_widget.insert(tk.END, formatted_json)
        else:
            text_widget.insert(tk.END, str(log_entry))
        
        text_widget.config(state="disabled")
    
    def save_selection(self, text_widget):
        """Save selected text to file"""
        try:
            selection = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            if not selection:
                messagebox.showwarning("Warning", "No text selected")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(selection)
                messagebox.showinfo("Success", f"Selection saved to {filename}")
                
        except tk.TclError:
            messagebox.showwarning("Warning", "No text selected")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def run(self):
        """Start the log viewer"""
        self.root.mainloop()


def main():
    """Main entry point"""
    viewer = LogViewer()
    viewer.run()


if __name__ == "__main__":
    main()
