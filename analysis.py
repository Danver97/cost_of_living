import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('cities.csv')

extra_eu = ['US', 'CA', 'AU']
other_east_eu = ['RO', 'CZ', 'SK', 'IS']
countries_to_exclude = extra_eu + other_east_eu

df = df[~df['country'].isin(countries_to_exclude)]

df = df.reset_index(drop=True)

print(df.columns)

df['total_cost_centre'] = df['base_cost_of_living'] + df['one_bedroom_rent_centre']
df['avg_savings_centre'] = df['avg_net_salary'] - df['total_cost_centre']
df['avg_savings_rate_centre'] = df['avg_savings_centre'] / df['avg_net_salary']
df['avg_squared_meters_earned_centre'] = df['avg_net_salary'] / df['price_per_squared_meter_centre']
df['avg_squared_meters_saved_centre'] = df['avg_savings_centre'] / df['price_per_squared_meter_centre']
df['total_cost_outside_centre'] = df['base_cost_of_living'] + df['one_bedroom_rent_outside_centre']
df['avg_savings_outside_centre'] = df['avg_net_salary'] - df['total_cost_outside_centre']
df['avg_savings_rate_outside_centre'] = df['avg_savings_outside_centre'] / df['avg_net_salary']
df['avg_squared_meters_earned_outside_centre'] = df['avg_net_salary'] / df['price_per_squared_meter_outside_centre']
df['avg_squared_meters_saved_outside_centre'] = df['avg_savings_outside_centre'] / df['price_per_squared_meter_outside_centre']

df = df.sort_values(by='avg_savings_rate_centre', ascending=False)
df = df.reset_index(drop=True)

def group_by_country(df: pd.DataFrame) -> pd.DataFrame:
    # We want a weighted average. I.e. if we have fewer entries from a city, we want that city to count less.
    # We initally multiply each city's stats by the number of entries
    # We group and sum, and then we compute the average stats by dividing by the summed entries
    grouped = df.copy().drop('city', axis=1)

    # Compute weighted stats
    grouped['weighted_avg_net_salary'] = grouped['avg_net_salary'] * grouped['entries']
    grouped['weighted_total_cost_centre'] = grouped['total_cost_centre'] * grouped['entries']
    grouped['weighted_total_cost_outside_centre'] = grouped['total_cost_outside_centre'] * grouped['entries']
    # Sum
    grouped = grouped.groupby('country', as_index=False).sum()
    # Compute averages from weighted summed stats
    grouped['avg_net_salary'] = grouped['weighted_avg_net_salary'] / grouped['entries']
    grouped['total_cost_centre'] = grouped['weighted_total_cost_centre'] / grouped['entries']
    grouped['total_cost_outside_centre'] = grouped['weighted_total_cost_outside_centre'] / grouped['entries']

    grouped['avg_savings_rate_centre'] = 1 - (grouped['total_cost_centre'] / grouped['avg_net_salary'])
    grouped['avg_savings_rate_outside_centre'] = 1 - (grouped['total_cost_outside_centre'] / grouped['avg_net_salary'])

    grouped = grouped.drop(['weighted_avg_net_salary', 'weighted_total_cost_centre', 'weighted_total_cost_outside_centre'], axis=1)

    
    grouped = grouped.sort_values(by='avg_savings_rate_centre', ascending=False)
    grouped = grouped.reset_index(drop=True)
    
    return grouped

country_grouped = group_by_country(df)
print(country_grouped)

print(df[df['country'] == 'IT'])

# Generate a color map for unique values in the 'country' column
unique_colors = np.unique(df['country'])
color_map = plt.cm.get_cmap('tab20', len(unique_colors))  # Use tab20 colormap for up to 20 unique colors

def subplot_data(data: pd.DataFrame, ax, plot_title: str, x_metric_name: str, xlabel: str, annotation_column: str = None) -> None:
    for i, color in enumerate(unique_colors):
        mask = (data['country'] == color)
        ax.scatter(data[x_metric_name][mask], data['avg_net_salary'][mask], color=color_map(i), label=color)
    
    if annotation_column is not None:
        # Annotates each data point with the label contained under annotation_column
        for x, y, label in zip(data[x_metric_name], data['avg_net_salary'], data[annotation_column]):
            ax.annotate(label, (x, y), textcoords="offset points", xytext=(0,4), ha='center', fontsize=5)

    ax.axvline(x=0, color='red', linestyle='--')  # Set a red line indicating the threshold under which it's not possible to save anything
    ax.set_title(plot_title)  # Set the title of the subplot
    ax.set_xlabel(xlabel)  # Set the label for the x-axis
    ax.set_ylabel('Salary')  # Set the label for the y-axis
    ax.legend(title='Countries')  # Display legend
    ax.grid(True)  # Display grid

def plot_data(data: pd.DataFrame, plot_title: str, metric_name: str, metric_label: str, annotation_column: str = None) -> None:
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(16, 6))

    city_centre_metric_name = metric_name + '_centre'
    outside_city_centre_metric_name = metric_name + '_outside_centre'

    subplot_data(data, ax1, 'City center', city_centre_metric_name, metric_label, annotation_column=annotation_column)
    subplot_data(data, ax2, 'Outside city center', outside_city_centre_metric_name, metric_label, annotation_column=annotation_column)

    fig.suptitle(plot_title)  # Set the title of the plot

plot_data(df, 'Savings Rate vs Avg Salary (Cities)', 'avg_savings_rate', 'Savings Rate')
plot_data(country_grouped, 'Savings Rate vs Avg Salary (Countries)', 'avg_savings_rate', 'Savings Rate')
plot_data(df, 'Home Price vs Avg Salary (Cities)', 'avg_squared_meters_earned', 'Avg m2 earned (per month)')
plot_data(df, 'Home Price vs Avg Savings (Cities)', 'avg_squared_meters_saved', 'Avg m2 saved (per month)')

plt.show()
