import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Literal
from .stats import calculate_cumulative
from .main import Variable

def plot_lorenz_curve(input: Variable, target: Variable, label: Literal["estimation", "validation", "test"], theme: str = "light"):
    input_data = input.statistics[label].grouped_categories if input.statistics[label].grouped_categories is not None else input.statistics[label].categories
    target_data = target.statistics[label].categories
    cumulative_frequency2, cumulative_target2, max_target2 = calculate_cumulative(target_data, ascending=False)
    cumulative_frequency1, cumulative_target1, max_target1 = calculate_cumulative(input_data, ascending=False, max=max_target2)
    # Préparer les étiquettes pour l'axe des x en triant les catégories par ordre croissant de la target_mean
    x_labels1 = sorted(input_data, key=lambda x: x.target_mean)[::-1]
    # convert x_labels1 to string
    x_labels1 = [category.to_string() for category in x_labels1]
    # limit the length of the string to 50 characters
    x_labels1 = [category[:50] + "..." if len(category) > 50 else category for category in x_labels1]

    # Courbe d'égalité parfaite
    if target.type == "nominal":
        equality_x = np.linspace(0, 1, 100)
        equality_y = equality_x
    elif target.type == "ordinal":
        equality_x = np.linspace(0, 1, 100)
        equality_y = np.linspace(0, 0, 100)
    else:
        raise ValueError(f"Unknown target type: {target.type}")

    # Set theme colors
    if theme == "dark":
        plt.style.use('dark_background')
        line_colors = {"curve1": "orange", "curve2": "green", "equality": "red"}
        text_color = "white"
    else:
        plt.style.use('default')
        line_colors = {"curve1": "blue", "curve2": "purple", "equality": "black"}
        text_color = "black"

    # Plot with transparent background
    plt.figure(figsize=(12, 8), facecolor='none', edgecolor='none')
    plt.plot(cumulative_frequency1, cumulative_target1, label=f"Lorenz curve for '{input.name}'", color=line_colors["curve1"], lw=2)
    plt.plot(cumulative_frequency2, cumulative_target2, label=f"Lorenz curve for '{target.name}'", color=line_colors["curve2"], linestyle="--", lw=2)
    plt.plot(equality_x, equality_y, label="random model", color=line_colors["equality"], linestyle="--", lw=2)

    # Décorations
    plt.xticks(ticks=np.linspace(0, 1, len(x_labels1)), labels=x_labels1, rotation=45, ha="right", color=text_color)
    plt.xlabel("Category Values", fontsize=12, color=text_color)
    plt.ylabel("Cumulated target (wealth)", fontsize=12, color=text_color)
    plt.legend(fontsize=12)
    plt.grid(alpha=0.3)
    plt.axis("equal")  # Échelle égale pour x et y

    # Afficher le graphique
    plt.tight_layout()
    #plt.savefig('lorenz_curve.png', transparent=True)  # Save with transparency
    plt.show()

def create_encoded_dataframe(variable: Variable):
    min_val = variable.statistics["estimation"].min
    max_val = variable.statistics["estimation"].max
    
    # Créer un DataFrame avec 100 valeurs uniformément réparties
    dfplot = pd.DataFrame({
        variable.name: np.linspace(min_val, max_val, 100)
    })
    
    # Ajouter une colonne encodée
    from .stats import encode_variable
    categories = variable.statistics["estimation"].grouped_categories if variable.statistics["estimation"].grouped_categories is not None else variable.statistics["estimation"].categories
    dfplot[variable.name + "_encoded"] = encode_variable(dfplot[variable.name], categories, variable.type)
    return dfplot

def plot_encoded_variable(dfplot, variable_name, theme: str = "light"):
    # Set theme colors
    if theme == "dark":
        plt.style.use('dark_background')
        line_colors = {"curve1": "orange", "curve2": "green", "equality": "red"}
        text_color = "white"
    else:
        plt.style.use('default')
        line_colors = {"curve1": "blue", "curve2": "purple", "equality": "black"}
        text_color = "black"
    plt.figure(figsize=(10, 8), facecolor='none', edgecolor='none')
    plt.plot(dfplot[variable_name], dfplot[variable_name + "_encoded"], label=f'Encoded {variable_name}',color=line_colors["curve1"])
    plt.xlabel(variable_name, fontsize=12, color=text_color)
    plt.ylabel(variable_name + "_encoded", fontsize=12, color=text_color)
    plt.title(f"Encoding of Variable '{variable_name}'", fontsize=12, color=text_color)
    plt.legend(fontsize=12)
    plt.grid(alpha=0.3)
    plt.show()