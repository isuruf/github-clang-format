
from contextlib import contextmanager
import os
import tornado.httpserver
import tornado.ioloop
import tornado.web
import requests
import tempfile
import shutil
import subprocess

from git import GitCommandError, Repo, Actor
import github
from fnmatch import fnmatch

@contextmanager
def tmp_directory():
    tmp_dir = tempfile.mkdtemp('_clang_format')
    yield tmp_dir
    shutil.rmtree(tmp_dir)

def get_github_token():
    tok = os.environ.get('GH_TOKEN')
    if not tok:
        raise RuntimeError("GH_TOKEN not available")
    return tok

def get_repo(gh):
    repo = os.environ.get('GH_REPO')
    if not repo:
        raise RuntimeError("GH_REPO not available")
    return gh.get_repo(repo)

def get_all_files(tmp_dir):
    l = []
    for root, directories, filenames in os.walk(tmp_dir):
        d = os.path.relpath(root, tmp_dir)
        if d == ".git" or d.startswith(".git/"):
            continue
        for filename in filenames: 
            l.append(os.path.relpath(os.path.join(root, filename), tmp_dir)) 
    return l
    
def run_clang_format(pr_id):
    gh = github.Github(get_github_token())

    with tmp_directory() as tmp_dir:
        repo = Repo.clone_from(get_repo(gh).clone_url, tmp_dir)

        # Retrieve the PR refs.
        try:
            repo.remotes.origin.fetch([
                'pull/{pr}/merge:pull/{pr}/merge'.format(pr=pr_id)
            ])
            ref_merge = repo.refs['pull/{pr}/merge'.format(pr=pr_id)]
        except GitCommandError:
            # Either `merge` doesn't exist because the PR was opened
            # in conflict or it is closed.
            return
        ref_merge.checkout(force=True)
        files = get_all_files(tmp_dir)
        includes = []
        excludes = []
        version = ""
        clang_format_file = '{}/.clang-format'.format(tmp_dir)
        if not os.path.isfile(clang_format_file):
            return
        with open(clang_format_file) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        for line in content:
            if line.startswith("# version: "):
                version = line[len("# version: "):]
            if line.startswith("# include: "):
                includes.append(line[len("# include: "):])
            if line.startswith("# exclude: "):
                excludes.append(line[len("# exclude: "):])
        if not version in ["3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9"]:
            return
        final_file_list = []
        for f in files:
            if any(fnmatch(f, include) for include in includes) and not(any(fnmatch(f, exclude) for exclude in excludes)):
                final_file_list.append(f)
        for f in final_file_list:
            subprocess.check_call(["clang-format-{}".format(version), "-i", f], cwd=tmp_dir)
        gh_username = gh.get_user().login
        gh_reponame = get_repo(gh).name
        actor = Actor(gh.get_user().name, "{}@users.noreply.github.com".format(gh_username))
        if len(repo.index.diff(None)) > 0:
            repo.git.add(u=True)
            repo.index.commit("Format using clang-format-{}".format(version), author=actor, committer=actor)
            dest_url = "https://{}@github.com/{}/{}".format(get_github_token(), gh_username, gh_reponame)
            remote = repo.create_remote(gh_username, url=dest_url)
            remote.push(refspec='{}:{}'.format("HEAD", "format-pr{}".format(pr_id)), force=True)
            return "https://github.com/{}/{}/commit/{}".format(gh_username, gh_reponame, hexsha)
        return


class MainHandler(tornado.web.RequestHandler):
    def post(self):
        headers = self.request.headers
        event = headers.get('X-GitHub-Event', None)

        if event == 'ping':
            self.write('pong')
        elif event == 'pull_request':
            body = tornado.escape.json_decode(self.request.body)
            action = body['action']
            title = body['pull_request']['title']
            pr = int(body['pull_request']['number'])
            if action == "opened" or action == "synchronize":
                message = run_clang_format(pr)
                if not message:
                    msg = """
Hi,
I've run clang-format and found that the code needs formatting.
Here's a commit that fixes this. {}
"""
                    msg = msg.format(message)
                    gh = github.Github(get_github_token())
                    issue = get_repo(gh).get_issue(pr)
                    issue.create_comment(message)

def main():
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    port = int(os.environ.get("PORT", 5000))
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
