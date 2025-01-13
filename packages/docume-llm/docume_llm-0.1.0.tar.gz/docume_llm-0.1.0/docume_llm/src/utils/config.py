from enum import Enum

class ApplicationType(Enum):
    JIRA = 'jira'
    TRELLO = 'trello'
    
    
class LLMModelType(Enum):
    OPENAI = 'openai'
    LLAMA = 'llama'
    
    
class Query:
    
    metadata_for_query = [
        ["story_info"],
        ["story_info", "description"],
        # ["story_info", "description"],
        # "",
        # "",
        # "",
        # "",
        
    ]
    queries = [
        
        ## Jira Story Intro
        '''
        Based on the Jira story details provided in the context, provide an introduction of the task contained in this story containing:
        Overview of the task: A brief summary of the main points or key aspects of the task in this Jira story. It provides a high-level understanding of what the task in this story is about.
        Purpose of the task: This should explain what this task aims to achieve.
        '''
        ,
        
        ## Description
        '''
        Based on the Jira story details provided in the context, provide the detailed description of the task in the story containing:
        Summary of the issue: A concise description of the task addressed by the Jira story.
        Background Information: Relevant context or historical details that help understand the issue, such as previous related work, changes, or decisions.
        Impact on Existing Functionality if any: Explanation of how the issue or its resolution will affect current features, systems, or processes.
        '''
        # ,

        # Functional and non functional requirements
        # '''
        # Based on the Jira story details provided in the context, provide the functional and non-functional requirements of the task if mentioned in the story:
        # Functional Requirements: Specific behaviors or functions the task must perform, detailing what should be done in the task should do to meet the user's needs.
        # Non-Functional Requirements: Criteria that define the task's quality attributes, such as performance, reliability, security, and usability, which dictate how the system performs its functions.
        # '''
        # ,
        
        # solutions and benefits
        # '''
        # Based on the Jira story details provided in the context, provide the detailed proposed solution of the story containing if mentioned in the story:
        # Suggested Solution: A proposed approach or strategy to address the issue or implement the task described in the Jira story.
        # Intended Benefits:  The expected positive outcomes or improvements that will result from implementing the suggested solution, such as enhanced performance, user satisfaction, or operational efficiency.

        # '''
        # ,

#        ## Implementation Details

        # '''
        # Based on the Jira story details provided in the context, provide the detailed comments and context information of the task containing:
        # Discussion Points from the Comments Section: Key topics, questions, or concerns raised during the discussion in the comments section of the Jira story.
        # Feedback from Code Reviewers: Insights, suggestions, or issues highlighted by code reviewers during the review process, aimed at improving the quality or functionality of the implementation.

        # '''
        # ,

        # acceptance_Criteria
        # '''
        # Based on the Jira story details provided in the context, provide the detailed acceptance criteria of the story. containing: 
        # Functional Success Metrics: Criteria or key performance indicators (KPIs) used to measure whether the system's functionality meets the desired objectives.
        # Performance Benchmarks: Standards or reference points used to assess the system's performance, such as response times, throughput, or resource usage.
        # Error Handling Validation: Processes or tests to ensure that the system correctly manages and responds to errors or exceptions, maintaining stability and providing useful feedback to users or developers.


        # '''
        # ,

    # word done summary
        # '''
        # Based on the Jira story details provided in the context, provide the detailed conclusion of the story containing:
        # Summary of the Work Done
        # Other References (if any)
        # '''
        ]