# PyToS;DR is a Python package that simplifies accessing and interpreting
# Terms of Service and Privacy Policies, drawing directly from the 
# ToS;DR GitHub repository.
#
# Copyright (c) 2024 José María Cruz Lorite
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import tqdm
import shutil
import platformdirs

from git import Repo

# prepare logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class PyToSDR:
    """PyToS;DR is a Python package that simplifies accessing Terms of Service documents
    from ToS;DR, drawing them directly from their GitHub repository.
    
    Attributes:
        repo_url (str): The path to the ToS;DR repository.
        repo_name (str): The name of the ToS;DR repository.
        cache_dir (str): The path to the cache directory.
        repo_path (str): The path to the ToS;DR repository.
        repo (git.Repo): The git repository object.
        services (list): A list of all services in the ToS;DR repository.
        documents (dict): A dictionary of all documents for each service.
        document_changes (dict): A dictionary of all changes for each document.
    """
    
    TOSDR_REPO_URL = "https://github.com/tosdr/tosdr-snapshots.git"
    OTA_REPO_URL = "https://github.com/OpenTermsArchive/contrib-versions.git"
    
    def __init__(self, track_changes: bool=True, changes_from_date=None, repo_url: str=TOSDR_REPO_URL):
        """Initialize the PyToS;DR object.
        
        Args:
            track_changes (bool): Whether to track changes in the repository.
            track_changes_from (str|datetime): The date from which to start tracking changes (default is 1700-01-01). 
            repo_url (str): The path to the ToS;DR repository.
        """
        self.repo_url = repo_url
        self.repo_name = os.path.basename(repo_url).replace(".git", "")
        self.cache_dir = platformdirs.user_cache_dir("pytosdr")
        self.repo_path = os.path.join(self.cache_dir, self.repo_name)
        
        # clone or pull the repository
        self.repo = None
        self._clone_or_pull_repo()
        
        # list all services
        logger.info(f"Listing all services.")
        self.services = self._list_services()
        logger.info(f"Found {len(self.services)} services.")
        
        # list all documents
        logger.info(f"Listing all documents for each service.")
        self.documents = {}
        for service in self.services:
            self.documents[service] = self._list_service_documents(service)
        logger.info(f"Found {sum([len(docs) for docs in self.documents.values()])} documents.")
    
    def _clone_or_pull_repo(self):
        """Clone the ToS;DR repository. If it already exists, pull the latest changes.
        """
        if not os.path.exists(self.repo_path):
            logger.info(f"The repository '{self.repo_name}' does not exist. Cloning it now. This may take a while.")
            Repo.clone_from(self.repo_url, self.repo_path)
        else:
            logger.info(f"The repository '{self.repo_name}' already exists, skipping cloning. Pulling the latest changes.")
            repo = Repo(self.repo_path)
            repo.remotes.origin.pull()
        logger.info(f"Repository '{self.repo_name}' is up-to-date.")
        self.repo = Repo(self.repo_path)
    
    def _cleanup_repo(self):
        """Delete the ToS;DR repository.
        """
        if os.path.exists(self.repo_path):
            shutil.rmtree(self.repo_path)
        else:
            raise FileNotFoundError(f"The repository {self.repo_name} does not exist.")
        return True
    
    def _list_services(self):
        """List all services in the ToS;DR repository.
        
        Returns:
            list: A list of all services.
        """
        services = []
        for service in os.listdir(self.repo_path):
            # check if it is a directory
            if os.path.isdir(os.path.join(self.repo_path, service)):
                services.append(service)
        return services
    
    def _list_service_documents(self, service: str):
        """List all documents for a given service.
        
        Args:
            service (str): The name of the service.
        
        Returns:
            list: A list of all documents for the given service.
        """
        documents = []
        service_path = os.path.join(self.repo_path, service)
        for document in os.listdir(service_path):
            documents.append(document)
        return [os.path.join(service, doc) for doc in documents]
    
    # def list_document_changes(self, document: str):
    #     """List all changes for a given document.
        
    #     Args:
    #         document (str): The name of the document.
        
    #     Returns:
    #         list: A list of all changes for the given document.
    #     """
    #     # for each document, list all commit changes
    #     logger.info(f"Listing all changes for each document.")
    #     self.document_changes = {}
    #     for commit in tqdm.tqdm(list(self.repo.iter_commits())):
    #         # get commit files changed
    #         for file in commit.stats.files:
    #             if not file in self.documents:
    #                 self.document_changes[file] = list()
    #             self.document_changes[file].append(commit)
    #     logger.info(f"Found {sum([len(changes) for changes in self.document_changes.values()])} changes.")
    #     return self.document_changes
