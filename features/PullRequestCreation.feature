Feature: Pull Request Creation

    Scenario: New feature branch creates PR
        Given I have an empty Azure Devops Git Repo
        And there is a new branch named 'feature/Utopia'
        When I create a pull request from 'feature/Utopia' to 'develop'
        Then there is an Azure Devops Pull Request with the title "RouteToLive: feature/Utopia"
        And that Pull Request goes from feature/Utopia to develop
        And that Pull Request has the 'Draft' status
