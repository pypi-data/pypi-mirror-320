import pandas as pd
import numpy as np
from dateutil import parser
import matplotlib.pyplot as plt
from typing import List, Optional
from .main import Variable
from .main import Statistics
from .main import Category, NominalCategory, IntervalCategory, MissingCategory, OtherCategory, GroupCategory
from typing import Literal
from typing import Tuple

def safe_parse_date(date_str):
    try:
        parsed_dt = parser.parse(date_str)
        return pd.Timestamp(parsed_dt).value
    except (ValueError, TypeError):
        # Retourne NaN ou NaT quand la conversion échoue
        print(f"Warning parsing date: {date_str}")
        return np.nan

def create_categories(df: pd.DataFrame, variable: Variable, target: Optional[str] = None) -> List[Category]:
    if variable.is_nominal() or variable.is_ordinal():
        stats = df[variable.name].value_counts(normalize=False).reset_index()
        stats.columns = ['value', 'count']
        stats['frequency'] = stats['count'] / len(df)
        
        if target is not None:
            target_mean = df.groupby(variable.name)[target].mean().reset_index()
            target_mean.columns = ['value', 'target_mean']
            stats = stats.merge(target_mean, on='value', how='left')
        else:
            stats['target_mean'] = None

        # Convert to list of Category
        categories: List[Category] = [
            NominalCategory(
                value=row['value'],
                count=row['count'],
                frequency=row['frequency'],
                target_mean=row['target_mean']
            )
            for _, row in stats.iterrows()
        ]
        return categories
    elif variable.is_continuous():
        missing_category = None
        # filter out missing values
        quantiles = pd.qcut(df[variable.name].dropna(), q=20, duplicates='drop')
        stats = quantiles.value_counts(normalize=False).reset_index()
        # get first row
        stats.columns = ['value', 'count']
        # count missing values
        missing_count = df[variable.name].isna().sum()
        if missing_count > 0:
            missing_category = MissingCategory(count=missing_count, frequency=missing_count / len(df))
        stats['frequency'] = stats['count'] / len(df)
                    
        if target is not None:
            # For each quantile interval in stats, calculate mean target value
            target_mean = df.groupby(by=quantiles, observed=False)[target].mean().reset_index()
            target_mean.columns = ['value', 'target_mean']
            # compute target mean when variable is missing
            if missing_count > 0:
                missing_rows = df[df[variable.name].isna()]
                missing_target_mean = missing_rows[target].mean()
                # add to target_mean
                missing_category.target_mean = missing_target_mean
            stats = stats.merge(target_mean, on='value', how='left')
        else:
            stats['target_mean'] = None

        # Convert to list of Category
        categories: List[Category] = [
            IntervalCategory(
                interval=row['value'],
                is_date=variable.storage == "date",
                count=row['count'],
                frequency=row['frequency'],
                target_mean=row['target_mean']
            )
            for _, row in stats.iterrows()
        ]
        if missing_category is not None:
            categories.append(missing_category)
        return categories
    
def split_categories(categories: List[Category]) -> Tuple[List[Category], List[Category], List[Category]]:
    plain_categories = []
    other_categories = []
    empty_categories = []
    for category in categories:
        if category.count == 0:
            empty_categories.append(category)
        elif isinstance(category, MissingCategory):
            other_categories.append(category)
        elif isinstance(category, OtherCategory):
            other_categories.append(category)
        else:
            plain_categories.append(category)
    return plain_categories, other_categories, empty_categories

