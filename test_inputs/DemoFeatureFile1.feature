Feature: Test Basic Features of Athena web application
  Background: Check login to candidate module
    And Navigate to login page at https://athena.geminisolutions.com/login
    And Login using "akshay.katiha@geminisolutions.com" and "Akshay@12"
    And redirect to landing page url https://athena.geminisolutions.com/app/candidate/courses

  @regression
  Scenario Outline: Verify course metrics on landing page
    Given User is on landing page
    Then Verify "<tab1>", "<tab2>", "<tab3>" and "<tab4>" are visible
    And verify user has completed more than 1 course
    And also verify that total training time is more than 30 min
    Examples:
      |tab1         |tab2             |tab3           |tab4               |
      |Total Courses|Completed Courses|Ongoing Courses|Total Training Time|

  @regression
  Scenario Outline : Verify the number of courses in each tab
    Given User is on landing page
    Then Verify "<tab1>", "<tab2>", "<tab3>" are visible
    When user clicks on "<tab1>" courses tab
    Then all "<tab1>" courses should be visible
    When user clicks on "<tab2>" courses tab
    Then all "<tab2>" courses should be visible
    When user clicks on "<tab3>" courses tab
    Then all "<tab3>" courses should be visible
    Examples:
      |tab1         |tab2             |tab3           |
      |Ongoing      |Completed        |Expired        |