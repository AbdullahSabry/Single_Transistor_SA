import tkinter as tk
from tkinter import ttk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from OPS import DF_OPS

def format_with_units(value):
    """Format a number with appropriate SI units and one decimal place."""
    units = ["T", "G", "M", "k", "", "m", "u", "n", "p", "f"]
    scales = [1e12, 1e9, 1e6, 1e3, 1, 1e-3, 1e-6, 1e-9, 1e-12, 1e-15]
    
    for unit, scale in zip(units, scales):
        if abs(value) >= scale or unit == "f":
            return f"{value / scale:.2f}{unit}"
    return str(round(value, 2))  # Fallback to rounding to one decimal place if not within any scale

def format_tick_si(value, tick_number):
    """Formatter function to format tick labels with SI units."""
    return format_with_units(value)

def format_row(row):
    """Format a DataFrame row with appropriate SI units and one decimal place."""
    formatted_row = {col: format_with_units(val) if isinstance(val, (int, float)) else val for col, val in row.items()}
    formatted_str = "\n".join(f"{key: <20}{value}" for key, value in formatted_row.items())
    return formatted_str

def plot_with_conditions(df, axes, condition_column, fig, ax, true_color='green', false_color='red', plot_only_true=False,
                         false_size=0.1, true_size=10, hue_variable=None, colormap='viridis',
                         hue_threshold=None, hue_threshold_direction='down', text_widget=None):
    """
    Plot data points based on given conditions and update the text widget with DataFrame row information upon clicking.
    """
    x_axis, y_axis = axes

    # Check if the necessary columns exist in the DataFrame
    if condition_column not in df.columns:
        raise ValueError(f"Condition column '{condition_column}' does not exist in the DataFrame")
    if hue_variable and hue_variable not in df.columns:
        raise ValueError(f"Hue variable column '{hue_variable}' does not exist in the DataFrame")
    
    # Apply filtering if plot_only_true is True
    if plot_only_true:
        df = df[df[condition_column] == True]
    
    # Apply hue threshold filtering
    if hue_variable and hue_threshold is not None:
        hue_min, hue_max = df[hue_variable].min(), df[hue_variable].max()
        threshold_value = hue_min + hue_threshold / 100.0 * (hue_max - hue_min)
        if hue_threshold_direction == 'down':
            df = df[df[hue_variable] >= threshold_value]
        elif hue_threshold_direction == 'up':
            df = df[df[hue_variable] <= threshold_value]

    # Determine colors and sizes based on the condition column
    sizes = df[condition_column].map({True: true_size, False: false_size})
    
    # If hue_variable is provided, use it to determine colors
    if hue_variable:
        norm = plt.Normalize(df[hue_variable].min(), df[hue_variable].max())
        cmap = plt.get_cmap(colormap)
        colors = cmap(norm(df[hue_variable]))
    else:
        colors = df[condition_column].map({True: true_color, False: false_color})
    
    # Clear the current figure
    fig.clf()

    # Create a new axis
    ax = fig.add_subplot(111)

    # Create the plot
    scatter = ax.scatter(df[x_axis], df[y_axis], c=colors, s=sizes, cmap=colormap, norm=norm)

    # Add colorbar if hue_variable is used
    if hue_variable:
        if hasattr(ax, 'colorbar') and ax.colorbar:
            ax.colorbar.remove()
        fig.colorbar = plt.colorbar(plt.cm.ScalarMappable(norm, cmap=colormap), ax=ax)
        fig.colorbar.set_label(hue_variable)
    
    # Format the tick labels with SI units and one decimal place
    ax.xaxis.set_major_formatter(FuncFormatter(format_tick_si))
    ax.yaxis.set_major_formatter(FuncFormatter(format_tick_si))
    
    # Function to display the corresponding DataFrame row and highlight the clicked point
    def onpick(event):
        ind = event.ind[0]  # Get the index of the picked point
        selected_row = df.iloc[ind]  # Get the corresponding row from the DataFrame
        formatted_row = format_row(selected_row)  # Format the row for readable output
        
        # Display the row information in the text widget
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)  # Clear previous text
        text_widget.insert(tk.END, formatted_row)
        text_widget.config(state=tk.DISABLED)
        
        # Highlight the selected point by increasing its size and changing its color
        ax.collections[0].set_sizes([true_size*10 if i == ind else size for i, size in enumerate(sizes)])
        ax.collections[0].set_edgecolor(['yellow' if i == ind else 'none' for i in range(len(sizes))])
        
        fig.canvas.draw()
    
    # Connect the pick event
    fig.canvas.mpl_connect('pick_event', onpick)
    
    # Set the picker property
    scatter.set_picker(True)
    
    # Labels and title
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.set_title(f'{x_axis} vs {y_axis}')
    
    fig.tight_layout()
    fig.canvas.draw()

