from __future__ import annotations  # Enables forward references
import json
import pandas as pd
from dataclasses import dataclass
from typing import List, Literal, Optional, Dict, Union, Callable, Any
from IPython.display import display

VariableType    = Literal["nominal", "continuous", "ordinal"]
VariableStorage = Literal["string", "int", "float", "date"]
DatasetRole     = Literal["estimation", "validation", "test", "apply"]

from dataclasses import dataclass
from typing import List, Union, Optional
import pandas as pd

@dataclass
class Category:
    count: int = 0
    frequency: float = 0.0
    target_mean: Optional[float] = None
    order: Optional[int] = None
    encoding: Optional[float] = None

@dataclass
class NominalCategory(Category):
    value: Union[str, float] = ""
    
    def to_string(self) -> str:
        return str(self.value)

@dataclass
class IntervalCategory(Category):
    interval: pd.Interval = pd.Interval(0, 0)
    is_date: bool = False

    def to_string(self) -> str:
        left = self.interval.left if not self.is_date else pd.to_datetime(self.interval.left).strftime('%Y-%m-%d')
        right = self.interval.right if not self.is_date else pd.to_datetime(self.interval.right).strftime('%Y-%m-%d')
        #left = self.interval.left
        #right = self.interval.right
        is_left_open = "[" if self.interval.closed_left else "]"
        is_right_open = "]" if self.interval.closed_right else "["
        return f"{is_left_open}{left}, {right}{is_right_open}"

@dataclass
class MissingCategory(Category):
    def to_string(self) -> str:
        return "Missing"
    
@dataclass
class OtherCategory(Category):
    values: Optional[List[Union[str, float]]] = None
    def to_string(self) -> str:
        return "Other"

@dataclass
class GroupCategory(Category):
    values: Optional[List[Union[str, float]]] = None
    otherCategory: Optional[OtherCategory] = None  # type: ignore

    def to_string(self) -> str: 
        if len(self.values) > 1:
            return "[" + ", ".join(str(v) for v in self.values) + "]"
        else:
            return str(self.values[0])
    
@dataclass
class Statistics:
    categories: List[Category]
    min: Optional[float] = None
    max: Optional[float] = None
    gini: Optional[float] = None
    grouped_categories: Optional[List[Category]] = None
    series: Optional[pd.Series] = None
    is_encoded: bool = False

    def set_data(self, data: pd.Series, storage: VariableStorage, type: VariableType, missing: Optional[str] = None):
        if storage == "date" and type == "continuous":
            from .stats import safe_parse_date
            self.series = data.astype(str)
            self.series = self.series.apply(safe_parse_date)
            self.series = pd.to_datetime(self.series, errors='coerce', utc=True)
            self.series = self.series.astype(int)
        elif storage == "int" or storage == "float":
            self.series = data.copy()
            if missing is not None:
                from numpy import nan
                self.series = data.replace(missing, nan)
            self.series = pd.to_numeric(self.series, errors='coerce')
        elif storage == "string":
            self.series = data.astype(str)
        else:
            self.series = data.copy()

