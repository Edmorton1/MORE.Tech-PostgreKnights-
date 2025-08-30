import os

for dirpath, _, filenames in os.walk("."):
	for filename in filenames:
		if filename.endswith(".py"):
			filepath = os.path.join(dirpath, filename)
			with open(filepath, "r", encoding="utf-8") as f:
				content = f.read()
			content = content.replace("	", "\t")
			with open(filepath, "w", encoding="utf-8") as f:
				f.write(content)
