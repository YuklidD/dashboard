from kubernetes import client, config
import os

class KubernetesService:
    def __init__(self):
        # Load kube config. In cluster or local.
        try:
            config.load_incluster_config()
        except config.ConfigException:
            try:
                config.load_kube_config()
            except config.ConfigException:
                print("Warning: Could not load kube config")
                self.apps_v1 = None
                self.core_v1 = None
                return

        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()

    def list_deployments(self, namespace="default"):
        if not self.apps_v1: return []
        return self.apps_v1.list_namespaced_deployment(namespace)

    def get_deployment_status(self, name, namespace="default"):
        if not self.apps_v1: return None
        try:
            return self.apps_v1.read_namespaced_deployment(name, namespace)
        except client.ApiException:
            return None

    def scale_deployment(self, name, replicas, namespace="default"):
        if not self.apps_v1: return None
        body = {"spec": {"replicas": replicas}}
        return self.apps_v1.patch_namespaced_deployment_scale(name, namespace, body)

k8s_service = KubernetesService()
