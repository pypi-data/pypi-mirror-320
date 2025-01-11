import pandas as pd
import matplotlib.pyplot as plt
import re
import seaborn as sns
import matplotlib.lines as mlines
import numpy as np


def plot_all_protein_z_scores(df, target, 
                              highlighted_compounds=None,
                              highlighted_label=None, 
                              xticks=True,
                             use_standard_error=True,
                             verbose=True):

    subdf = df[df["Genes"]==target]
    if subdf.empty:
        if verbose:
            print(f"No data found for {target}")
        return
    
    # Step 1: Group and aggregate by compound
    if use_standard_error:
        compound_stats = subdf.groupby("Compound")["Z Score"].agg(
            median="median",
            se=lambda x: np.std(x, ddof=1) / np.sqrt(len(x)),  # Standard error calculation
            count="count"  # To display occurrence counts if needed
        ).reset_index()
    else:
        compound_stats = subdf.groupby("Compound")["Z Score"].agg(
            median="median",
            min="min",
            max="max",
            count="count"
        ).reset_index()


    # Step 2: Sort compounds by median Z Score
    compound_stats = compound_stats.sort_values(by="median").reset_index(drop=True)
    
    # Step 3: Create figure and plot each compound with conditional coloring
    fig, ax = plt.subplots(figsize=(10, 5))
    for _, row in compound_stats.iterrows():
        color = 'red' if row["Compound"] in highlighted_compounds else 'blue'
        
        # Conditionally use standard error or min-max for yerr
        if use_standard_error:
            yerr = row["se"]
        else:
            yerr = [[row["median"] - row["min"]], [row["max"] - row["median"]]]
        
        ax.errorbar(
            row["Compound"],                   # x-axis: Compound name
            row["median"],                     # y-axis: median Z Score
            yerr=yerr,                         # Error bars (SE or min-max)
            fmt='o',                           # Point style
            capsize=4,                         # Error bar cap size
            color=color,                       # Conditional color
            label="_nolegend_"                 # Prevents automatic addition to legend
        )
       
       
    # Add a horizontal line at y=0 without a label
    ax.axhline(0, color="grey", linestyle="--")
    
    # Manually create legend handles
    if highlighted_compounds is not None:
        highlighted_handle = mlines.Line2D([], [], color='red', marker='o', linestyle='None',
                                           markersize=8, label='Wave2 Compounds')
        normal_handle = mlines.Line2D([], [], color='blue', marker='o', linestyle='None',
                                      markersize=8, label='Other Compounds')
    
    # Customize the plot
    ax.set_xlabel("Compound")
    ax.set_ylabel("Z Score")
    if use_standard_error:
        ax.set_title(f"{target}: Median Z Score by Compound with Standard Error Bars")
    else:
        ax.set_title(f"{target}: Median Z Score by Compound with Min/Max Error Bars")
    ax.legend(handles=[highlighted_handle, normal_handle])
    
    # Remove non-highlighted x-axis labels
    if not xticks:
        for tick in ax.get_xticklabels():
            if tick.get_text() not in highlighted_compounds:
                tick.set_visible(False)
        
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

# def plot_all_z_scores(df: pd.DataFrame) -> None:
#     # Step 1: Group by 'Compound' and calculate median, min, and max Z Scores
#     compound_stats = df.groupby("Compound")["Z Score"].agg(
#         median="median",
#         min="min",
#         max="max"
#     ).reset_index()


#     # Step 2: Sort compounds by median Z Score
#     compound_stats = compound_stats.sort_values(by="median")

#     # Step 3: Plot with error bars
#     plt.figure(figsize=(10, 6))
#     plt.errorbar(
#         compound_stats["Compound"],          # x-axis: Compound names (sorted)
#         compound_stats["median"],            # y-axis: median Z Score
#         yerr=[compound_stats["median"] - compound_stats["min"],  # Error bar from min to median
#             compound_stats["max"] - compound_stats["median"]], # Error bar from median to max
#         fmt='o',                             # Point style
#         capsize=4,                           # Error bar cap size
#         color='blue'
#     )

#     plt.axhline(0, color="red", linestyle="--")
#     # Customize the plot
#     plt.xlabel("Compound")
#     plt.ylabel("Z Score")
#     plt.title("STAT3: Median Z Score by Compound with Min/Max Error Bars")
#     plt.xticks(rotation=90)
#     plt.tight_layout()

#     plt.show()

