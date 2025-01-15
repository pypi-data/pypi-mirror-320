A Python package to load, transform, and visualize patient trajectories for one or many patients.  
It handles missing values gracefully, allows you to rename or drop columns,  
and lets you annotate the plotted trajectories with any additional fields.

## Usage Example

```

"""
This script demonstrates the usage of the `PatientTrajectoryVisualizer` to create Gantt
charts for visualizing patient trajectories.

Key Features:
- Customizable figure size and resolution.
- Annotated patient episodes with optional cluster legends.
- Flexible annotation options for additional insights.

Dependencies:
- pandas
- matplotlib
- PatientTrajectoryVisualizer (import from `patient_trajectory.visualization`)

"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from patient_trajectory.visualization import PatientTrajectoryVisualizer

# Sample DataFrame with patient trajectory data
df = pd.DataFrame({
    "pasient": [
        1, 1, 1, 2, 2, 3, 4, 4, 5, 6,
        7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
        17, 18, 19, 20, 21
    ],
    "episode_start_date": [
        "2001-01-01", "2002-03-20", "2003-10-05", "2005-05-01", "2005-06-15",
        "2010-01-01", "2018-08-20", "2019-02-02", "2020-01-01", "2020-05-15",
        "2021-07-10", "2021-12-01", "2022-03-14", "2023-01-01", "2023-04-10",
        "2023-06-15", "2023-08-01", "2023-09-12", "2024-01-01", "2024-03-15",
        "2025-01-01", "2025-02-15", "2025-03-20", "2025-05-10", "2025-07-01"
    ],
    "episode_end_date": [
        "2001-02-15", "2002-06-01", "2004-01-10", "2005-05-10", None,
        "2010-01-05", "2019-01-01", None, "2020-02-01", "2020-06-01",
        None, "2022-01-10", "2022-04-01", "2023-02-15", "2023-05-05",
        None, "2023-08-20", None, "2024-02-01", None,
        "2025-01-10", None, "2025-04-01", None, None
    ],
    "age": [
        10, 11, 12, 35, 36,
        75, 5, 6, 45, 30,
        25, 28, 33, 20, 22,
        18, 40, 50, 60, 65,
        27, 55, 78, 42, 24
    ],
    "cluster": [
        1, np.nan, 2, 2, 3,
        3, 1, np.nan, 5, 5,
        np.nan, 5, 2, 6, np.nan,
        6, 4, 3, 4, np.nan,
        3, 1, 5, 2, 4
    ],
    "diagnosis": [
        None, "Flu", "Migraine", "COVID", None,
        "Cold", "Broken Bone", "Follow-up", "Diabetes", "Asthma",
        "Hypertension", "Obesity", "Depression", "Anxiety", None,
        "Migraine", "Arthritis", "Pneumonia", "Stroke", None,
        "Allergy", "Hypertension", "Cold", "COVID", "Broken Bone"
    ],
    "medication": [
        "MedA", None, "MedB", "MedC", "MedD",
        None, "MedX", None, "MedE", "MedF",
        "MedG", None, "MedH", "MedI", "MedJ",
        None, "MedK", "MedL", "MedM", None,
        "MedN", None, "MedO", "MedP", "MedQ"
    ],
    "insurance": [
        "Public", "Private", "Public", None, "None",
        "Public", "Private", "Public", "Public", "Private",
        "None", "Public", "Private", "Public", "None",
        "Public", "Private", "Public", "None", "Public",
        "Public", "Private", "None", "Public", "Public"
    ],
    "gender": [
        "M", "F", "M", "F", "F",
        "M", "M", "F", "F", "M",
        "M", "F", "F", "M", "F",
        "M", "F", "F", "M", "F",
        "M", "F", "M", "F", "M"
    ],
    "marital_status": [
        "Single", "Single", "Single", "Married", "Married",
        "Widowed", "Single", "Single", "Married", "Single",
        "Single", "Married", "Single", "Married", "Single",
        "Single", "Married", "Divorced", "Married", "Single",
        "Single", "Married", "Widowed", "Married", "Single"
    ],
    "blood_type": [
        "O+", "A+", "B+", "O-", "AB+",
        "A-", "B+", "O+", "A+", "AB+",
        "O-", "B-", "A+", "O+", "A-",
        "B+", "AB-", "B-", "O+", "A+",
        "O-", "A+", "AB+", "B-", "A-"
    ],
    "allergies": [
        None, None, "Peanuts", None, None,
        "Gluten", None, "Seafood", None, None,
        None, None, "Lactose", None, "Peanuts",
        None, "Seafood", None, "Bee stings", None,
        "Pollen", None, "Penicillin", "None", None
    ],
    "height_cm": [
        140, 145, 150, 170, 172,
        160, 110, 112, 175, 180,
        165, 168, 174, 169, 155,
        178, 185, 182, 177, 163,
        170, 165, 155, 172, 176
    ]
})

# Instantiate the visualizer
viz = PatientTrajectoryVisualizer(df=df)

# Create a Gantt chart with customizable options
fig, ax = viz.plot_gantt(
    annotation_cols=[
        "diagnosis", "medication", "insurance", "gender", "marital_status",
        "blood_type", "allergies", "height_cm"
    ],  # Columns to annotate in rectangles (first two are in line 1, others in line 2)
    figsize=(28, 12),  # Figure size (width, height) in inches
    dpi=120,  # Resolution (dots per inch)
    row_height=0.7,  # Height of each episode bar
    row_gap=0.3,  # Vertical space between bars
    annotation_fontsize=8,  # Font size of annotation text
    axis_fontsize=10,  # Font size for axis labels
    title_fontsize=14,  # Font size for the chart title
    add_cluster_legend=True,  # Whether to include a cluster legend
    curve_color="blue",  # Color of the connecting curve
    curve_linestyle="--",  # Line style for the curve
    curve_linewidth=1.5  # Line width for the curve
)

# Display the plot
plt.show()


```

## Citation

If you use this work, please cite:

```bibtex
@inproceedings{Pant2024,
  author    = {Pant, D. and Koochakpour, K. and Westbye, O. S. and Clausen, C. and Leventhal, B. L. and Koposov, R. and Rost, T. B. and Skokauskas, N. and Nytro, O.},
  title     = {Visualizing Patient Trajectories and Disorder Co-occurrences in Child and Adolescent Mental Health},
  booktitle = {2024 IEEE International Conference on Bioinformatics and Biomedicine (BIBM)},
  publisher = {IEEE Computer Society},
  pages     = {5531--5538},
  year      = {2024},
  month     = {Dec 1}
}
```
