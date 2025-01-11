import xml.etree.ElementTree as ET


def get_asset_paths_from_mjcf(xml_file_path):
    """
    Parses the MJcF XML file and extracts all asset paths into a list.

    Args:
    xml_file_path (str): Path to the MJcF XML file.

    Returns:
    list: A list of asset paths found in the XML file.
    """
    try:
        # Parse the XML file
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # List to store asset paths
        asset_paths = []

        # Loop through the 'asset' nodes and collect file paths
        for asset in root.iter("asset"):
            for child in asset:
                # Check for the 'file' attribute (usually used for paths in assets)
                file_path = child.attrib.get("file")
                if file_path:
                    asset_paths.append(file_path)

        return asset_paths

    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        return []
    except FileNotFoundError:
        print("File not found. Please provide a valid file path.")
        return []


if __name__ == "__main__":
    # Example usage
    # Replace 'example_mjcf.xml' with the path to your MJcF XML file
    xml_file_path = "../../../assets/robocasa_scenes/layout0000-style0000.xml"
    asset_paths = get_asset_paths_from_mjcf(xml_file_path)

    if asset_paths:
        print("Asset paths found in the MJcF file:")
        for asset in asset_paths:
            print(asset)
    else:
        print("No asset paths found or an error occurred.")