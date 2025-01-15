
try:
    import numpy as np
except ImportError:
    raise ImportError("Numpy is required but not installed. Please install via 'pip install numpy'.")

try:
    import pandas as pd
except ImportError:
    raise ImportError("pandas is required but not installed. Please install via 'pip install pandas'.")

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
except ImportError:
    raise ImportError("Matplotlib is required but not installed. Please install via 'pip install matplotlib'.")

# We'll conditionally import SciPy for spline interpolation
try:
    from scipy.interpolate import make_interp_spline
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("Warning: SciPy not found. Curves will be drawn as piecewise lines instead of splines.")

from collections import defaultdict

class PatientTrajectoryVisualizer:
    """
    A class to create a Gantt-style visualization of patient episodes.

    Example usage:
    --------------
    df = pd.DataFrame({
        "pasient": [1, 1, 2],
        "episode_start_date": ["2020-01-01", "2020-03-01", "2021-01-15"],
        "episode_end_date":   ["2020-02-01", "2020-04-01", "2021-02-15"],
        "age": [10, 11, 50],
        "cluster": [1, 2, 1],
        "diagnosis": ["Flu", "Cold", "Check-up"]
    })

    viz = PatientTrajectoryVisualizer(df=df)
    fig, ax = viz.plot_gantt(annotation_cols=["diagnosis"], save_path="myplot.png")
    plt.show()
    """

    def __init__(
        self,
        df: pd.DataFrame,
        pasient_col="pasient",
        cluster_col="cluster",
        start_date_col="episode_start_date",
        end_date_col="episode_end_date",
        # The user can store more defaults here if needed
    ):
        """
        Initialize the visualizer with a DataFrame and basic column mappings.
        """
        self.df = df
        self.pasient_col = pasient_col
        self.cluster_col = cluster_col
        self.start_date_col = start_date_col
        self.end_date_col = end_date_col

        # Basic validity checks
        if "age" not in df.columns:
            raise ValueError("DataFrame must have an 'age' column for the numeric axis.")
        if pasient_col not in df.columns:
            raise ValueError(f"DataFrame missing required column: {pasient_col}")

        # Make sure date columns are datetime
        if not np.issubdtype(df[start_date_col].dtype, np.datetime64):
            self.df[start_date_col] = pd.to_datetime(df[start_date_col], errors="coerce")
        if not np.issubdtype(df[end_date_col].dtype, np.datetime64):
            self.df[end_date_col] = pd.to_datetime(df[end_date_col], errors="coerce")

        # Compute age_start => from the "age" column
        self.df["age_start"] = self.df["age"]

        # Compute age_end => from the date difference (fallback = same as start)
        def compute_age_end(row):
            if pd.notnull(row[self.end_date_col]) and pd.notnull(row[self.start_date_col]):
                dur_days = (row[self.end_date_col] - row[self.start_date_col]).days
                return row["age_start"] + dur_days / 365.0
            else:
                return row["age_start"]

        self.df["age_end"] = self.df.apply(compute_age_end, axis=1)

        # Sort by patient, then by age_start
        self.df.sort_values(by=[pasient_col, "age_start"], inplace=True, ignore_index=True)

    def plot_gantt(
        self,
        annotation_cols=None,
        figsize=(12, 6),
        dpi=60,
        cluster_colors=None,
        row_height=0.6,
        row_gap=0.2,
        annotation_fontsize=8,
        axis_fontsize=12,
        title_fontsize=14,
        add_cluster_legend=True,
        save_path=None,
        curve_color="black",
        curve_linestyle="--",
        curve_linewidth=2.0,
        title="Patient Episodes Trajectory"
    ):
        """
        Plot the Gantt chart for patient episodes.

        Parameters
        ----------
        annotation_cols : list of str, optional
            Columns to annotate in each rectangle (first 2 are line 1, rest line 2).
        figsize : tuple
            (width, height) in inches for the figure.
        dpi : int
            Resolution (dots per inch).
        cluster_colors : list of str, optional
            List of colors for cluster indices (1-based). Missing => uses default.
        row_height : float
            Height of each episode bar.
        row_gap : float
            Vertical space between bars.
        annotation_fontsize : int
            Font size of annotation text.
        axis_fontsize : int
            Font size for axis labels.
        title_fontsize : int
            Font size for the plot title.
        add_cluster_legend : bool
            Whether to add a legend for cluster colors.
        save_path : str or None
            If provided, the figure is saved to this path (e.g., "myplot.png").
        curve_color : str
            Color for the line connecting episodes of the same patient.
        curve_linestyle : str
            Linestyle (e.g. "--") for the connecting line or spline.
        curve_linewidth : float
            Width for the connecting line.
        title : str
            Title of the plot.

        Returns
        -------
        (fig, ax) : (matplotlib.figure.Figure, matplotlib.axes._axes.Axes)
        """

        df = self.df
        pasient_col = self.pasient_col
        cluster_col = self.cluster_col
        start_date_col = self.start_date_col
        end_date_col = self.end_date_col

        if annotation_cols is None:
            annotation_cols = []

        # Default cluster colors
        if cluster_colors is None:
            cluster_colors = [
                "red", "green", "blue", "orange",
                "purple", "brown", "cyan", "magenta",
                "yellow", "pink", "olive", "teal"
            ]

        # Create figure and axes
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

        current_y = 0.0
        y_ticks = []
        y_tick_labels = []
        used_clusters = set()

        all_age_starts = []
        all_age_ends = []

        patient_centers = defaultdict(list)

        # Plot each row
        num_rows = len(df)
        for idx in range(num_rows):
            row = df.iloc[idx]
            patient_id = row[pasient_col]
            age_start = row["age_start"]
            age_end = row["age_end"]

            # Ensure minimal width
            width = age_end - age_start
            if width <= 0:
                width = 0.5

            all_age_starts.append(age_start)
            all_age_ends.append(age_start + width)

            # Cluster color
            cluster_val = row.get(cluster_col, np.nan)
            if pd.notnull(cluster_val):
                try:
                    cluster_idx = int(cluster_val) - 1
                except (ValueError, TypeError):
                    cluster_idx = -1
            else:
                cluster_idx = -1

            color = cluster_colors[cluster_idx] if 0 <= cluster_idx < len(cluster_colors) else "gray"
            if cluster_idx >= 0:
                used_clusters.add(cluster_idx)

            # Draw rectangle
            rect = patches.Rectangle(
                (age_start, current_y),
                width,
                row_height,
                facecolor=color,
                edgecolor="black",
                alpha=0.7
            )
            ax.add_patch(rect)

            # Center of bar
            center_x = age_start + width / 2.0
            center_y = current_y + row_height / 2.0
            patient_centers[patient_id].append((center_x, center_y))

            # Build annotation text (2 lines: first 2 columns => line1, rest => line2)
            line1_parts = []
            line2_parts = []
            for i, col in enumerate(annotation_cols):
                val = row.get(col, None)
                if pd.notnull(val):
                    entry = f"{col}: {val}"
                    if i < 2:
                        line1_parts.append(entry)
                    else:
                        line2_parts.append(entry)

            line1 = ", ".join(line1_parts)
            line2 = ", ".join(line2_parts)
            if line1 and line2:
                annotation_text = f"{line1}\n{line2}"
            elif line1:
                annotation_text = line1
            else:
                annotation_text = ""

            # Place text
            if annotation_text.strip():
                ax.text(
                    center_x + 0.5,
                    center_y,
                    annotation_text,
                    ha="left",
                    va="center",
                    fontsize=annotation_fontsize,
                    color="black",
                    bbox=dict(
                        boxstyle="round,pad=0.3",
                        facecolor="white",
                        edgecolor="none",
                        alpha=0.6
                    )
                )

            # Y-label
            episode_label = f"Pat {patient_id}, E{idx+1}"
            y_ticks.append(center_y)
            y_tick_labels.append(episode_label)

            # Advance
            current_y += (row_height + row_gap)

            # Dotted line if next row is a new patient
            if idx < (num_rows - 1):
                next_patient_id = df.iloc[idx+1][pasient_col]
                if next_patient_id != patient_id:
                    ax.axhline(
                        y=current_y,
                        color='gray',
                        linestyle=':',
                        linewidth=1.0,
                        alpha=0.8
                    )

        # Connect episodes (spline if SciPy, else piecewise)
        if HAS_SCIPY:
            for pid, centers in patient_centers.items():
                if len(centers) < 2:
                    continue
                centers_sorted = sorted(centers, key=lambda c: c[1])
                xs = [c[0] for c in centers_sorted]
                ys = [c[1] for c in centers_sorted]
                if len(xs) < 2:
                    continue
                k_spline = min(3, len(xs) - 1)
                if k_spline < 1:
                    continue
                y_new = np.linspace(ys[0], ys[-1], 150)
                spline = make_interp_spline(ys, xs, k=k_spline)
                x_smooth = spline(y_new)
                ax.plot(
                    x_smooth, y_new,
                    color=curve_color,
                    linestyle=curve_linestyle,
                    linewidth=curve_linewidth,
                    alpha=0.8
                )
        else:
            # piecewise fallback
            for pid, centers in patient_centers.items():
                if len(centers) < 2:
                    continue
                centers_sorted = sorted(centers, key=lambda c: c[1])
                xs = [c[0] for c in centers_sorted]
                ys = [c[1] for c in centers_sorted]
                ax.plot(
                    xs, ys,
                    color=curve_color,
                    linestyle=curve_linestyle,
                    linewidth=curve_linewidth,
                    alpha=0.8
                )

        # Configure axes
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_tick_labels, fontsize=axis_fontsize)

        if all_age_starts and all_age_ends:
            age_min = min(all_age_starts)
            age_max = max(all_age_ends)
            ax.set_xlim(age_min - 0.5, age_max + 0.5)
        else:
            ax.set_xlim(0, 1)

        ax.set_ylim(0, current_y)
        ax.set_xlabel("Age (Years)", fontsize=axis_fontsize)
        ax.set_ylabel("Patient Episodes", fontsize=axis_fontsize)
        ax.grid(True, axis="x", linestyle="--", alpha=0.5)

        ax.set_title(title, fontsize=title_fontsize, pad=20)

        # Optional cluster legend
        if add_cluster_legend and len(used_clusters) > 0:
            from matplotlib.lines import Line2D
            legend_elems = []
            for c_idx in sorted(used_clusters):
                c_label = f"Cluster {c_idx+1}"
                c_color = cluster_colors[c_idx]
                legend_elems.append(
                    Line2D([0], [0],
                           color=c_color,
                           marker='s', markersize=5,
                           linewidth=2, label=c_label, alpha=0.7)
                )
            ax.legend(
                handles=legend_elems,
                title="Clusters",
                fontsize=axis_fontsize,
                title_fontsize=axis_fontsize,
                loc='upper left',
                bbox_to_anchor=(1.05, 1)
            )

        fig.tight_layout()

        # Save if requested
        if save_path:
            fig.savefig(save_path, dpi=dpi, bbox_inches="tight")

        return fig, ax

