from ruamel.yaml import YAML
from glob import glob
from pathlib import Path

yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 4096

changed_datasets = []

for metadata_file in glob("*/metadata.yaml"):
    with open(metadata_file, "r") as f:
        metadata = yaml.load(f)

    for observable in metadata["implemented_observables"]:
        variants = observable.get("variants", {})
        legacy = variants.get("legacy", {})
        if "theory" in legacy:
            legacy_data = dict(legacy)
            legacy_theory = {"theory": legacy_data.pop("theory")}

            # Not all will have both legacy data and theory, in those cases skip
            if not legacy_data:
                continue
            variants["legacy_data"] = legacy_data
            variants["legacy_theory"] = legacy_theory

            changed_datasets.append(
                f"{Path(metadata_file).parent.name}_{observable['observable_name']}"
            )

    with open(metadata_file, "w") as f:
        yaml.dump(metadata, f)

print("\n".join(changed_datasets))
