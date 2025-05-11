# Skillset Example

## Description

This code sample demonstrates building a Copilot Extension using the skillsets approach rather than a traditional agent. This extension is designed to generate random test and example data for a number of development purposes, by calling publicly available APIs.

## Understanding Skillsets

Skillsets are a streamlined approach to building Copilot Extensions that emphasizes simplicity and ease of integration. Unlike the agent model which requires you to manage AI interactions, skillsets provide a direct way for Copilot to access your service's capabilities through well-defined API endpoints.

### What Are Skillsets?

A skillset is a collection of up to 5 API endpoints that Copilot can directly call based on user requests. Each skill in your skillset:

- Has a specific name and inference description that helps Copilot understand when and how to use it
- Defines a URL endpoint that Copilot will call
- Specifies a JSON schema for parameters that Copilot will fill based on user intent
- Declares a return type (typically String) that Copilot will process and present to users

Skillsets represent the "function calling" pattern - where Copilot's AI determines which function to call based on user requests, constructs the appropriate parameters, and handles presenting the results back to users.

### How Skillsets Work

1. **User Request**: A user asks a question in Copilot Chat that matches one of your skillset's capabilities
2. **Inference**: Copilot determines which skill to invoke based on the inference description
3. **Parameter Mapping**: Copilot extracts parameters from the user's request and maps them to your schema
4. **API Call**: Copilot calls your endpoint with the extracted parameters
5. **Response Handling**: Your endpoint returns data that Copilot presents back to the user

### Architectural Model
- **Skillsets**: Define up to 5 API endpoints that Copilot can call directly. Copilot handles all AI interactions, prompt engineering, and response formatting.
- **Agents**: Provide full control over the interaction flow, including custom prompt crafting and specific LLM model selection.

