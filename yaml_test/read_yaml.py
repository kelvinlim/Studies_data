import yaml

file = 'yaml_test/test.yaml'

with open(file, 'r') as f:
    data = yaml.safe_load(f)

# what are the column names?
print("Column names:")
print(data.keys())

# print the description for each column
for col, info in data.items():
    print(f"\n{info['label']}:")
    print(info['desc'])

