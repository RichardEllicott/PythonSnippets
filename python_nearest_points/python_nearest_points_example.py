from scipy.spatial import cKDTree
import numpy as np

# Initialize points
points = np.random.rand(1000, 3)  # 1000 random 3D points
tree = cKDTree(points)

# Function to add a new point and update the tree
def add_point(tree, points, new_point):
    points = np.vstack([points, new_point])  # Append new point
    return cKDTree(points), points  # Rebuild tree with updated points

# Add a new point
new_point = np.array([0.5, 0.5, 0.5])
tree, points = add_point(tree, points, new_point)

# Find nearest neighbor
query_point = np.array([0.5, 0.5, 0.5])
dist, idx = tree.query(query_point, k=1)
print(f"Nearest point: {points[idx]}, distance: {dist}")

# Find 5 nearest neighbors
distances, indices = tree.query(query_point, k=5)
print(f"5 nearest points:\n{points[indices]}\nDistances: {distances}")