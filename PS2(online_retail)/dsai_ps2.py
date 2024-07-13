# -*- coding: utf-8 -*-
"""CapstoneDSAI_PS2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1JxvYB9Sk9vn4qULoVQeepFi0sEVbM8RT

## Data Preprocessing and Insights
"""

import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

# Load the data, specifying the correct encoding
online_retail_data = pd.read_csv('/content/online_retail.csv', encoding='latin1')

df=online_retail_data

df.head()

df.info()

df.describe()

df.isnull().sum()

# Drop rows with missing CustomerID
online_retail_data.dropna(subset=['CustomerID'], inplace=True)

# Create TotalPrice column
online_retail_data['TotalPrice'] = online_retail_data['Quantity'] * online_retail_data['UnitPrice']

online_retail_data.head()

# Convert InvoiceDate to datetime
online_retail_data['InvoiceDate'] = pd.to_datetime(online_retail_data['InvoiceDate'])

# Sales trends
sales_trend = online_retail_data.groupby(online_retail_data['InvoiceDate'].dt.date)['TotalPrice'].sum()
sales_trend.plot(figsize=(12, 6))
plt.title('Sales Trend Over Time')
plt.xlabel('Date')
plt.ylabel('Total Sales')
plt.show()

# Most popular products
popular_products = online_retail_data.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(10)
print(popular_products)

# Top customers
top_customers = online_retail_data.groupby('CustomerID')['TotalPrice'].sum().sort_values(ascending=False).head(10)
print(top_customers)

# Country sales
country_sales = online_retail_data.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False).head(10)
print(country_sales)





"""## Customer Segmentation"""

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Reference date for recency calculation
reference_date = online_retail_data['InvoiceDate'].max() + dt.timedelta(days=1)

# RFM calculation
rfm = online_retail_data.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency
    'InvoiceNo': 'nunique',  # Frequency
    'TotalPrice': 'sum'  # Monetary
}).reset_index()

rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

rfm

# Normalize RFM values
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])

# Determine optimal number of clusters using the elbow method
wcss = []
for i in range(1, 11):
    kmeans = KMeans(n_clusters=i, random_state=42)
    kmeans.fit(rfm_scaled)
    wcss.append(kmeans.inertia_)

plt.plot(range(1, 11), wcss)
plt.title('Elbow Method')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')
plt.show()

# Apply K-Means clustering
optimal_clusters = 4
kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)

# Analyze clusters
cluster_analysis = rfm.groupby('Cluster').mean()
print(cluster_analysis)



"""### CLV Segmentation

Customer Lifetime Value (CLV) estimates the total revenue a business can reasonably expect from a single customer account throughout their relationship with the company.

Method:

Calculate the average purchase value.
Determine the average purchase frequency rate.

Compute the customer value.

Calculate the average customer lifespan.

Derive the CLV by multiplying these metrics.
"""

# Average Purchase Value
online_retail_data['TotalPrice'] = online_retail_data['Quantity'] * online_retail_data['UnitPrice']
customer_value = online_retail_data.groupby('CustomerID')['TotalPrice'].sum() / online_retail_data.groupby('CustomerID')['InvoiceNo'].nunique()

# Average Purchase Frequency Rate
purchase_frequency = online_retail_data.groupby('CustomerID')['InvoiceNo'].nunique() / len(online_retail_data['InvoiceDate'].unique())

# Customer Value
customer_value = purchase_frequency * customer_value

# Average Customer Lifespan
customer_lifespan = online_retail_data.groupby('CustomerID')['InvoiceDate'].apply(lambda x: (x.max() - x.min()).days / 365)

# Customer Lifetime Value
clv = customer_value * customer_lifespan

# Combine into DataFrame
clv_df = pd.DataFrame({'CustomerID': clv.index, 'CLV': clv.values})
print(clv_df.head())



"""### Behavioral Segmentation

Behavioral segmentation divides customers based on their behavior, such as purchasing habits, user status, or feedback. This method often uses a combination of transactional, usage, and engagement data.

Method:

Identify key behavioral attributes (e.g., purchase frequency, types of products bought, return rate).

Use clustering algorithms to segment customers based on these attributes.
"""

# Define key behavioral attributes
behavioral_data = online_retail_data.groupby('CustomerID').agg({
    'Quantity': 'sum',
    'InvoiceNo': 'nunique',
    'TotalPrice': 'sum'
}).reset_index()

# Apply clustering (e.g., K-Means)
from sklearn.cluster import KMeans

kmeans_behavioral = KMeans(n_clusters=3, random_state=42)
behavioral_data['BehavioralCluster'] = kmeans_behavioral.fit_predict(behavioral_data[['Quantity', 'InvoiceNo', 'TotalPrice']])

print(behavioral_data.head())



"""### Hierarchical Clustering

Hierarchical clustering creates a tree-like structure (dendrogram) to represent nested clusters. It can be agglomerative (bottom-up) or divisive (top-down).
"""

from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

# Compute linkage matrix
Z = linkage(rfm_scaled, method='ward')

# Plot the dendrogram
plt.figure(figsize=(10, 7))
dendrogram(Z)
plt.show()

# Determine clusters
hierarchical_clusters = fcluster(Z, t=3, criterion='maxclust')
rfm['HierarchicalCluster'] = hierarchical_clusters

rfm



"""### DBSCAN

DBSCAN (Density-Based Spatial Clustering of Applications with Noise) groups points that are closely packed together and marks points in low-density regions as outliers.
"""

from sklearn.cluster import DBSCAN

# Apply DBSCAN
dbscan = DBSCAN(eps=0.5, min_samples=5)
rfm['DBSCANCluster'] = dbscan.fit_predict(rfm_scaled)

rfm['DBSCANCluster'].value_counts()



"""### Agglomerative Clustering

Agglomerative clustering is a type of hierarchical clustering that starts with individual points as clusters and merges the closest pairs until all points are in one cluster.
"""





"""### GMM

Gaussian Mixture Models (GMM) assumes that the data is generated from a mixture of several Gaussian distributions, each representing a cluster.
"""

from sklearn.mixture import GaussianMixture

# Apply Gaussian Mixture Model
gmm = GaussianMixture(n_components=3, random_state=42)
rfm['GMMCluster'] = gmm.fit_predict(rfm_scaled)

rfm['GMMCluster'].value_counts()



"""### Spectral Clustering

Spectral clustering uses the eigenvalues of the similarity matrix to reduce dimensions and then applies clustering.
"""

from sklearn.cluster import SpectralClustering

# Apply Spectral Clustering
spectral = SpectralClustering(n_clusters=8, random_state=42)
rfm['SpectralCluster'] = spectral.fit_predict(rfm_scaled)

rfm['SpectralCluster'].value_counts()



"""## Saving the Model"""

import pickle

# Save the scaler and k-means model
with open('scaler.pkl', 'wb') as file:
    pickle.dump(scaler, file)

with open('kmeans.pkl', 'wb') as file:
    pickle.dump(kmeans, file)