def add_order(variable_type: Literal["nominal", "continuous", "ordinal"], categories: List[Category], order_by: str = "frequency", order: Optional[List[str]] = None) -> List[Category]:
    plain_categories, other_categories, empty_categories = split_categories(categories)
    # set target_mean to None for empty categories
    for category in empty_categories:
        category.target_mean = 0
    plain_categories.extend(empty_categories)
    if order_by == "natural":
        if variable_type == "nominal" or variable_type == "ordinal":
            sorted_categories = sorted(
                plain_categories,
                key=lambda x: x.value
            )
        elif variable_type == "continuous":
            # filter out "Missing" category
            sorted_categories = sorted(
                plain_categories,
                key=lambda x: x.interval
            )
        for i, category in enumerate(sorted_categories):
            category.order = i
        # catenate other categories
        sorted_categories.extend(other_categories)
        return sorted_categories
    elif order_by == "specified":
        sorted_categories = sorted(
            categories,
            key=lambda x: order.index(str(x.value))
        )
    else:
        def get_value(category):
            return getattr(category, order_by)
        plain_categories.extend(other_categories)
        sorted_categories = sorted(
            plain_categories,
            key=get_value,
            reverse=(order_by == "frequency")
        )
    
    for i, category in enumerate(plain_categories):
        category.order = i
    return sorted_categories

def add_encoding(categories: List[Category], encoding_type: str = "dummy") -> List[Category]:
    if encoding_type == "dummy":
        for category in categories:
            category.encoding = category.order
    elif encoding_type == "uniform":
        total_frequency = sum(cat.frequency for cat in categories)
        cumulative_frequency = 0
        for category in categories:
            cumulative_frequency += category.frequency
            category.encoding = -1 + 2 * (cumulative_frequency - category.frequency / 2) / total_frequency
    else:
        raise ValueError(f"Unknown encoding type: {encoding_type}")
    return categories

def encode_variable(series: pd.Series, categories: List[Category], variable_type: Literal["nominal", "continuous", "ordinal"]) -> pd.Series:
    if variable_type == "continuous":
        # Extraire les centres des intervalles et les encodings
        interval_centers = []
        encodings = []
        missing_encoding = None

        # split categories into missing and no missing
        plain_categories, other_categories, empty_categories = split_categories(categories)
        for category in other_categories:
            missing_encoding = category.encoding

        # iterate on categories sorted by natural pandas interval order
        for category in sorted(plain_categories, key=lambda x: x.interval):
            interval = category.interval
            center = (interval.left + interval.right) / 2
            interval_centers.append(center)
            encodings.append(category.encoding)

        def interpolate(value):
            if len(interval_centers) == 0:
                return 0
            if pd.isna(value):
                if missing_encoding is not None:
                    return missing_encoding
                else:
                    return 0
            if len(interval_centers) == 1:
                return encodings[0]
            for i in range(len(interval_centers) - 1):
                if interval_centers[i] <= value < interval_centers[i + 1]:
                    # Interpolation linéaire
                    x1, y1 = interval_centers[i], encodings[i]
                    x2, y2 = interval_centers[i + 1], encodings[i + 1]
                    return y1 + (y2 - y1) * (value - x1) / (x2 - x1)
            # Gérer les valeurs aux extrêmes
            if value < interval_centers[0]:
                x1, y1 = interval_centers[0], encodings[0]
                x2, y2 = interval_centers[1], encodings[1]
                return y1 + (y2 - y1) * (value - x1) / (x2 - x1)
            elif value >= interval_centers[-1]:
                x1, y1 = interval_centers[-2], encodings[-2]
                x2, y2 = interval_centers[-1], encodings[-1]
                return y1 + (y2 - y1) * (value - x1) / (x2 - x1)
        
        # Appliquer l'interpolation sur la série
        encoded_series = series.apply(interpolate)
        return encoded_series
    
    elif variable_type == "ordinal":
        # create a local "encode" function to associate each value to an encoding
        def encode(value):
            for category in categories:
                # handle pandas interval
                if isinstance(category, IntervalCategory):
                    if category.interval.left <= value and category.interval.right >= value:
                        return category.encoding
                elif isinstance(category, NominalCategory):
                    if value == category.value:
                        return category.encoding
            # emit warning if value is not found in any category
            print(f"Warning: value {value} not found in any category")
            return np.nan
        encoded_series = series.apply(encode)
        return encoded_series
    else:
        encoding_map = {}
        for category in categories:
            if isinstance(category, OtherCategory):
                for value in category.values:
                    encoding_map[value] = category.encoding
            elif isinstance(category, GroupCategory):
                for value in category.values:
                    encoding_map[value] = category.encoding
                if category.otherCategory is not None:
                    for value in category.otherCategory.values:
                        encoding_map[value] = category.encoding
            else:
                encoding_map[category.value] = category.encoding
        encoded_series = series.map(encoding_map)
        return encoded_series

