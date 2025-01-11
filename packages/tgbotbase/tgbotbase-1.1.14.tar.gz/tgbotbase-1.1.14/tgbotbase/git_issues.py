import tgbotbase.github_create_issue as github_create_issue
from hashlib import sha256


class GitIssue:
    def __init__(self, exception: Exception, text: str, message_id: int):
        self.ex = exception
        self.text = text
        self.message_id = message_id
        self.renv_data = False

    def set_renv(self, renv_data: str):
        self.renv_data: tuple[int, int] | int = list(map(int, renv_data.split(","))) if renv_data else 0

    def title(self) -> str:
        return f"({self.renv_data[1] + 1 if self.renv_data else 1}) [{self.err_hash}] {self.main_error}"

    def issue_text(self) -> str:
        return (
            f"{self.text}\n\n"
            f"Message ID: `/m {self.message_id}`"
        )

    @property
    def err_hash(self) -> str:
        return sha256(f"{self.main_error}-{self.text}".encode("utf-8")).hexdigest()[:8]
    
    @property
    def main_error(self) -> str:
        return str(self.ex).replace("<", "^").replace(">", "^")

    def create(self) -> str:
        if self.renv_data is False:
            print("renv data is False in GitIssue")
            return 
        
        if self.renv_data == 0:
            issue_id = github_create_issue.make_github_issue(
                title = self.title(),
                body = self.issue_text(),
                assignee = github_create_issue.GITHUB_USER,
                labels = ["bug"]
            )
            return f"{issue_id},{1}"
        
        else:
            github_create_issue.edit_github_issue(
                issue_id = self.renv_data[0],
                title = self.title(),
                body = self.issue_text(),
                assignee = github_create_issue.GITHUB_USER,
                labels = ["bug"]
            )
            return f"{self.renv_data[0]},{self.renv_data[1] + 1}"
        
        
