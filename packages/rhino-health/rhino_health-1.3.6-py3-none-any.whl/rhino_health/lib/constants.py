"""
Constants that are used in the rest of the system
"""
import enum


class ApiEnvironment:
    """
    Which environment you are hitting. By default you should be using PROD_API_URL

    Examples
    --------
    >>> from rhino_health import ApiEnvironment.LOCALHOST_API_URL, ApiEnvironment.DEV1_AWS_URL, ApiEnvironment.PROD_API_URL, ApiEnvironment.DEMO_DEV_URL
    """

    LOCALHOST_API_URL = "http://localhost:8080/api/"
    QA_AWS_URL = "https://qa-cloud.rhinohealth.com/api/"
    QA_URL = QA_AWS_URL  # Backwards Compat
    QA_GCP_URL = "https://qa-cloud.rhinofcp.com/api/"
    DEV1_AWS_URL = "https://dev1.rhinohealth.com/api/"
    DEV2_AWS_URL = "https://dev2.rhinohealth.com/api/"
    DEV3_AWS_URL = "https://dev3.rhinohealth.com/api/"
    DEV1_GCP_URL = "https://dev1.rhinofcp.com/api/"
    DEMO_DEV_URL = "https://demo-dev.rhinohealth.com/api/"
    DEMO_URL = "https://demo-prod.rhinohealth.com/api/"
    STAGING_AWS_URL = "https://staging.rhinohealth.com/api/"
    STAGING_GCP_URL = "https://staging.rhinofcp.com/api/"
    PROD_AWS_URL = "https://prod.rhinohealth.com/api/"
    PROD_API_URL = PROD_AWS_URL  # Backwards Compat
    PROD_GCP_URL = "https://prod.rhinofcp.com/api/"


class Dashboard:
    """
    Which dashboard serves the environment
    """

    LOCALHOST_URL = "http://localhost:3000"
    DEV1_AWS_URL = "https://dev1-dashboard.rhinohealth.com"
    DEV2_AWS_URL = "https://dev2-dashboard.rhinohealth.com"
    DEV3_AWS_URL = "https://dev3-dashboard.rhinohealth.com"
    DEV1_GCP_URL = "https://dev1-dashboard.rhinofcp.com"
    DEMO_DEV_URL = "https://demo-dev-dashboard.rhinohealth.com"
    STAGING_AWS_URL = "https://staging-dashboard.rhinohealth.com"
    STAGING_GCP_URL = "https://staging-dashboard.rhinofcp.com"
    DEMO_URL = "https://demo.rhinohealth.com"
    PROD_AWS_URL = "https://dashboard.rhinohealth.com"
    PROD_GCP_URL = "https://dashboard.rhinofcp.com"
    PROD_URL = PROD_AWS_URL  # Backwards Compat


class ContainerRegistryService:
    """
    Which container registry serves the environment
    """

    TEST_URL = "localhost:5201"
    LOCALHOST_URL = "localhost:5001"
    DEV_AWS_URL = "913123821419.dkr.ecr.us-east-1.amazonaws.com"
    DEV_URL = DEV_AWS_URL
    DEV_GCP_URL = "europe-west4-docker.pkg.dev/rhino-health-dev/rhino-gc-workgroup-rhino-health-dev"
    DEMO_DEV_URL = "913123821419.dkr.ecr.us-east-1.amazonaws.com"
    DEMO_URL = "913123821419.dkr.ecr.us-east-1.amazonaws.com"
    PROD_AWS_URL = "913123821419.dkr.ecr.us-east-1.amazonaws.com"
    PROD_URL = PROD_AWS_URL
    PROD_GCP_URL = "europe-west4-docker.pkg.dev/rhino-health-dev/rhino-gc-workgroup-rhino-health"


ECRService = ContainerRegistryService
"""
@autoapi False Deprecated
"""

BASE_URL_TO_DASHBOARD = {
    ApiEnvironment.LOCALHOST_API_URL: Dashboard.LOCALHOST_URL,
    ApiEnvironment.DEV1_AWS_URL: Dashboard.DEV1_AWS_URL,
    ApiEnvironment.DEV2_AWS_URL: Dashboard.DEV2_AWS_URL,
    ApiEnvironment.DEV3_AWS_URL: Dashboard.DEV3_AWS_URL,
    ApiEnvironment.DEV1_GCP_URL: Dashboard.DEV1_GCP_URL,
    ApiEnvironment.DEMO_DEV_URL: Dashboard.DEMO_DEV_URL,
    ApiEnvironment.DEMO_URL: Dashboard.DEMO_URL,
    ApiEnvironment.STAGING_AWS_URL: Dashboard.STAGING_AWS_URL,
    ApiEnvironment.STAGING_GCP_URL: Dashboard.STAGING_GCP_URL,
    ApiEnvironment.PROD_AWS_URL: Dashboard.PROD_AWS_URL,
    ApiEnvironment.PROD_GCP_URL: Dashboard.PROD_GCP_URL,
}
"""
Mapping of Base URL to Dashboard
"""


class CloudProvider(str, enum.Enum):
    AWS = "aws"
    GCP = "gcp"
