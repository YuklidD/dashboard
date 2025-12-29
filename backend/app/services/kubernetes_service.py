from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import List, Dict, Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class KubernetesService:
    def __init__(self):
        if settings.K8S_IN_CLUSTER:
            config.load_incluster_config()
        else:
            config.load_kube_config()
        
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.namespace = settings.K8S_NAMESPACE
    
    def create_honeypot_deployment(self, honeypot_type: str, replicas: int = 1,
                                   cpu_limit: str = "500m", memory_limit: str = "512Mi") -> Dict:
        """Deploy a new honeypot instance"""
        deployment_name = f"{honeypot_type}-honeypot-{self._generate_id()}"
        
        # Define container based on honeypot type
        container_image = {
            "shellm": "haas/shellm-honeypot:latest",
            "ssh": "haas/ssh-honeypot:latest",
            "http": "haas/http-honeypot:latest"
        }.get(honeypot_type, "haas/generic-honeypot:latest")
        
        container = client.V1Container(
            name=honeypot_type,
            image=container_image,
            resources=client.V1ResourceRequirements(
                limits={"cpu": cpu_limit, "memory": memory_limit},
                requests={"cpu": "100m", "memory": "128Mi"}
            ),
            ports=[client.V1ContainerPort(container_port=8080)],
            env=[
                client.V1EnvVar(name="HONEYPOT_TYPE", value=honeypot_type),
                client.V1EnvVar(name="PROMETHEUS_ENDPOINT", value=settings.PROMETHEUS_URL)
            ]
        )
        
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={"app": deployment_name, "type": honeypot_type}
            ),
            spec=client.V1PodSpec(containers=[container])
        )
        
        spec = client.V1DeploymentSpec(
            replicas=replicas,
            selector=client.V1LabelSelector(
                match_labels={"app": deployment_name}
            ),
            template=template
        )
        
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=deployment_name),
            spec=spec
        )
        
        try:
            self.apps_v1.create_namespaced_deployment(
                namespace=self.namespace,
                body=deployment
            )
            logger.info(f"Created deployment: {deployment_name}")
            return {"deployment_name": deployment_name, "status": "created"}
        except ApiException as e:
            logger.error(f"Failed to create deployment: {e}")
            raise
    
    def list_honeypot_pods(self) -> List[Dict]:
        """List all honeypot pods"""
        try:
            pods = self.core_v1.list_namespaced_pod(
                namespace=self.namespace,
                label_selector="type in (shellm,ssh,http)"
            )
            
            result = []
            for pod in pods.items:
                result.append({
                    "pod_name": pod.metadata.name,
                    "status": pod.status.phase,
                    "node": pod.spec.node_name,
                    "ip": pod.status.pod_ip,
                    "start_time": pod.status.start_time,
                    "honeypot_type": pod.metadata.labels.get("type", "unknown")
                })
            return result
        except ApiException as e:
            logger.error(f"Failed to list pods: {e}")
            return []
    
    def delete_honeypot_pod(self, pod_name: str) -> bool:
        """Terminate a specific honeypot pod"""
        try:
            self.core_v1.delete_namespaced_pod(
                name=pod_name,
                namespace=self.namespace
            )
            logger.info(f"Deleted pod: {pod_name}")
            return True
        except ApiException as e:
            logger.error(f"Failed to delete pod: {e}")
            return False
    
    def extend_pod_lifetime(self, pod_name: str, additional_minutes: int) -> bool:
        """Extend pod lifetime by updating TTL annotation"""
        try:
            pod = self.core_v1.read_namespaced_pod(
                name=pod_name,
                namespace=self.namespace
            )
            
            if not pod.metadata.annotations:
                pod.metadata.annotations = {}
            
            current_ttl = int(pod.metadata.annotations.get("ttl-minutes", "60"))
            new_ttl = current_ttl + additional_minutes
            pod.metadata.annotations["ttl-minutes"] = str(new_ttl)
            
            self.core_v1.patch_namespaced_pod(
                name=pod_name,
                namespace=self.namespace,
                body=pod
            )
            logger.info(f"Extended pod {pod_name} lifetime to {new_ttl} minutes")
            return True
        except ApiException as e:
            logger.error(f"Failed to extend pod lifetime: {e}")
            return False
    
    def isolate_pod(self, pod_name: str) -> bool:
        """Isolate pod by applying network policy"""
        # Create a NetworkPolicy that blocks all traffic except monitoring
        network_policy = client.V1NetworkPolicy(
            metadata=client.V1ObjectMeta(
                name=f"isolate-{pod_name}",
                namespace=self.namespace
            ),
            spec=client.V1NetworkPolicySpec(
                pod_selector=client.V1LabelSelector(
                    match_labels={"pod": pod_name}
                ),
                policy_types=["Ingress", "Egress"],
                ingress=[],
                egress=[
                    client.V1NetworkPolicyEgressRule(
                        to=[client.V1NetworkPolicyPeer(
                            namespace_selector=client.V1LabelSelector(
                                match_labels={"name": "monitoring"}
                            )
                        )]
                    )
                ]
            )
        )
        
        try:
            networking_v1 = client.NetworkingV1Api()
            networking_v1.create_namespaced_network_policy(
                namespace=self.namespace,
                body=network_policy
            )
            logger.info(f"Isolated pod: {pod_name}")
            return True
        except ApiException as e:
            logger.error(f"Failed to isolate pod: {e}")
            return False
    
    def _generate_id(self) -> str:
        """Generate unique ID for resources"""
        import random
        import string
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

k8s_service = KubernetesService()