def merge_two_categories(cat1: Category, cat2: Category, input_type: str, input_storage: str) -> Category:
    """
    Merge two adjacent Category objects:
    - Aggregates their values
    - Adds up their counts and frequencies
    - Computes a weighted average of their target_mean
    The 'order' and 'encoding' fields are recalculated later if needed.
    """
    merged_count = cat1.count + cat2.count
    merged_frequency = cat1.frequency + cat2.frequency
    # Weighted target mean based on frequency
    if cat1.target_mean is not None and cat2.target_mean is not None:
        merged_target_mean = (
            cat1.target_mean * cat1.frequency + cat2.target_mean * cat2.frequency
        ) / merged_frequency
    else:
        merged_target_mean = None

    if input_type == "nominal":
        cat1values = []
        cat2values = []
        other_category = None
        if isinstance(cat1, OtherCategory):
            cat1values = [cat1.to_string()]
            other_category = cat1
        elif isinstance(cat1, GroupCategory):
            cat1values = cat1.values
        else:
            cat1values = [cat1.value]
        if isinstance(cat2, OtherCategory):
            cat2values = [cat2.to_string()]
            other_category = cat2
        elif isinstance(cat2, GroupCategory):
            cat2values = cat2.values
        else:
            cat2values = [cat2.value]
        return GroupCategory(
            values=cat1values + cat2values,
            count=merged_count,
            frequency=merged_frequency,
            target_mean=merged_target_mean,
            otherCategory=other_category
        )
    elif input_type == "continuous":
        # merge Pandas intervals
        return IntervalCategory(
            interval=pd.Interval(cat1.interval.left, cat2.interval.right),
            is_date=cat1.is_date,
            count=merged_count,
            frequency=merged_frequency,
            target_mean=merged_target_mean
        )
    else: # ordinal
        if input_storage == "int" or input_storage == "float":
            # if cat1.value[-1] is an Interval, cat2.value[-1] is an int or float
            if isinstance(cat1, IntervalCategory) and isinstance(cat2, NominalCategory):
                interval = pd.Interval(cat1.interval.left, cat2.value)
            elif isinstance(cat1, NominalCategory) and isinstance(cat2, IntervalCategory):
                interval = pd.Interval(cat1.value, cat2.interval.right)
            elif isinstance(cat1, NominalCategory) and isinstance(cat2, NominalCategory):
                interval = pd.Interval(cat1.value, cat2.value)
            elif isinstance(cat1, IntervalCategory) and isinstance(cat2, IntervalCategory):
                interval = pd.Interval(cat1.interval.left, cat2.interval.right)
            else:
                # throw error if cat1.values[-1] is not an interval or a float or an int
                raise ValueError(f"Unknown cat1 type: {cat1} and cat2 type: {cat2}")
            cat = IntervalCategory(
                interval=interval,
                count=merged_count,
                frequency=merged_frequency,
                target_mean=merged_target_mean
            )
            if hasattr(cat1, "is_date"):
                cat.is_date = cat1.is_date
            return cat
        else:
            cat1values = []
            cat2values = []
            
            if isinstance(cat1, GroupCategory):
                cat1values = cat1.values
            else:
                cat1values = [cat1.value]
            
            if isinstance(cat2, GroupCategory):
                cat2values = cat2.values
            else:
                cat2values = [cat2.value]
            return GroupCategory(
                values=cat1values + cat2values,
                count=merged_count,
                frequency=merged_frequency,
                target_mean=merged_target_mean
            )


