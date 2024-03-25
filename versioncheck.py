import pkg_resources

def check_package_versions():
    # List of required packages and their versions
    required_packages = {
        'PyQt5': '>=5.15.4',
        'easyocr': '>=1.5.1',
        'googletrans': '>=4.0.0',
        'Pillow': '>=9.0.0',
        'pyautogui': '>=0.9.52',
    }

    # Check installed package versions
    for package_name, version_spec in required_packages.items():
        try:
            package_version = pkg_resources.get_distribution(package_name).version
            if pkg_resources.parse_version(package_version) < pkg_resources.parse_version(version_spec):
                print(f"{package_name}: Installed version {package_version} does not meet the requirement {version_spec}")
            else:
                print(f"{package_name}: OK ({package_version})")
        except pkg_resources.DistributionNotFound:
            print(f"{package_name}: Not installed")

if __name__ == "__main__":
    check_package_versions()