@dataclass
class Variable:
    name: str
    type: VariableType
    storage: VariableStorage
    missing: Optional[str] = None
    order: Optional[List[str]] = None
    statistics: Optional[Dict[DatasetRole, Statistics]] = None
    
    def is_nominal(self) -> bool:
        return self.type == "nominal"
    
    def is_continuous(self) -> bool:
        return self.type == "continuous"
    
    def is_ordinal(self) -> bool:
        return self.type == "ordinal"
    
    def build_statistics(self, target: Optional[Variable] = None, label: DatasetRole = "estimation"):
        # create dataframe from statistics series
        if target is None:
            df = pd.DataFrame({ self.name: self.statistics[label].series })
        else:
            df = pd.DataFrame({ self.name: self.statistics[label].series, target.name: target.statistics[label].series })
        from .stats import create_target_categories, create_input_statistics
        if target is None:
          self.statistics[label].categories = create_target_categories(df, self) 
        else:
          stats = create_input_statistics(df, self, target, label)
          self.statistics[label] = stats

    def compute_gini(self, target: Variable, label: DatasetRole = "estimation"):
        from .stats import calculate_gini
        categories = self.statistics[label].grouped_categories if self.statistics[label].grouped_categories is not None else self.statistics[label].categories 
        self.statistics[label].gini = calculate_gini(categories, target.statistics[label].categories, target.type)
    
    def display(self, grouped: bool = False, label: DatasetRole = "estimation"):
        categories = self.statistics[label].grouped_categories if grouped else self.statistics[label].categories
        display(to_dataframe(categories))
    
    def to_dataframe(self, grouped: bool = False, label: DatasetRole = "estimation"):
        categories = self.statistics[label].grouped_categories if grouped else self.statistics[label].categories
        return to_dataframe(categories)
    
    def encode(self, series: Optional[pd.Series] = None, label: DatasetRole = "estimation"):
        if series is None:
            series = self.statistics[label].series
        from .stats import encode_variable
        categories = self.statistics[label].grouped_categories if self.statistics[label].grouped_categories is not None else self.statistics[label].categories
        self.statistics[label].series = encode_variable(series, categories, self.type)
        self.statistics[label].is_encoded = True
    
    def plot_lorenz_curve(self, target: Variable, label: DatasetRole = "estimation", theme: Literal["light", "dark"] = "light"):
        from .plot import plot_lorenz_curve
        plot_lorenz_curve(self, target, label, theme)

    def plot_encoding(self, target: Variable, label: DatasetRole = "estimation", theme: Literal["light", "dark"] = "light"):
        if self.type == "continuous":
            from .plot import plot_encoded_variable, create_encoded_dataframe
            dfplot = create_encoded_dataframe(self)
            plot_encoded_variable(dfplot, self.name, theme)
        else:
            print("Cannot plot encoded function for non-continuous variable")

    def estimate(self, target: Variable, grouped: bool = True, fro: DatasetRole = "estimation", to: DatasetRole = "test"):
        if target.statistics[to].is_encoded is False:
            target.build_statistics(label=to)
            target.encode(label=to)
        from .stats import estimate, add_order
        new_categories = estimate(self, target, grouped, fro, to)
        ordered_categories = add_order(self.type, new_categories, order_by="target_mean", order=self.order)
        # Save the new categories in the statistics for the "test" dataset
        if grouped:
            self.statistics[to].grouped_categories = ordered_categories
        else:
            self.statistics[to].categories = ordered_categories
        self.compute_gini(target, to)
