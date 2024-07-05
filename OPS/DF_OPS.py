import pandas as pd
import math
import re

def parse_condition(condition):
    """Parse a condition string into its components."""
    pattern = r'(\S+)\s*(=|<|>)\s*(\S+)'
    match = re.match(pattern, condition)
    
    if match:
        return match.groups()  # returns a tuple (lhs, operator, rhs)
    else:
        raise ValueError(f"Invalid condition format: {condition}")
    
def parse_from_number(formatted_value):
    """Parse a formatted number with SI units back to a unitless number."""
    
    units = {"T": 1e12, "G": 1e9, "M": 1e6, "k": 1e3, "": 1, "m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12, "f": 1e-15}
    
    # Regular expression to match the number and the optional unit
    match = re.match(r"([-+]?\d*\.?\d+)([TGMkmunpf]?)", formatted_value)
    
    if not match:
        raise ValueError("Invalid formatted value")
    
    number = float(match.group(1))
    unit = match.group(2)
    
    if unit not in units:
        raise ValueError("Invalid unit in formatted value")
    
    return number * units[unit]


class DF_OPS:
    def __init__(self, df):
        self.df = df

        self.df['W'] = self.df['W'].apply(parse_from_number) # To be removed after correcting the LUT generation
        self.specs = ['intrinsic_gain', 'ft', 'area', 'gmoverid']
        self.mod_df = self.add_specs_df()
    
        self.conditional_df = 0

        self.proportional = ['cgg', 'gm', 'gmb', 'id']
        self.inversly = ['rout']


    def add_specs_df(self):
        mod_df = self.df.copy()
        for spec in self.specs:
            if spec == 'intrinsic_gain':
                mod_df['intrinsic_gain'] = mod_df['gm']*mod_df['rout']
            elif spec == 'ft':
                mod_df['ft'] = mod_df['gm']/(2*math.pi*mod_df['cgg'])
            elif spec == 'gmoverid':
                mod_df['gmoverid'] = mod_df['gm']/mod_df['id']
        return mod_df

    def compute_conditional_df(self, conditions, tolerance_percent=1.0, WoverL_min=0.5, Wmax=100e-6):
        parsed_conditions = [parse_condition(cond) for cond in conditions]

        self.conditional_df = pd.DataFrame(columns=self.mod_df.columns)
        flag = 0
        for row in parsed_conditions:
            temp_copy = self.mod_df.copy()

            if row[0] in self.proportional:
                temp_copy['W'] = self.mod_df['W'].multiply(float(row[2])/self.mod_df[row[0]], axis=0)

            elif row[0] in self.inversly:
                temp_copy['W'] = self.mod_df['W'].multiply(self.mod_df[row[0]]/float(row[2]), axis=0)

            if row[0] in self.proportional+self.inversly:
                temp_copy['condition'] = row[0]

                temp_copy = temp_copy[temp_copy['W'] < Wmax] # Condition to ensure W is less than the max
                temp_copy = temp_copy[temp_copy['W']/temp_copy['L'] > WoverL_min] # Condition to ensure W/L is greater than min.

                temp_copy[self.proportional] = temp_copy[self.proportional].multiply(temp_copy['W']/self.df['W'], axis=0)
                temp_copy[self.inversly] = temp_copy[self.inversly].divide(temp_copy['W']/self.df['W'], axis=0)
                

                self.conditional_df = pd.concat([self.conditional_df, temp_copy], ignore_index=True)
                flag = 1
        self.conditional_df['area'] = self.conditional_df['W'].multiply(self.conditional_df['L'], axis=0)
        if not flag:
            raise Exception("The conditions are not sufficient")

        # Initialize met_specs column with True values
        self.conditional_df['met_specs'] = True
        for condition in parsed_conditions:
            if condition[1] == '=':
                tolerance = tolerance_percent / 100.0 * float(condition[2])
                condition_str1 = f"{condition[0]} <= {condition[2]}+{tolerance}"
                condition_str2 = f"{condition[0]} >= {condition[2]}-{tolerance}"
                self.conditional_df['met_specs'] &= self.conditional_df.eval(condition_str1)
                self.conditional_df['met_specs'] &= self.conditional_df.eval(condition_str2)
            elif condition[1] == '>':
                self.conditional_df['met_specs'] &= self.conditional_df.eval(f"{condition[0]} >= {condition[2]}")
            elif condition[1] == '<':
                self.conditional_df['met_specs'] &= self.conditional_df.eval(f"{condition[0]} <= {condition[2]}")
        


    