# Define the UI
class DataPlotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Data Plotter")
        self.geometry("1200x800")
        
        # Initialize with an empty DataFrame
        self.df = pd.DataFrame()
        self.df_obj = None
        
        # Input frame for user inputs
        input_frame = ttk.Frame(self)
        input_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        self.conditions = []
        
        # Add input fields for conditions
        self.conditions_label = ttk.Label(input_frame, text="Conditions:")
        self.conditions_label.pack(anchor=tk.W)
        
        self.conditions_frame = ttk.Frame(input_frame)
        self.conditions_frame.pack(fill=tk.X)
        
        self.add_condition_button = ttk.Button(input_frame, text="Add Condition", command=self.add_condition)
        self.add_condition_button.pack(anchor=tk.W)
        
        # Add input fields for other variables
    
        self.x_axis_label = ttk.Label(input_frame, text="X-axis:")
        self.x_axis_label.pack(anchor=tk.W)
        self.x_axis_combobox = ttk.Combobox(input_frame, values=list(self.df.columns))
        self.x_axis_combobox.pack(fill=tk.X)

        
        self.y_axis_label = ttk.Label(input_frame, text="Y-axis:")
        self.y_axis_label.pack(anchor=tk.W)
        self.y_axis_combobox = ttk.Combobox(input_frame, values=list(self.df.columns))
        self.y_axis_combobox.pack(fill=tk.X)
        
        self.plot_only_true_label = ttk.Label(input_frame, text="Plot only true:")
        self.plot_only_true_label.pack(anchor=tk.W)
        self.plot_only_true_combobox = ttk.Combobox(input_frame, values=[True, False])
        self.plot_only_true_combobox.current(0)  # Set default value to True
        self.plot_only_true_combobox.pack(fill=tk.X)
        
        self.hue_variable_label = ttk.Label(input_frame, text="Hue variable:")
        self.hue_variable_label.pack(anchor=tk.W)
        self.hue_variable_combobox = ttk.Combobox(input_frame, values=list(self.df.columns))
        self.hue_variable_combobox.pack(fill=tk.X)
        
        self.colormap_label = ttk.Label(input_frame, text="Colormap:")
        self.colormap_label.pack(anchor=tk.W)
        self.colormap_combobox = ttk.Combobox(input_frame, values=plt.colormaps())
        self.colormap_combobox.set('viridis')
        self.colormap_combobox.pack(fill=tk.X)
        
        self.hue_threshold_label = ttk.Label(input_frame, text="Hue threshold:")
        self.hue_threshold_label.pack(anchor=tk.W)
        self.hue_threshold_entry = ttk.Entry(input_frame)
        self.hue_threshold_entry.insert(0, "0")
        self.hue_threshold_entry.pack(fill=tk.X)
        
        self.threshold_exclusion_label = ttk.Label(input_frame, text="Threshold exclusion:")
        self.threshold_exclusion_label.pack(anchor=tk.W)
        self.threshold_exclusion_combobox = ttk.Combobox(input_frame, values=['down', 'up'])
        self.threshold_exclusion_combobox.set('down')
        self.threshold_exclusion_combobox.pack(fill=tk.X)

        self.WoverLmin_label = ttk.Label(input_frame, text="W/L min:")
        self.WoverLmin_label.pack(anchor=tk.W)
        self.WoverLmin_entry = ttk.Entry(input_frame)
        self.WoverLmin_entry.insert(0, "0.5")
        self.WoverLmin_entry.pack(fill=tk.X)

        self.Wmax_label = ttk.Label(input_frame, text="Max width:")
        self.Wmax_label.pack(anchor=tk.W)
        self.Wmax_entry = ttk.Entry(input_frame)
        self.Wmax_entry.insert(0, "100e-6")
        self.Wmax_entry.pack(fill=tk.X)
        
        self.plot_button = ttk.Button(input_frame, text="Plot", command=self.plot_data)
        self.plot_button.pack(anchor=tk.W)
        self.plot_button.config(state=tk.DISABLED)  # Disable until DataFrame is loaded
        
        
        
        # Frame for the plot
        self.colorbar = None
        self.plot_frame = ttk.Frame(self, width=50, height=50)
        self.plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.figure = plt.Figure()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Text widget for displaying DataFrame row information
        self.text_widget = tk.Text(self, wrap=tk.WORD, height=20, width=30, state=tk.DISABLED)
        self.text_widget.pack(fill=tk.X)
        
        # Entry for DataFrame path
        self.df_path_label = ttk.Label(input_frame, text="DataFrame path:")
        self.df_path_label.pack(anchor=tk.W)
        self.df_path_entry = ttk.Entry(input_frame)
        self.df_path_entry.insert(0, "900kPoints.csv")
        self.df_path_entry.pack(fill=tk.X)


        self.load_button = ttk.Button(input_frame, text="Load DataFrame", command=self.load_dataframe)
        self.load_button.pack(anchor=tk.W)
        
    def add_condition(self):
        condition_frame = ttk.Frame(self.conditions_frame)
        condition_frame.pack(fill=tk.X, pady=2)
        
        variable_combobox = ttk.Combobox(condition_frame, values=list(self.df.columns), width=5, justify='center')
        variable_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        operation_combobox = ttk.Combobox(condition_frame, values=['=', '>', '<'], width=3, justify='center')
        operation_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        value_entry = ttk.Entry(condition_frame, width=5)
        value_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        remove_button = ttk.Button(condition_frame, text="X", command=lambda: self.remove_condition(condition_frame))
        remove_button.pack(side=tk.LEFT)
        
        self.conditions.append((variable_combobox, operation_combobox, value_entry, condition_frame))
    
    def remove_condition(self, condition_frame):
        # Remove the condition from the conditions list
        for condition in self.conditions:
            if condition[3] == condition_frame:
                self.conditions.remove(condition)
                condition_frame.destroy()
                break
    
    def load_dataframe(self):
        df_path = self.df_path_entry.get()
        self.df = pd.read_csv(df_path)
        self.df_obj = DF_OPS.DF_OPS(self.df)
        # Clear the conditions list and UI
        for condition in self.conditions:
            condition[3].destroy()
        self.conditions.clear()
        
        # Reinitialize the conditions frame
        self.conditions_frame.destroy()
        self.conditions_frame = ttk.Frame(self)
        self.conditions_frame.pack(fill=tk.X)
        
        # Update hue_variable_combobox with new DataFrame columns
        self.hue_variable_combobox['values'] = list(self.df_obj.mod_df.columns)
        self.x_axis_combobox['values'] = list(self.df_obj.mod_df.columns)
        self.y_axis_combobox['values'] = list(self.df_obj.mod_df.columns)

        # Enable plot button once DataFrame is loaded
        self.plot_button.config(state=tk.NORMAL)
        
    def plot_data(self):
        # Gather input data
        conditions = [
            f"{combobox[0].get()} {combobox[1].get()} {combobox[2].get()}"
            for combobox in self.conditions
        ] if self.conditions else [
        'rout > 40e3',
        'region = 2',
        'VSB > 0.2',
        'VSB < 0.4',
        'gm > 1.44e-3',
        'VDS < 1'
    ]
        x_axis = self.x_axis_combobox.get() if self.x_axis_combobox.get() else 'area'
        y_axis = self.y_axis_combobox.get() if self.y_axis_combobox.get() else 'id'
        plot_only_true = self.plot_only_true_combobox.get() == 'True'
        hue_variable = self.hue_variable_combobox.get() if self.hue_variable_combobox.get() else None
        colormap = self.colormap_combobox.get() if self.colormap_combobox.get() else None
        hue_threshold = float(self.hue_threshold_entry.get()) if self.hue_threshold_entry.get() else None
        WoverL_min = float(self.WoverLmin_entry.get()) if self.WoverLmin_entry.get() else None
        Wmax = float(self.Wmax_entry.get()) if self.Wmax_entry.get() else None
        threshold_exclusion = self.threshold_exclusion_combobox.get() if self.threshold_exclusion_combobox.get() else None
        
        # Initialize or update the DF_OPS object
        if not self.df_obj:
            self.df_obj = DF_OPS.DF_OPS(self.df)
        
        self.df_obj.compute_conditional_df(conditions=conditions, tolerance_percent=1, WoverL_min=WoverL_min, Wmax=Wmax)
        
        # Clear the previous plot and colorbar
        self.figure.clf()
        self.ax = self.figure.add_subplot(111)
        
        # Plot the new data
        plot_with_conditions(self.df_obj.conditional_df, [x_axis, y_axis], 'met_specs', self.figure, self.ax,
                             plot_only_true=plot_only_true,
                             hue_variable=hue_variable, colormap=colormap,
                             hue_threshold=hue_threshold, hue_threshold_direction=threshold_exclusion,
                             text_widget=self.text_widget)
        self.canvas.draw()

# Run the application
if __name__ == "__main__":
    app = DataPlotApp()
    app.mainloop()