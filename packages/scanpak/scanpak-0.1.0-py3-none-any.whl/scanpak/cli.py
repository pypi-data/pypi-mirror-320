import sys

import argparse
import requests
import tabulate


class CVEData:
    def __init__(self, 
                 cve_id: str, 
                 cve_alias: list, 
                 description: str):
        self.cve_id = cve_id
        self.cve_alias = cve_alias
        self.description = description

    # use tabulate to print the data in a table

    def get_cve_id(self):
        return self.cve_id

    def get_cve_alias(self):
        return self.cve_alias

    def get_description(self):
        # return the first sentence of the description
        if not self.description:
            return "No description available"

        if len(self.description) < 40:
            return self.description.split("\n")[0]

        # there is a \n in the description, split by \n and return 
        # the first sentence
        if "\n" in self.description:
            return self.description.split("\n")[1].split(". ")[0]
        if "\n" in self.description[:40]:
            return self.description.split("\n")[1]

        return self.description


def get_vulnerabilities(package_name, package_version):
    """
    get the vulnerabilities for python 
    package from PyPI API
    """

    url = f"https://pypi.org/pypi/{package_name}/{package_version}/json"

    # now fetch vulnerabilities
    response = requests.get(url)

    vulnerability_ids = []

    for i in response.json().get('vulnerabilities'):
        vulnerability_ids.append(i.get('id'))

    return vulnerability_ids


def parse_package_arg(package):
    """
    take a package argument and parse it
    if there is a version specified, return
    the package name and the version
    """

    if "==" in package:
        return package.split("==")
    else:
        # get the latest version from pypi
        url = f"https://pypi.org/pypi/{package}/json"
        response = requests.get(url)
        if response.json().get('message') == "Not Found":
            print(f"Package {package} not found in PyPI")
            sys.exit(1)
        if response.status_code != 200:
            print("Request unsuccessful, exiting...")
            sys.exit(1)
        version = response.json().get("info").get("version")

        if not version:
            print("could not find version from the PyPI API, please provide \
                a version")
            sys.exit(1)

        # return the package and package version
        return package, version


def query_osv(cve_id):
    url = f"https://api.osv.dev/v1/vulns/{cve_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error occurred while getting info about {cve_id}")
        sys.exit(1)


def print_vuln_info(package):
    package_name, parsed_version = parse_package_arg(package)
    print(f"Package name: {package_name}")
    print(f"Package version: {parsed_version}")

    vuln_ids = get_vulnerabilities(package_name, parsed_version)

    # store the cve data
    cve_data = []

    # get vulnerability for each id
    for id in vuln_ids:
        r = query_osv(id)
        cve = CVEData(cve_id=r.get('id'),
                      cve_alias=r.get('aliases'),
                      description=r.get('details'))
        cve_data.append([
            cve.get_cve_id(),
            cve.get_cve_alias(),
            cve.get_description()[:80] + "..."
        ])

    print(printAllCVEData(cve_data))

    
def printAllCVEData(cve_data):
    # return a string representation of the data
    headers = ["CVE ID", "CVE Alias", "Description"]
    return tabulate.tabulate(cve_data, headers=headers, tablefmt="fancy_grid")


def main():
    parser = argparse.ArgumentParser(description="Scan a python package for vulnerabilities")
    parser.add_argument("package", help="The package to scan")
    args = parser.parse_args()
    print_vuln_info(args.package)


if __name__ == "__main__":
    main()