def group_dictionary_by_gini(
    data_input: List[Category],
    input_type: str,
    input_storage: str,
    data_target: List[Category],
    target_type: str,
    max_loss: float = 0.01
) -> List[Category]:
    """
    Performs a hierarchical ascending clustering of adjacent categories based on their target_mean,
    merging two adjacent categories if the resulting Gini index does not drop more than the specified
    'max_loss' percentage. If the Gini drop exceeds 'max_loss', the merge is rejected.

    :param data_input: A list of Category objects describing the input variable.
    :param data_target: A list of Category objects describing the target variable (e.g. binary target).
    :param target_type: The type of the target variable (e.g. "nominal", "ordinal", "continuous").
    :param max_loss: The maximum percentage drop in the Gini index allowed when merging two categories.
    :return: A potentially merged list of Category objects.
    """
    other_categories = []
    if input_type == "continuous" or input_type == "ordinal":
        data_input, other_categories, empty_categories = split_categories(data_input)

    old_gini = calculate_gini(data_input, data_target, target_type)
    
    # 3) Iterate as long as a merge is accepted.
    while True:
        merged_any = False  # Will track if at least one merge is done in this pass
        i = 0

        # Pass from left to right
        while i < len(data_input) - 1:
            # Tentatively merge categories i and i+1
            merged_cat = merge_two_categories(data_input[i], data_input[i+1], input_type, input_storage)

            # Construct a hypothetical list with the merged category
            hypothetical_dict = data_input[:i] + [merged_cat] + data_input[i+2:]
            new_gini = calculate_gini(hypothetical_dict, data_target, target_type)

            # Check whether the Gini loss is within max_loss
            if new_gini >= old_gini * (1 - max_loss):
                # The Gini drop is acceptable, so accept the merge
                data_input = hypothetical_dict
                old_gini = new_gini
                merged_any = True
            else:
                # The Gini drop is too large, reject the merge
                i += 1
                continue

            # If the merge was accepted, we do not increment i here,
            # so we can consider merging the newly created merged_cat
            # again with the next category in the same pass.
            # If you want only one merge per pass, then uncomment the next line:
            # i += 1

        # If no merge was accepted in this pass, we're done
        if not merged_any:
            break

    # 4) At the end, we assign a final order if needed
    data_input = sorted(data_input, key=lambda c: (c.target_mean if c.target_mean is not None else float('inf')))
    for idx, cat in enumerate(data_input):
        cat.order = idx
    
    # add other categories
    data_input.extend(other_categories)
    return data_input

def group_other(categories: List[Category], min_count: int = 15) -> List[Category]:
    """
    Groups all categories with a "count" less than `min_count` into a new "other" category.

    :param categories: List of initial categories.
    :param min_count: Minimum count threshold to avoid being grouped.
    :return: New list of categories.
    """
    other_category = OtherCategory(
        values=[],
        count=0,
        frequency=0.0,
        target_mean=0.0,
    )
    
    new_categories = []
    
    for category in categories:
        if category.count < min_count:
            # Add to the "other" category
            other_category.values.extend(category.value if isinstance(category, NominalCategory) else category.to_string())
            # Compute the weighted average for target_mean in the "other" category
            other_category.target_mean = (
                other_category.target_mean * other_category.count +
                category.target_mean * category.count
            ) / (other_category.count + category.count)
            other_category.frequency = other_category.frequency + category.frequency
            other_category.count = other_category.count + category.count
        else:
            # Keep categories with sufficient count
            new_categories.append(category)
    
    # Add the "other" category if it has values
    if other_category.count > 0:
        new_categories.append(other_category)
    
    return new_categories

def create_input_statistics(df: pd.DataFrame, variable: Variable, target: Variable, label: Literal["estimation", "validation", "test"]) -> Statistics:
    categories = create_categories(df, variable, target.name)
    if variable.is_nominal():
        other_categories = group_other(categories)
        ordered_categories = add_order(variable.type, other_categories, "target_mean")
        grouped_categories = group_dictionary_by_gini(ordered_categories, variable.type, variable.storage, target.statistics[label].categories, target.type)
    elif variable.is_continuous():
        ordered_categories = add_order(variable.type, categories, "natural")
        grouped_categories = group_dictionary_by_gini(ordered_categories, variable.type, variable.storage, target.statistics[label].categories, target.type)
        grouped_categories = add_order(variable.type, grouped_categories, "target_mean")
    else:
        other_categories = group_other(categories)
        order = "natural" if variable.order is None else "specified"
        ordered_categories = add_order(variable.type, other_categories, order)
        grouped_categories = group_dictionary_by_gini(ordered_categories, variable.type, variable.storage, target.statistics[label].categories, target.type)
        grouped_categories = add_order(variable.type, grouped_categories, "target_mean")
    encoded_categories = add_encoding(grouped_categories, "uniform")
    if variable.is_continuous():
        min = df[variable.name].min()
        max = df[variable.name].max()
        stats = Statistics(categories=ordered_categories, grouped_categories=encoded_categories, min=min, max=max, series=df[variable.name])
    else:
        stats = Statistics(categories=ordered_categories, grouped_categories=encoded_categories, series=df[variable.name])
    return stats

