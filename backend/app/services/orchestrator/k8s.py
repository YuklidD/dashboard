import uuid
from datetime import datetime
from typing import List, Optional
from kubernetes import client, config
from app.services.orchestrator.base import HoneypotOrchestrator
from app.models.honeypot import Honeypot, HoneypotCreate, HoneypotStatus

class K8sOrchestrator(HoneypotOrchestrator):
    def __init__(self):
        try:
            config.load_incluster_config()
        except config.ConfigException:
            try:
                config.load_kube_config()
            except config.ConfigException:
                print("Warning: Could not load kubeconfig. K8s operations will fail.")
        
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.namespace = "haas-honeypots"

    def deploy_honeypot(self, honeypot_create: HoneypotCreate) -> Honeypot:
        honeypot_id = str(uuid.uuid4())
        name = f"honeypot-{honeypot_id[:8]}"
        
        # Define Deployment
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(name=name, labels={"app": "honeypot", "id": honeypot_id}),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(match_labels={"app": "honeypot", "id": honeypot_id}),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": "honeypot", "id": honeypot_id}),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="shellm",
                                image=honeypot_create.image,
                                ports=[client.V1ContainerPort(container_port=2222)]
                            )
                        ]
                    )
                )
            )
        )

        try:
            self.apps_v1.create_namespaced_deployment(namespace=self.namespace, body=deployment)
            return Honeypot(
                id=honeypot_id,
                name=honeypot_create.name,
                image=honeypot_create.image,
                status=HoneypotStatus.PENDING,
                created_at=datetime.utcnow()
            )
        except client.ApiException as e:
            print(f"Exception when calling AppsV1Api->create_namespaced_deployment: {e}")
            raise e

    def terminate_honeypot(self, honeypot_id: str) -> bool:
        # Find deployment by label
        label_selector = f"id={honeypot_id}"
        deployments = self.apps_v1.list_namespaced_deployment(namespace=self.namespace, label_selector=label_selector)
        
        if not deployments.items:
            return False
            
        name = deployments.items[0].metadata.name
        try:
            self.apps_v1.delete_namespaced_deployment(name=name, namespace=self.namespace)
            return True
        except client.ApiException as e:
            print(f"Exception when calling AppsV1Api->delete_namespaced_deployment: {e}")
            return False

    def get_honeypot(self, honeypot_id: str) -> Optional[Honeypot]:
        # This is a simplified implementation. In reality, we'd check Pod status.
        label_selector = f"id={honeypot_id}"
        pods = self.core_v1.list_namespaced_pod(namespace=self.namespace, label_selector=label_selector)
        
        if not pods.items:
            return None
            
        pod = pods.items[0]
        status = HoneypotStatus.PENDING
        if pod.status.phase == "Running":
            status = HoneypotStatus.RUNNING
        elif pod.status.phase in ["Succeeded", "Failed"]:
            status = HoneypotStatus.TERMINATED
            
        return Honeypot(
            id=honeypot_id,
            name=pod.metadata.name, # Use pod name or store original name in annotation
            image=pod.spec.containers[0].image,
            status=status,
            ip_address=pod.status.pod_ip,
            created_at=pod.metadata.creation_timestamp
        )

    def list_honeypots(self) -> List[Honeypot]:
        pods = self.core_v1.list_namespaced_pod(namespace=self.namespace, label_selector="app=honeypot")
        results = []
        for pod in pods.items:
            # Extract ID from labels
            honeypot_id = pod.metadata.labels.get("id", "unknown")
            
            status = HoneypotStatus.PENDING
            if pod.status.phase == "Running":
                status = HoneypotStatus.RUNNING
            
            results.append(Honeypot(
                id=honeypot_id,
                name=pod.metadata.name,
                image=pod.spec.containers[0].image,
                status=status,
                ip_address=pod.status.pod_ip,
                created_at=pod.metadata.creation_timestamp
            ))
        return results
