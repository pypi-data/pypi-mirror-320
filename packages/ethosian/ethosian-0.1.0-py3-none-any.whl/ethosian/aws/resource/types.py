from collections import OrderedDict
from typing import Dict, List, Type, Union

from ethosian.aws.resource.base import AwsResource
from ethosian.aws.resource.acm.certificate import AcmCertificate
from ethosian.aws.resource.cloudformation.stack import CloudFormationStack
from ethosian.aws.resource.ec2.volume import EbsVolume
from ethosian.aws.resource.ec2.subnet import Subnet
from ethosian.aws.resource.ec2.security_group import SecurityGroup
from ethosian.aws.resource.ecs.cluster import EcsCluster
from ethosian.aws.resource.ecs.task_definition import EcsTaskDefinition
from ethosian.aws.resource.ecs.service import EcsService

from ethosian.aws.resource.elb.load_balancer import LoadBalancer
from ethosian.aws.resource.elb.target_group import TargetGroup
from ethosian.aws.resource.elb.listener import Listener
from ethosian.aws.resource.iam.role import IamRole
from ethosian.aws.resource.iam.policy import IamPolicy
from ethosian.aws.resource.glue.crawler import GlueCrawler
from ethosian.aws.resource.s3.bucket import S3Bucket
from ethosian.aws.resource.secret.manager import SecretsManager
from ethosian.aws.resource.emr.cluster import EmrCluster
from ethosian.aws.resource.rds.db_cluster import DbCluster
from ethosian.aws.resource.rds.db_instance import DbInstance
from ethosian.aws.resource.rds.db_subnet_group import DbSubnetGroup
from ethosian.aws.resource.elasticache.cluster import CacheCluster
from ethosian.aws.resource.elasticache.subnet_group import CacheSubnetGroup

# Use this as a type for an object which can hold any AwsResource
AwsResourceType = Union[
    AcmCertificate,
    CloudFormationStack,
    EbsVolume,
    IamRole,
    IamPolicy,
    GlueCrawler,
    S3Bucket,
    SecretsManager,
    Subnet,
    SecurityGroup,
    DbSubnetGroup,
    DbCluster,
    DbInstance,
    CacheSubnetGroup,
    CacheCluster,
    EmrCluster,
    EcsCluster,
    EcsTaskDefinition,
    EcsService,
    LoadBalancer,
    TargetGroup,
    Listener,
]

# Use this as an ordered list to iterate over all AwsResource Classes
# This list is the order in which resources should be installed as well.
AwsResourceTypeList: List[Type[AwsResource]] = [
    Subnet,
    SecurityGroup,
    IamRole,
    IamPolicy,
    S3Bucket,
    SecretsManager,
    EbsVolume,
    AcmCertificate,
    CloudFormationStack,
    GlueCrawler,
    DbSubnetGroup,
    DbCluster,
    DbInstance,
    CacheSubnetGroup,
    CacheCluster,
    LoadBalancer,
    TargetGroup,
    Listener,
    EcsCluster,
    EcsTaskDefinition,
    EcsService,
    EmrCluster,
]

# Map Aws resource alias' to their type
_aws_resource_type_names: Dict[str, Type[AwsResource]] = {
    aws_type.__name__.lower(): aws_type for aws_type in AwsResourceTypeList
}
_aws_resource_type_aliases: Dict[str, Type[AwsResource]] = {
    "s3": S3Bucket,
    "volume": EbsVolume,
}

AwsResourceAliasToTypeMap: Dict[str, Type[AwsResource]] = dict(
    **_aws_resource_type_names, **_aws_resource_type_aliases)

# Maps each AwsResource to an install weight
# lower weight AwsResource(s) get installed first
AwsResourceInstallOrder: Dict[str, int] = OrderedDict(
    {resource_type.__name__: idx for idx,
        resource_type in enumerate(AwsResourceTypeList, start=1)}
)