########################
## Target dictionary
########################

def update_target_mean_with_encoding(categories: List[Category]) -> List[Category]:
    for category in categories:
        category.target_mean = category.encoding
    return categories

def create_target_categories(df: pd.DataFrame, target: Variable) -> List[Category]:
    categories = create_categories(df, target)
    if target.is_nominal():
        categories = add_order(target.type, categories, "frequency")
    elif target.is_ordinal():
        categories = add_order(target.type, categories, "specified", order=target.order)
    elif target.is_continuous():
        # emit error
        raise ValueError(f"Continuous target variables are not supported yet: {target.name}")
    else:
        raise ValueError(f"Unknown target type: {target.type}")
    if len(categories) == 2 and target.is_nominal():
        categories = add_encoding(categories, "dummy")
        categories = update_target_mean_with_encoding(categories)
    elif target.is_ordinal():
        categories = add_encoding(categories, "uniform")
        categories = update_target_mean_with_encoding(categories)
    else:
        raise ValueError(f"Target dictionary contains more than 2 values: {len(categories)}.")
    return categories

########################
## Gini index
########################

def calculate_gini(data_input: List[Category], data_target: List[Category], target_type: str) -> float:
    cumulative_frequency_input, cumulative_target_input, max_target_input = calculate_cumulative(data_input, ascending=False)
    cumulative_frequency_target, cumulative_target_target, max_target_target = calculate_cumulative(data_target, ascending=False, max=max_target_input)
    # Calculer l'aire sous la courbe de Lorenz
    lorenz_area_input = np.trapz(cumulative_target_input, cumulative_frequency_input)
    lorenz_area_target = np.trapz(cumulative_target_target, cumulative_frequency_target)

    if target_type == "nominal":
        lorenz_area_input = 1 - 2 * lorenz_area_input
        lorenz_area_target = 1 - 2 * lorenz_area_target

    gini_index = lorenz_area_input / lorenz_area_target
    return gini_index

def calculate_cumulative(data: List[Category], ascending: bool = False, max: Optional[float] = None) -> tuple[np.ndarray, np.ndarray, float]:
    target_mean = np.array([category.target_mean for category in data])
    frequency = np.array([category.frequency for category in data])

    # Trier par target_mean selon la direction souhaitée
    if ascending:
        sorted_indices = np.argsort(target_mean)
    else:
        # Par défaut : ordre décroissant (pour la courbe de Lorenz)
        sorted_indices = np.argsort(-target_mean)

    target_mean = target_mean[sorted_indices]
    frequency = frequency[sorted_indices]

    # Calcul des cumuls
    cumulative_frequency = np.cumsum(frequency)
    cumulative_target = np.cumsum(frequency * target_mean)

    # Ajouter un zéro initial
    cumulative_frequency = np.insert(cumulative_frequency, 0, 0)
    cumulative_target = np.insert(cumulative_target, 0, 0)

    # Normalise cumulative_target by the max value of cumulative_target 
    max_target = cumulative_target.max()
    if max is not None:
        max_target = max
    if max_target > 0:
        cumulative_target /= max_target

    return cumulative_frequency, cumulative_target, max_target

########################
## Apply
########################

