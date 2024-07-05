
# GitHub Issue Reviewer

This Streamlit application allows you to review GitHub issues efficiently, keeping track of reviewed and selected issues.

## Installation and Setup

1. Install Python 3.7 or higher if you haven't already.

2. Install Streamlit and other required packages:
   ```
   pip install streamlit requests python-dotenv
   ```

3. Clone this repository or download the `gh_reviewer.py` file.

4. Create a GitHub Personal Access Token:
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Generate a new token with `repo` scope
   - Copy the token for later use

## Running the Application

1. Open a terminal and navigate to the directory containing `gh_reviewer.py`.

2. Run the Streamlit app:
   ```
   streamlit run gh_reviewer.py
   ```

3. Your default web browser should open automatically. If not, the terminal will display a local URL you can open.

## Using the Application

1. In the sidebar, paste your GitHub API token into the "GitHub API Token" field.

2. Configure the repository and issue filtering options:
   - Repository Owner (e.g., "The-OpenROAD-Project")
   - Repository Name (e.g., "OpenROAD")
   - Minimum Comments
   - Issue State (ALL, OPEN, or CLOSED)
   - Order By (UPDATED_AT, CREATED_AT, or COMMENTS)
   - Direction (DESC or ASC)

3. Click "Fetch Issues" to retrieve issues based on your configuration.

4. Review each issue:
   - Read the issue details and comments
   - Click "Yes" to mark an issue as selected
   - Click "No" to skip the issue

5. The app will keep track of your progress:
   - `urls.txt`: Contains URLs of all reviewed issues
   - `selected_urls.txt`: Contains URLs of issues marked as "Yes"

6. You can close the app at any time. When you rerun it, it will exclude previously reviewed issues.

## Statistics

The sidebar displays statistics about your reviewing progress:
- Total Issues Reviewed
- Issues Marked 'Yes'

These statistics persist across sessions, allowing you to track your overall progress.

Happy reviewing!