![Architectural comparison between Skillsets and Agents](https://github.com/user-attachments/assets/9c5d6489-afb5-47c2-be73-2561d89dfde3)


### When to Choose Skillsets
Skillsets are ideal when you want to:
- Quickly integrate existing APIs or services without managing AI logic
- Focus purely on your service's core functionality
- Maintain consistent Copilot-style interactions without extensive development
- Get started with minimal infrastructure and setup
- Leverage Copilot's intelligence for parameter extraction and response formatting

Use agents instead if you need:
- Complex custom interaction flows
- Specific LLM model control (using LLMs that aren't provided by the Copilot API)
- Custom prompt crafting
- Advanced state management
- More than 5 API endpoints

## Example Implementation

This extension showcases the skillset approach by providing three simple endpoints that generate random development data:
- Random commit messages
- Lorem ipsum text generation
- Random user data

## Getting Started
1. Clone the repository: 

```
git clone git@github.com:copilot-extensions/skillset-example.git
cd skillset-example
```

2. Install dependencies:

```
go mod tidy
```

## Usage

1. Start up ngrok with the port provided:

```
ngrok http http://localhost:8080
```

2. Set the environment variables (use the ngrok generated url for the `FDQN`)
3. Run the application:

```
go run .
```

## Accessing the Extension in Chat:

1. In the `Copilot` tab of your Application settings (`https://github.com/settings/apps/<app_name>/agent`)
- Set the app type to "Skillset"
- Specify the following skills:

### Skillset Configuration Examples

Each skill in your skillset requires four key components:
- **Name**: A unique identifier for the skill (used internally by Copilot)
- **Inference Description**: Helps Copilot understand when to use this skill based on user intent
- **URL**: The endpoint that Copilot will call when invoking this skill
- **Parameters**: A JSON schema defining what parameters the skill accepts
- **Return Type**: The format of data returned (typically String)

```
Name: random_commit_message
Inference description: Generates a random commit message
URL: https://<your ngrok domain>/random-commit-message
Parameters: { "type": "object" }
Return type: String
---
Name: random_lorem_ipsum 
Inference description: Generates a random Lorem Ipsum text. Responses should have html tags present.
URL: https://<your ngrok domain>/random-lorem-ipsum
Parameters: 
{
   "type": "object",
   "properties": {
      "number_of_paragraphs": {
         "type": "number",
         "description": "The number of paragraphs to be generated. Must be between 1 and 10 inclusive"
      },
      "paragraph_length": {
         "type": "string",
         "description": "The length of each paragraph. Must be one of \"short\", \"medium\", \"long\", or \"verylong\""
      }
   }
}
Return type: String
---
Name: random_user
Inference description: Generates data for a random user
URL: https://<your ngrok domain>/random-user
Parameters: { "type": "object" }
Return type: String
```

The parameters definition is particularly important as it determines how Copilot extracts information from user requests. A well-designed schema helps Copilot accurately map user intent to your API parameters.

2. In the `General` tab of your application settings (`https://github.com/settings/apps/<app_name>`)
- Set the `Callback URL` to anything (`https://github.com` works well for testing, in a real environment, this would be a URL you control)
- Set the `Homepage URL` to anything as above
3. Ensure your permissions are enabled in `Permissions & events` > 
- `Account Permissions` > `Copilot Chat` > `Access: Read Only`
4. Ensure you install your application at (`https://github.com/apps/<app_name>`)
5. Now if you go to `https://github.com/copilot` you can `@` your skillset extension using the name of your app.

## What can the bot do?

Here's some example things:

* `@skillset-example please create a random commit message`
* `@skillset-example generate a lorem ipsum`
* `@skillset-example generate a short lorem ipsum with 3 paragraphs`
* `@skillset-example generate random user data`

## Implementation

This bot provides a passthrough to a couple of other APIs:

* For commit messages, https://whatthecommit.com/
* For Lorem Ipsum, https://loripsum.net/
* For user data, https://randomuser.me/

## Skillset Best Practices

When designing your own skillset-based Copilot Extension, consider these best practices:

1. **Clear Inference Descriptions**: Write precise, action-oriented descriptions that help Copilot understand when to use each skill
2. **Descriptive Parameter Schemas**: Include detailed descriptions for each parameter to help Copilot extract information correctly from user requests
3. **Limited Scope**: Each skill should do one thing well, rather than trying to handle multiple use cases
4. **Robust Error Handling**: Ensure your APIs gracefully handle invalid inputs and provide helpful error messages
5. **Fast Response Times**: Keep your API endpoints performant as users expect quick responses
6. **Stateless Design**: Design your skills to be stateless whenever possible for simplicity
7. **Comprehensive Testing**: Test your skills with various input combinations to ensure they work as expected

Remember that skillsets are limited to 5 endpoints, so choose your skills carefully to offer the most value to your users.

## Documentation

### Skillset Documentation
- [About skillsets](https://docs.github.com/en/copilot/building-copilot-extensions/building-a-copilot-skillset-for-your-copilot-extension/about-copilot-skillsets) - Overview of the skillset approach
- [Building a Copilot skillset](https://docs.github.com/en/copilot/building-copilot-extensions/building-a-copilot-skillset-for-your-copilot-extension) - Detailed guide on building skillsets
- [Creating a Copilot skillset](https://docs.github.com/en/copilot/building-copilot-extensions/building-a-copilot-skillset-for-your-copilot-extension/creating-a-copilot-skillset) - Step-by-step instructions
- [Skillset schema reference](https://docs.github.com/en/copilot/building-copilot-extensions/building-a-copilot-skillset-for-your-copilot-extension/skillset-schema-reference) - JSON schema reference

### General Copilot Extensions Documentation
- [Using Copilot Extensions](https://docs.github.com/en/copilot/using-github-copilot/using-extensions-to-integrate-external-tools-with-copilot-chat) - How users interact with extensions
- [About building Copilot Extensions](https://docs.github.com/en/copilot/building-copilot-extensions/about-building-copilot-extensions) - General extensions development
- [Set up process](https://docs.github.com/en/copilot/building-copilot-extensions/setting-up-copilot-extensions) - Setting up your development environment
