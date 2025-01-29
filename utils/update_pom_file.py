import xml.etree.ElementTree as ET

def add_dependency_to_pom(pom_file, new_dependency_xml):
    # Register namespace to preserve the existing formatting and namespace attributes
    ET.register_namespace('', "http://maven.apache.org/POM/4.0.0")
    ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")

    # Parse the existing pom.xml file
    tree = ET.parse(pom_file)
    root = tree.getroot()
    ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}
    # Parse the new dependency XML string
    new_dependency = ET.fromstring(new_dependency_xml)

    # Get the dependencies node
    dependencies = root.find('{http://maven.apache.org/POM/4.0.0}dependencies')
    if dependencies is None:
        dependencies = ET.SubElement(root, 'dependencies')

  # Check if dependency already exists
    exists = False
    for dep in dependencies.findall('maven:dependency', namespaces=ns):
        dep_group_id = dep.find('maven:groupId', namespaces=ns)
        dep_artifact_id = dep.find('maven:artifactId', namespaces=ns)
        new_group_id = new_dependency.find('maven:groupId', namespaces=ns)
        new_artifact_id = new_dependency.find('maven:artifactId', namespaces=ns)
        
        # Ensure elements found before comparing texts
        if (dep_group_id is not None and new_group_id is not None and
            dep_group_id.text == new_group_id.text and
            dep_artifact_id is not None and new_artifact_id is not None and
            dep_artifact_id.text == new_artifact_id.text):
            exists = True
            break


    # Append the new dependency if not exists
    if not exists:
        dependencies.append(new_dependency)
        tree.write(pom_file, encoding='utf-8', xml_declaration=True)
        print("Dependency added successfully.")
    else:
        print("Dependency already exists.")

# Specify the dependency XML as a string
dependency_xml = '''
<dependency>
    <groupId>io.newtest</groupId>
    <artifactId>test-dependency-new</artifactId>
    <version>1.1.0</version>
    <scope>testing the scope</scope>
</dependency>
'''

if __name__ == "__main__":
# Call the function to update the pom.xml   
    add_dependency_to_pom('NextGen\pom.xml', dependency_xml)
