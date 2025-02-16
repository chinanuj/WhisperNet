from collections import defaultdict
import matplotlib.pyplot as plt

def analyze_degrees_plot():
    # Track latest degree for each peer
    latest_degrees = {}
    
    # Read the log file
    with open('freqtrack.log', 'r') as f:
        for line in f:
            peer_id, degree = line.strip().split('=>')
            latest_degrees[peer_id] = int(degree)

    # Calculate degree distribution
    degree_freq = defaultdict(int)
    for degree in latest_degrees.values():
        degree_freq[degree] += 1
    
    # Prepare data for plotting
    degrees = sorted(degree_freq.keys(), reverse=True)
    frequencies = [degree_freq[d] for d in degrees]
    
    # Create the visualization
    plt.figure(figsize=(12, 6))
    
    # Bar plot
    plt.bar(degrees, frequencies, color='steelblue', alpha=0.8)
    
    # Customize the plot
    plt.title('Network Degree Distribution', fontsize=14, pad=20)
    plt.xlabel('Degree', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    
    # Add grid for better readability
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Add statistics as text
    stats_text = (
        f"Total Peers: {len(latest_degrees)}\n"
        f"Average Degree: {sum(latest_degrees.values())/len(latest_degrees):.2f}\n"
        f"Maximum Degree: {max(latest_degrees.values())}\n"
        f"Minimum Degree: {min(latest_degrees.values())}"
    )
    
    # Position the stats box in the upper right
    plt.text(0.95, 0.95, stats_text,
             transform=plt.gca().transAxes,
             verticalalignment='top',
             horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Adjust layout to prevent text cutoff
    plt.tight_layout()
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    analyze_degrees_plot()