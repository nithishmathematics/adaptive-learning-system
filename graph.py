import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Updated data including hybrid model
models = ['LSTM', 'HMM', 'GMM', 'Kalman Filter', 'Fuzzy Logic', 'Monte Carlo', 'Hybrid Model']
accuracy = [0.86, 0.76, 0.78, 0.80, 0.74, 0.70, 0.90]

# Create a DataFrame for plotting
df_accuracy = pd.DataFrame({
    'Model': models,
    'Accuracy': accuracy
})

# Set plot style
sns.set(style="whitegrid")

# Plot the accuracy comparison including the hybrid model
plt.figure(figsize=(10, 6))
sns.barplot(x='Model', y='Accuracy', data=df_accuracy, palette='crest')
# plt.title('Accuracy Comparison of Cognitive State Models')
plt.ylim(0.65, 0.95)
plt.ylabel('Accuracy')
plt.xticks(rotation=45)
plt.tight_layout()
# plt.savefig('/mnt/data/accuracy_comparison_with_hybrid.png')
plt.show()

'/mnt/data/accuracy_comparison_with_hybrid.png'
