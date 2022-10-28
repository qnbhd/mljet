"""
DeployMe - A simple Open Source deployment tool for ML models

If you have been working on ML models, then you have probably
faced the task of deploying these models. Perhaps you are
participating in a hackathon or want to show your work to
management. According to our survey, more than 60% of the
data-scientists surveyed faced this task and more than 60%
of the respondents spent more than half an hour creating
such a service.

The most common solution is to wrap it in some kind
of web framework (like Flask).
"""

from deployme.docker_.docker_builder import deploy_to_docker

__version__ = "0.0.4"
