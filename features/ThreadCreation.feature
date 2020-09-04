Feature: Thread Creation

	Scenario: New thread on PR for each commit
    	Given I have an empty Azure Devops Git Repo
        And there is a new branch named 'feature/Utopia'
    	When I make a new commit to 'feature/Utopia'
        And I trigger a PR update for that commit
    	Then the Pull Request "RouteToLive: feature/Utopia" has a new thread
    	And that thread has an initial comment including the formatted name of the built artifact