def plot_all_protein_z_scores(df, target, 
                              highlighted_compounds=None,
                              highlighted_label=None, 
                              xticks=True,
                              use_standard_error=True,
                              verbose=True):

    subdf = df[df["Genes"]==target]
    if subdf.empty:
        if verbose:
            print(f"No data found for {target}")
        return
    
    # Step 1: Group and aggregate by compound
    if use_standard_error:
        compound_stats = subdf.groupby("Compound")["Z Score"].agg(
            median="median",
            se=lambda x: np.std(x, ddof=1) / np.sqrt(len(x)),  # Standard error calculation
            count="count"  # To display occurrence counts if needed
        ).reset_index()
    else:
        compound_stats = subdf.groupby("Compound")["Z Score"].agg(
            median="median",
            min="min",
            max="max",
            count="count"
        ).reset_index()


    # Step 2: Sort compounds by median Z Score
    compound_stats = compound_stats.sort_values(by="median").reset_index(drop=True)
    
    # Step 3: Create figure and plot each compound with conditional coloring
    fig, ax = plt.subplots(figsize=(10, 5))
    for _, row in compound_stats.iterrows():
        color = 'red' if row["Compound"] in highlighted_compounds else 'blue'
        
        # Conditionally use standard error or min-max for yerr
        if use_standard_error:
            yerr = row["se"]
        else:
            yerr = [[row["median"] - row["min"]], [row["max"] - row["median"]]]
        
        ax.errorbar(
            row["Compound"],                   # x-axis: Compound name
            row["median"],                     # y-axis: median Z Score
            yerr=yerr,                         # Error bars (SE or min-max)
            fmt='o',                           # Point style
            capsize=4,                         # Error bar cap size
            color=color,                       # Conditional color
            label="_nolegend_"                 # Prevents automatic addition to legend
        )
       
       
    # Add a horizontal line at y=0 without a label
    ax.axhline(0, color="grey", linestyle="--")
    
    # Manually create legend handles
    if highlighted_compounds is not None:
        highlighted_handle = mlines.Line2D([], [], color='red', marker='o', linestyle='None',
                                           markersize=8, label='Wave2 Compounds')
        normal_handle = mlines.Line2D([], [], color='blue', marker='o', linestyle='None',
                                      markersize=8, label='Other Compounds')
    
    # Customize the plot
    ax.set_xlabel("Compound")
    ax.set_ylabel("Z Score")
    if use_standard_error:
        ax.set_title(f"{target}: Median Z Score by Compound with Standard Error Bars")
    else:
        ax.set_title(f"{target}: Median Z Score by Compound with Min/Max Error Bars")
    ax.legend(handles=[highlighted_handle, normal_handle])
    
    # Remove non-highlighted x-axis labels
    if not xticks:
        for tick in ax.get_xticklabels():
            if tick.get_text() not in highlighted_compounds:
                tick.set_visible(False)
        
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()



