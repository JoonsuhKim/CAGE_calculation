import matplotlib.pyplot as plt
import pandas as pd

def plot_bubble_chart(head, size_attr='CLS', title='Bubble Chart', color='skyblue', industry='apparel'):
    cur = head
    x_vals, y_vals, sizes, labels = [], [], [], []

    while cur:
        if cur.ISO == 'KOR':
            cur = cur.next
            continue
        x_vals.append(cur.x_axis / 1000)
        y_vals.append(cur.y_axis)
        size_value = getattr(cur, size_attr)
        sizes.append(1 if pd.isna(size_value) or size_value <= 0 else size_value * 75)
        labels.append(cur.ISO)
        cur = cur.next

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(x_vals, y_vals, s=sizes, alpha=0.7, color=color, edgecolors='black')
    for i in range(len(labels)):
        ax.text(x_vals[i], y_vals[i], labels[i], fontsize=max(8, sizes[i] / 500), ha='center', va='center')

    ylim_dict = {'automotive': 3000, 'electronics': 800}
    ax.set_xlim(0, 100)
    ax.set_ylim(0, ylim_dict.get(industry, 1500))
    ax.set_xlabel("per capita GDP ($K)", fontsize=12)
    ax.set_ylabel(f"per capita {industry} consumption ($)", fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(False)
    plt.tight_layout()
    return fig
