
import streamlit as st
import requests
import os

# Function to execute a GraphQL query
def execute_query(query, variables, token):
    headers = {
        "Authorization": f"bearer {token}"
    }
    response = requests.post("https://api.github.com/graphql", json={'query': query, 'variables': variables}, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if 'errors' in result:
            st.error(f"GraphQL query returned errors: {result['errors']}")
            return None
        return result
    else:
        st.error(f"Query failed with status code {response.status_code}")
        return None

# Function to fetch issues with customizable parameters
def fetch_issues(repo_owner, repo_name, token, min_comments=0, state="ALL", order_by="UPDATED_AT", direction="DESC", first=100):
    query = """
    query($owner: String!, $name: String!, $cursor: String, $state: [IssueState!], $orderBy: IssueOrderField!, $direction: OrderDirection!, $first: Int!) {
      repository(owner: $owner, name: $name) {
        issues(first: $first, after: $cursor, states: $state, orderBy: {field: $orderBy, direction: $direction}) {
          edges {
            node {
              number
              url
              title
              body
              createdAt
              updatedAt
              comments(first: 100) {
                totalCount
                edges {
                  node {
                    author {
                      login
                    }
                    body
                    createdAt
                  }
                }
              }
            }
          }
          pageInfo {
            endCursor
            hasNextPage
          }
        }
      }
    }
    """
    variables = {
        "owner": repo_owner,
        "name": repo_name,
        "cursor": None,
        "state": state if state != "ALL" else ["OPEN", "CLOSED"],
        "orderBy": order_by,
        "direction": direction,
        "first": first
    }
    
    all_issues = []
    
    while True:
        result = execute_query(query, variables, token)
        if result is None or 'data' not in result:
            break
        
        edges = result['data']['repository']['issues']['edges']
        page_info = result['data']['repository']['issues']['pageInfo']
        
        for edge in edges:
            issue = edge['node']
            comment_count = issue['comments']['totalCount']
            if comment_count >= min_comments:
                comments = [{
                    "author": comment['node']['author']['login'] if comment['node']['author'] else 'Unknown',
                    "body": comment['node']['body'],
                    "createdAt": comment['node']['createdAt']
                } for comment in issue['comments']['edges']]
                
                all_issues.append({
                    "number": issue['number'],
                    "url": issue['url'],
                    "title": issue.get('title', 'No Title'),
                    "body": issue.get('body', 'No Description'),
                    "createdAt": issue['createdAt'],
                    "updatedAt": issue['updatedAt'],
                    "comments": comments,
                    "comment_count": comment_count
                })
        
        if not page_info['hasNextPage']:
            break
        
        variables['cursor'] = page_info['endCursor']
    
    return all_issues

def load_reviewed_urls():
    if os.path.exists('urls.txt'):
        with open('urls.txt', 'r') as f:
            return set(line.strip() for line in f)
    return set()

def main():
    st.title("GitHub Issue Reviewer")

    # Sidebar for configuration
    st.sidebar.header("Configuration")
    github_token = st.sidebar.text_input("GitHub API Token", value='', type="password")
    repo_owner = st.sidebar.text_input("Repository Owner", value="The-OpenROAD-Project")
    repo_name = st.sidebar.text_input("Repository Name", value="OpenROAD")
    min_comments = st.sidebar.number_input("Minimum Comments", min_value=0, value=2)
    state = st.sidebar.selectbox("Issue State", ["ALL", "OPEN", "CLOSED"])
    order_by = st.sidebar.selectbox("Order By", ["UPDATED_AT", "CREATED_AT", "COMMENTS"])
    direction = st.sidebar.selectbox("Direction", ["DESC", "ASC"])
    first = 100

    if 'reviewed_count' not in st.session_state:
        st.session_state.reviewed_count = 0

    reviewed_urls = load_reviewed_urls()

    if st.sidebar.button("Fetch Issues"):
        if not github_token:
            st.error("Please enter a valid GitHub API token.")
        else:
            all_issues = fetch_issues(repo_owner, repo_name, github_token, min_comments, state, order_by, direction, first)
            st.session_state.issues = [issue for issue in all_issues if issue['url'] not in reviewed_urls]
            st.session_state.current_issue_index = 0

    if 'issues' in st.session_state and st.session_state.issues:
        total_issues = len(st.session_state.issues)
        remaining_issues = total_issues - st.session_state.current_issue_index
        
        st.write(f"Total Issues Fetched: {total_issues}")
        st.write(f"Remaining Issues to Check: {remaining_issues}")
        st.write(f"Total Issues Reviewed: {st.session_state.reviewed_count}")
        
        current_issue = st.session_state.issues[st.session_state.current_issue_index]
        
        st.write(f"Issue #{current_issue['number']}: {current_issue['title']}")
        st.write(f"Created At: {current_issue['createdAt']}")
        st.write(f"Updated At: {current_issue['updatedAt']}")
        st.write(f"Comment Count: {current_issue['comment_count']}")
        st.markdown(f"[View Issue on GitHub]({current_issue['url']})")

        with st.expander("Show Issue Body"):
            st.write(current_issue['body'])

        # Display comments
        st.subheader("Comments:")
        for comment in current_issue['comments']:
            st.write(f"**{comment['author']}** commented at {comment['createdAt']}")
            st.write(comment['body'])
            st.markdown("---")

        col1, col2 = st.columns(2)
        if col1.button("Yes"):
            with open('urls.txt', 'a') as f:
                f.write(f"{current_issue['url']}\n")
            with open('selected_urls.txt', 'a') as f:
                f.write(f"{current_issue['url']}\n")
            st.session_state.current_issue_index += 1
            st.session_state.reviewed_count += 1
        if col2.button("No"):
            with open('urls.txt', 'a') as f:
                f.write(f"{current_issue['url']}\n")
            st.session_state.current_issue_index += 1
            st.session_state.reviewed_count += 1

        if st.session_state.current_issue_index >= total_issues:
            st.write("All issues reviewed!")
    elif 'issues' in st.session_state:
        st.write("No new issues found matching the specified criteria.")
    else:
        st.write("Please configure and fetch issues using the sidebar.")

    # Display statistics
    st.sidebar.markdown("---")
    st.sidebar.subheader("Statistics")
    st.sidebar.write(f"Total Issues Reviewed: {st.session_state.reviewed_count}")
    
    if os.path.exists('selected_urls.txt'):
        with open('selected_urls.txt', 'r') as f:
            selected_count = len(f.readlines())
        st.sidebar.write(f"Issues Marked 'Yes': {selected_count}")

if __name__ == "__main__":
    main()