def plot_target_z_scores_transpose(df,
                                   target,
                                   highlighted_compounds,
                                   peptide="cysteine",
                                   clean_peptides=True,
                                   truncate_peptides=False,
                                   ax=None,
                                   verbose=True):
    """
    Plot robust Z scores for a target by peptide across all compounds,
    highlighting cysteine peptides for specific highlighted compounds.
    
    Args:
        df (pd.DataFrame): DataFrame containing Z scores for different peptides.
        target (str or list): Target gene or list of target genes to filter by.
        highlighted_compounds (list): List of compounds to highlight cysteine peptides.
        peptide (str or list): Peptide(s) to highlight (e.g., "cysteine" for cysteine peptides).
        clean_peptides (bool): Whether to apply peptide cleaning to 'Precursor.Id'.
        truncate_peptides (bool): Whether to truncate peptide names on the y-axis.
        ax (plt.Axes): Matplotlib Axes object to plot on, creates new if None.
    
    Notes:
        This function assumes 'df' is a melted DataFrame with Z scores.
    """
    def clean_peptide(peptide):
        return re.sub(r'\(UniMod:\d+\)', '', peptide)

    # Filter for the target(s) across all compounds
    if isinstance(target, str):
        subdf = df.loc[df["Genes"] == target]
    else:
        subdf = df.loc[df["Genes"].isin(target)]

    if subdf.empty:
        if verbose:
            print(f"no data found for {target}")
        return

    subdf = subdf[subdf["Compound"]!="TAL48"]
    
    # Clean peptides if specified
    if clean_peptides:
        subdf["Cleaned_Peptide"] = subdf["Precursor.Id"].apply(clean_peptide)
    else:
        subdf["Cleaned_Peptide"] = subdf["Precursor.Id"]

    

    # Define highlighted peptides based on cysteine content if specified
    if peptide == 'cysteine':
        highlight_peptides = [clean_peptide(pep) if clean_peptides else pep
                              for pep in subdf["Precursor.Id"].unique() if "C" in pep]
    else:
        highlight_peptides = [peptide] if isinstance(peptide, str) else peptide

    subdf = subdf.loc[subdf["Cleaned_Peptide"].isin(highlight_peptides)]

    if subdf.empty:
        if verbose:
            print(f"no cysteine peptides found for {target}")
        return

    # Determine figure height based on unique peptides
    custom_height = 0.25 * subdf["Cleaned_Peptide"].nunique()
    fig_height = max(custom_height, 3)

    # Create figure and axis if not provided
    created_fig = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, fig_height))
        created_fig = True

    # Plot all peptides with a beeswarm effect using Seaborn's stripplot
    all_else = subdf.loc[subdf["Cleaned_Peptide"].isin(highlight_peptides)]
    sns.stripplot(
        data=all_else,
        x="Z Score",
        y="Cleaned_Peptide",
        order=subdf["Cleaned_Peptide"].unique(),  # To keep consistent y-axis order
        jitter=0.25,  # Controls the spread for the beeswarm effect
        color="lightblue",  # Default color for non-highlighted peptides
        ax=ax,
        alpha=0.6,
        size=6
    )
     # Create a list to store legend handles
    legend_handles = []


  # Assign a color palette for highlighted compounds
    palette = sns.color_palette("bright", len(highlighted_compounds))

    # Highlight cysteine peptides in each highlighted compound with a unique color
    for idx, compound in enumerate(highlighted_compounds):
        compound_color = palette[idx]
        compound_df = subdf[subdf["Compound"] == compound]
        for p in highlight_peptides:
            peptide_df = compound_df[compound_df["Cleaned_Peptide"] == p]
            if not peptide_df.empty:
                sns.stripplot(
                    data=peptide_df,
                    x="Z Score",
                    y="Cleaned_Peptide",
                    order=subdf["Cleaned_Peptide"].unique(),
                    jitter=0.25,
                    color=compound_color,
                    ax=ax,
                    size=8,  # Larger size for highlighted points
                    edgecolor="black",
                    linewidth=0.6
                )
        # Add a custom legend handle for this compound
        legend_handles.append(
            plt.Line2D([0], [0], marker='o', color='w', label=compound,
                       markerfacecolor=compound_color, markersize=8, markeredgecolor='black')
        )

    # Add a vertical line at Z score = 0 for reference
    ax.axvline(0, color='black', linestyle="--")

    ax.margins(y=0.3)
    # Customize the plot
    ax.set_xlabel("Robust Z Score")
    ax.set_ylabel("Peptides")
    ax.set_title(f"{target} - Z Scores by Peptide and Compound")
    
    # Display the legend for highlighted compounds

    ax.legend(handles=legend_handles)

    # Only apply layout adjustments if a new figure was created
    if created_fig:
        plt.tight_layout()
        plt.show()


def plot_protein_z_scores(df,
                          target,
                          compound=None,
                          hline=False,
                          xticks=True,
                          ax=None,
                          savefig=False,
                          show=True):

    if ax is None:
        fig, ax = plt.subplots(figsize=(10,5))
    else:
        show=False
        savefig=False
    
    # Filter for the target, compound
    subdf = df.loc[df["Genes"]==target]

    # Plot all compounds
    ax.scatter(subdf["Compound"], subdf["Z Score"],
                color='blue',
                alpha=0.5)


    # Highlight specific compound(s)
    if compound:
        if isinstance(compound, str):
            compound = [compound]
    
        for c in compound:
            compound_df = subdf.loc[subdf["Compound"]==c]
            ax.scatter(compound_df["Compound"], compound_df["Z Score"],
                        color='red',
                        s=100,
                        edgecolor='black'
                       )
           # Label the first occurrence of the specific compound
            if not compound_df.empty:
                first_row = compound_df.iloc[0]
                label_y_pos = 2.5*np.std(df["Z Score"])
                ax.text(first_row["Compound"], label_y_pos, 
                         c, color='red', fontsize=10, ha='center', va='top')


    # Add line at 0 if hline = True
    if hline:
        ax.axhline(0, color='red', linestyle="--", linewidth=1)

    # Add labels
    if xticks:
        ax.set_xticklabels(subdf["Compound"], rotation=90)
    else:
        ax.set_xticklabels([])
    ax.set_ylabel("Robust Z Score")
    ax.set_xlabel("Compounds")
    ax.set_title(target)

    # Save and show
    if savefig:
        is_negative = peptide_df["Z Score"] < 0
        is_negative_sum = is_negative.sum()
        if is_negative_sum == len(peptide_df):
            status="good"
        else:
            status="bad"
        save_path = os.path.join(os.getcwd(), status, f"{target}.png")
        plt.tight_layout()
        plt.savefig(save_path)
    if show:
        plt.show()