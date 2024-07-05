# Transistor Sizing Assistant
This project is a powerful tool for IC designers to efficiently size transistors based on specific operating conditions and performance requirements. It consists of two main phases: LUT (Look-Up Table) generation and data visualization.
## Key Features

### Interactive GUI for easy transistor sizing
* Support for complex conditional queries
* Dynamic plotting with customizable axes and color mapping
* Real-time display of operating points
* Handles large datasets (demonstrated with 900k points)

### Project Structure

#### 1. LUT Generation (not included in this repo)

* Python script interfacing with Spectre simulator
Generates comprehensive transistor operating point data


#### 2. Data Visualization (included in this repo)

* Interactive GUI for data exploration and transistor sizing
Built with Tkinter, Matplotlib, and Pandas



### How to Use

1. Load the DataFrame (e.g., "900kPoints.csv")
2. Add conditions using the sliding bars (e.g., VSB > 0.2, VSB < 0.4)
3. Configure graph settings (X-axis, Y-axis, hue variable, etc.)
4. Click "Plot" to visualize the data
5. Click on any point to display its full operating point information

### Demo Highlight
The included demo showcases sizing the input NMOS pair of a 5T OTA:

* Conditions set: 0.2 < VSB < 0.4 (accounting for body effect), requirements for transistor parameteres (gm, rout)
* Plot: VGS vs. area, with drain current (id) as the hue variable
* Goal: Find the point with lowest VGS and area while maintaining reasonable power consumption
* Dataset: 900,000 operating points

![Demo](https://github.com/AbdullahSabry/Single_Transistor_SA/assets/87365208/b6bda437-f4e7-4421-ae68-87e631ceb3a4)

This demo illustrates the power of the tool in quickly identifying optimal transistor sizes that meet multiple criteria simultaneously.
### Code Structure

`main_app.py`: Contains the main GUI application logic
`DF_OPS.py`: Handles dataframe operations and condition parsing

### Getting Started

1. Clone this repository
2. Install required dependencies (Tkinter, Pandas, Matplotlib)
3. Run main_app.py to launch the application
4. Load your transistor operating point data and start exploring!

Note: The LUT generation phase is not included in this repository for security reasons. Users should generate their own LUT data using appropriate simulation tools before using this visualization application.
