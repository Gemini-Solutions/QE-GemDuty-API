import getpass
import os
from logger import logger

current_directory = os.getcwd()
JAVA_ROOT=os.path.join(current_directory, "NextGen") 
JAVA_ROOT_IMP=os.path.join(current_directory, "NextGen\\src\\test\\java\\implementation\\Implementation.java") 
JAVA_ROOT_LOC=os.path.join(current_directory, "NextGen\\src\\test\\java\\locators\\Locators.java") 
JAVA_ROOT_STD=os.path.join(current_directory, "NextGen\\src\\test\\java\\stepdefinitions\\StepDefinition.java") 
JAVA_ROOT_FT=os.path.join(current_directory, "NextGen\\src\\test\\resources\\features\\FeatureFile.feature") 

def testrunner_content():
    return ("""
package testrunners;

import io.cucumber.junit.Cucumber;
import org.junit.runner.RunWith;
import io.cucumber.junit.CucumberOptions;

@RunWith(Cucumber.class)
@CucumberOptions(
        features = "src/test/resources/features",
        glue = {"stepdefinitions"},
        plugin = {"pretty", "html:Results/reports.html"}
)
public class TestRunner {
}
    """
    )

# TODO : update the xml content if required
def xml_content():
    return ("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.qa</groupId>
    <artifactId>pimco-demo</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <!-- https://mvnrepository.com/artifact/org.seleniumhq.selenium/selenium-java -->
        <dependency>
            <groupId>org.seleniumhq.selenium</groupId>
            <artifactId>selenium-java</artifactId>
            <version>4.22.0</version>
        </dependency>

        <!-- https://mvnrepository.com/artifact/io.cucumber/cucumber-java -->
        <dependency>
            <groupId>io.cucumber</groupId>
            <artifactId>cucumber-java</artifactId>
            <version>7.18.0</version>
        </dependency>

        <!-- https://mvnrepository.com/artifact/io.cucumber/cucumber-junit -->
        <dependency>
            <groupId>io.cucumber</groupId>
            <artifactId>cucumber-junit</artifactId>
            <version>7.18.0</version>
            <scope>test</scope>
        </dependency>


        <!-- https://mvnrepository.com/artifact/com.aventstack/extentreports -->
        <dependency>
            <groupId>com.aventstack</groupId>
            <artifactId>extentreports</artifactId>
            <version>5.1.2</version>
        </dependency>

        <!-- https://mvnrepository.com/artifact/io.github.bonigarcia/webdrivermanager -->
        <dependency>
            <groupId>io.github.bonigarcia</groupId>
            <artifactId>webdrivermanager</artifactId>
            <version>5.9.1</version>
        </dependency>

    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
                <configuration>
                    <source>1.8</source>
                    <target>1.8</target>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>2.22.2</version>
            </plugin>
        </plugins>
    </build>

</project>
""")




content_generators = {
    'java' : testrunner_content, 
    'xml': xml_content
}

def create_new_file(file_type, folder_path, file_name):
    file_name_without_ext = os.path.splitext(file_name)[0]
    file_extension = file_type.lower()

    os.makedirs(folder_path, exist_ok=True)

    # Check if the file type is supported
    if file_extension in content_generators:
        file_path = os.path.join(folder_path, f'{file_name_without_ext}.{file_extension}')
        with open(file_path, 'w') as file:
            # if file_extension in ['xml', 'yml']:
            #     content = content_generators[file_extension]()
            # else:
            content = content_generators[file_extension]()
            file.write(content)
        #print(f"{file_extension} file '{file_name}' created successfully in '{folder_path}'!")
    else:
        logger.info(f"{file_extension} Unsupported file type. Please choose a correct file type!")


def create_project_structure(project_name):
    
    project_path = project_name

    try:
        if not os.path.exists(project_path):
            os.mkdir(project_path)
            logger.info(f"Project '{project_name}' created")
        else:
            logger.info(f"The directory '{project_name}' already exists.")
# TODO : remove the files which are not required 
        files_to_create = [
            ("xml", project_path, "pom.xml"),
            ("java", os.path.join(project_path, "src/main/java/org/example"), "Main.java"),
            ("java", os.path.join(project_path, "src/test/java/locators"), "Locators.java"),
            ("java", os.path.join(project_path, "src/test/java/implementation"), "Implementation.java"),
            ("java", os.path.join(project_path, "src/test/java/testrunners"), "TestRunner.java"),
            ("java", os.path.join(project_path, "src/test/java/stepdefinitions"), "StepDefinition.java"),
            ("java", os.path.join(project_path, "src/test/java/stepdefinitions"), "Hook.java"),
            ("feature", os.path.join(project_path, "src/test/resources/features"), "FeatureFile.feature"),
            ("java", os.path.join(project_path, "Results"), "report.html"),
            ("xml", os.path.join(project_path, "src/test"), "testng.xml")
        ]

        # Create files
        for file_type, folder_path, file_name in files_to_create:
            create_new_file(file_type, folder_path, file_name)

    except Exception as e:
        logger.info(f"An error occurred: {e}")
        
        
        
if __name__ == "__main__":
    # Create the project
    create_project_structure("NextGen")