@dataclass
class Coder:
    target: Variable
    inputs: Dict[str, Variable]
    skipped: List[str]

    def __init__(self, desc_file_path: str):
        with open(desc_file_path, 'r') as file:
            desc_json = json.load(file)
        target = next((v for v in desc_json.get('variables', []) if v.get("role") == "target"), None)
        inputs = [v for v in desc_json.get('variables', []) if v.get("role") == "input" or v.get("role") == "skipped"]
        # skipped is the list of skipped variables names
        self.skipped = [v.get("name") for v in desc_json.get('variables', []) if v.get("role") == "skipped"]
    
        self.target=Variable(
            name=target.get("name"),
            type=target.get("type"),
            storage=target.get("storage"),
            missing=None,
            order=target.get("order", None)
        )

        self.inputs={}

        for input_var in inputs:
            name = input_var.get("name")
            self.inputs[name] = Variable(
                name=name,
                type=input_var.get("type"),
                storage=input_var.get("storage"),
                missing=input_var.get("missing", None),
                order=input_var.get("order", None)
            )

    def set_data(self, data: pd.DataFrame, label: DatasetRole = "estimation"):
        def set_data_for_variable(variable: Variable):
            if variable.statistics is None:
                variable.statistics = {}    
            if label not in variable.statistics:
                variable.statistics[label] = Statistics(
                   categories=None, 
                   min=None, 
                   max=None, 
                   gini=None, 
                   grouped_categories=None, 
                   series=None
                )
            variable.statistics[label].set_data(data[variable.name], variable.storage, variable.type, variable.missing)
            print(".", end="", flush=True)
        self.foreach_input(set_data_for_variable)
        if label != "apply":
            set_data_for_variable(self.target)
        print("\nDone")

    def display_description(self):
        rows = []

        rows.append({
            "Name": self.target.name,
            "Type": self.target.type,
            "Missing": self.target.missing if self.target.missing is not None else "None",
            "Storage": self.target.storage,
            "Role": "Target"
        })

        for name, properties in self.inputs.items():
            if name not in self.skipped:
                rows.append({
                    "Name": name,
                    "Type": properties.type,
                    "Missing": properties.missing if properties.missing is not None else "None",
                    "Storage": properties.storage,
                    "Role": "Input"
                })

        for name in self.skipped:
            rows.append({
                "Name": name,
                "Type": self.inputs[name].type,
                "Missing": self.inputs[name].missing if self.inputs[name].missing is not None else "None",
                "Storage": self.inputs[name].storage,
                "Role": "Skipped"
            })

        df = pd.DataFrame(rows)
        pd.set_option('display.max_rows', len(df)+1)
        display(df)
        pd.reset_option('display.max_rows')

    def display_ginis(self, label: DatasetRole = "estimation"):
        gini_scores = {}
        # format gini score to 2 decimal place
        self.foreach_input(lambda v: gini_scores.__setitem__(v.name, round(v.statistics[label].gini, 2)), lambda v: v.statistics[label].gini)
        gini_scores_df = pd.DataFrame.rename(pd.DataFrame.from_dict(gini_scores, orient='index'), columns={0: 'Normalized Gini score'}).sort_values(by='Normalized Gini score', ascending=False)
        pd.set_option('display.max_rows', len(gini_scores_df)+1)
        display(gini_scores_df)
        pd.reset_option('display.max_rows')

    # iterage input variables sorted by lambda arg "sort" and apply function "func"
    def foreach_input(self, func: Callable[[Variable], Any], sort: Optional[Callable[[Variable], Any]] = None):
      if sort is None:
        for variable in self.inputs.values():
          func(variable)
      else:
        for variable in sorted(self.inputs.values(), key=sort):
          func(variable)

    def build(self, label: DatasetRole = "estimation"):
        print("Build target...")
        self.target.build_statistics(label=label)
        print("Encode target...")
        self.target.encode(label=label)
        print("Build inputs...")
        def build_input(v: Variable):
            # print one dot per input
            print(".", end="", flush=True)
            v.build_statistics(self.target, label)
        self.foreach_input(build_input)
        print("\nDone")

    def encode(self, data: pd.DataFrame, label: DatasetRole = "estimation") -> pd.DataFrame:
        from .stats import encode_variable
        print("Set data...")
        self.set_data(data, "apply")
        print("Encode data...")
        # Accumulate the series in a list
        encoded_series = []
        
        def encode(v: Variable):
            categories = v.statistics[label].grouped_categories if v.statistics[label].grouped_categories is not None else v.statistics[label].categories
            encoded_series.append(pd.Series(encode_variable(v.statistics["apply"].series, categories, v.type), name=v.name))
            print(".", end="", flush=True)
        
        self.foreach_input(encode)
        
        # Use pd.concat to join all series at once
        res = pd.concat(encoded_series, axis=1)
        print("\nDone")
        return res

def to_dataframe(categories: List[Category]) -> pd.DataFrame:
    data = []
    for category in categories:
        data.append({
            'value': category.to_string(),
            'count': category.count,
            'frequency': category.frequency,
            'target_mean': category.target_mean,
            'order': category.order,
            'encoding': category.encoding
        })
    
    return pd.DataFrame(data)
