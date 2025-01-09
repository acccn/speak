import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker

def plot_timeline(timeline, output_path="timeline.png"):
    if not timeline:
        print("Timeline is empty. Skipping plot.")
        return None
    
    # 动态调整图片宽度，根据时间长度调整比例
    max_time = max([end for _, end, _ in timeline])
    fig_width = max(20, max_time / 10)  # 每100秒宽度设置为10个单位
    fig, ax = plt.subplots(figsize=(fig_width, 4))

    colors = {
        "01": "red",
        "02": "blue",
        "03": "green",
        "04": "orange",
        "05": "purple"
    }

    for start, end, speaker in timeline:
        color = colors.get(speaker, "gray")
        rect = mpatches.Rectangle((start, 0), end-start, 0.5, color=color)
        ax.add_patch(rect)

    # 设置x轴刻度
    ax.set_xlim(0, max_time + 5)
    ax.set_ylim(-0.2, 0.7)  # 调整y轴范围，使图形更靠近x轴
    ax.set_yticks([])
    ax.set_xlabel("Time (s)")
    ax.set_title("Speaker Timeline")

    # 动态调整x轴刻度的密度，最高精度1秒
    if max_time <= 60:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))  # 设置刻度间隔为1秒
    elif max_time <= 600:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(10))  # 设置刻度间隔为10秒
    else:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(30))  # 设置刻度间隔为30秒

    plt.savefig(output_path)
    plt.close()
    print(f"Timeline plot saved as '{output_path}'.")

    return output_path