def is_element_of(value, category: Category) -> bool:
    """
    Checks if a value belongs to a given category.

    :param value: The value to test.
    :param category: An instance of Category.
    :return: True if the value belongs to the category, False otherwise.
    """
    if isinstance(category, IntervalCategory):
        #print(f"value: {value}, interval: {category.interval}, contains: {category.interval.__contains__(value)}")
        return category.interval.__contains__(value)
    elif isinstance(category, NominalCategory):
        return value == category.value
    elif isinstance(category, MissingCategory):
        # return True if value is nan
        return pd.isna(value)
    elif isinstance(category, GroupCategory):
        if category.otherCategory is not None:
            return value in category.values or value in category.otherCategory.values
        else:
            return value in category.values
    return False



def estimate(input: Variable, target: Variable, grouped: bool = True, fro: str = "estimation", to: str = "test") -> List[Category]:
    """
    Estimates the grouped statistics from the input to the "test" (count, frequency, target_mean).

    :param input: The input variable containing the grouped categories.
    :param target: The target variable to calculate the means.
    :param grouped: Whether to use the grouped categories or not, default is True.
    :param fro: The dataset label categories are taken from, default is "estimation".
    :param to: The dataset label categories are applied to, default is "test".
    :return: A list of categories updated with the recalculated statistics.
    """
    # Retrieve "apply" data from the input
    apply_data = input.statistics[to].series
    apply_target = target.statistics[to].series

    # Get the grouped categories from the input
    grouped_categories = input.statistics[fro].grouped_categories if grouped else input.statistics[fro].categories
    if input.is_continuous():
        grouped_categories = adjust_smallest_interval(grouped_categories)  

    # Prepare a list to store the updated categories
    updated_categories = []

    for category in grouped_categories:
        # Filter the data corresponding to this category
        mask = apply_data.apply(lambda value: is_element_of(value, category))
        filtered_data = apply_data[mask]

        # Calculate the statistics for this category
        count = len(filtered_data)
        frequency = count / len(apply_data) if len(apply_data) > 0 else 0
        target_mean = None
        if count > 0:
            target_mean = apply_target[mask].mean()

        # Create a new instance of the category with the updated statistics
        if isinstance(category, NominalCategory):
            new_category = NominalCategory(
                value=getattr(category, "value", None),
                count=count,
                frequency=frequency,
                target_mean=target_mean
            )
        elif isinstance(category, IntervalCategory):
            new_category = IntervalCategory(
                interval=getattr(category, "interval", None),
                is_date=category.is_date,
                count=count,
                frequency=frequency,
                target_mean=target_mean
            )
        elif isinstance(category, GroupCategory):
            new_category = GroupCategory(
                values=getattr(category, "values", None),
                count=count,
                frequency=frequency,
                target_mean=target_mean,
                otherCategory=getattr(category, "otherCategory", None)
            )
        elif isinstance(category, MissingCategory):
            new_category = MissingCategory(
                count=count,
                frequency=frequency,
                target_mean=target_mean
            )
        else:
            raise TypeError(f"Unknown category type: {type(category)}")
        updated_categories.append(new_category)

    return updated_categories

def adjust_smallest_interval(categories: List[IntervalCategory]) -> List[IntervalCategory]:
    if not categories:
        return categories

    # split categories into missing and no missing  
    plain_categories, other_categories, empty_categories = split_categories(categories)
    # Find the smallest interval
    smallest_interval = min(plain_categories, key=lambda cat: cat.interval.left)

    # Adjust the lower bound of the smallest interval
    adjusted_categories = []
    for category in plain_categories:
        if category == smallest_interval:
            # remove 1% of the left value
            new_interval = pd.Interval(
                left=category.interval.left - 0.01 * (category.interval.right - category.interval.left),
                right=category.interval.right
            )
            adjusted_category = IntervalCategory(
                interval=new_interval,
                is_date=category.is_date,
                count=category.count,
                frequency=category.frequency,
                target_mean=category.target_mean
            )
            adjusted_categories.append(adjusted_category)
        else:
            adjusted_categories.append(category)

    # catenate missing categories
    adjusted_categories.extend(other_categories)
    print(f"adjusted lenngth vs original length: {len(adjusted_categories)} vs {len(categories)}")
    return adjusted_categories




