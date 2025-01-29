GREETING_REPLY_PROMPT="""
Greetings From QANextGen!
NextGen is a project focused on developing and validating an AI-powered solution for automatic test case generation using Large Language Models (LLMs). This initiative is part of our ongoing efforts to integrate advanced AI technologies into our Quality Engineering (QE) processes.
Please consider putting a relevant query for the application, Thanks!
"""

SIMPLE_INSTRUCTIONS_REPLY_PROMPT="""
The instructions provided by you are too simple for me to understand, the instructions lack {missing_params} due to which they cannot be converted into relevant test cases, hence provide more context about the {missing_params} in your instructions.
"""