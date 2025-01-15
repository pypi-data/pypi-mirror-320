import grp
import os
import pwd
import subprocess
from typing import List, Optional

import typer
import yaml
from kubernetes import client, config
from loguru import logger

MAX_CPU = 192
MAX_RAM = 890
MAX_GPU = 8
GPU_PRODUCTS = [
    "NVIDIA-A100-SXM4-80GB",
    "NVIDIA-A100-SXM4-40GB",
    "NVIDIA-A100-SXM4-40GB-MIG-3g.20gb",
    "NVIDIA-A100-SXM4-40GB-MIG-1g.5gb",
    "NVIDIA-H100-80GB-HBM3",
]


app = typer.Typer()


def fetch_user_info() -> dict:
    try:
        user_info = {}

        # Get the current user name
        user_info["login_user"] = os.getlogin()

        # Get user entry from /etc/passwd
        pw_entry = pwd.getpwnam(os.getlogin())

        # Extracting home directory and shell from the password entry
        user_info["home"] = pw_entry.pw_dir
        user_info["shell"] = pw_entry.pw_shell

        # Get group IDs
        group_ids = os.getgrouplist(os.getlogin(), pw_entry.pw_gid)

        # Get group names from group IDs
        user_info["groups"] = " ".join([grp.getgrgid(gid).gr_name for gid in group_ids])
        return user_info

    except Exception as e:
        logger.exception(f"Error fetching user info: {e}")
        return {}


class KubernetesJob:
    def __init__(
        self,
        name: str,
        image: str,
        kueue_queue_name: str,
        command: List[str] = None,
        args: Optional[List[str]] = None,
        cpu_request: Optional[str] = None,
        ram_request: Optional[str] = None,
        storage_request: Optional[str] = None,
        gpu_type: Optional[str] = None,
        gpu_product: Optional[str] = None,
        gpu_limit: Optional[int] = None,
        backoff_limit: int = 4,
        restart_policy: str = "Never",
        shm_size: Optional[str] = None,
        env_vars: Optional[dict] = None,
        secret_env_vars: Optional[dict] = None,
        volume_mounts: Optional[dict] = None,
        job_deadlineseconds: Optional[int] = None,
        privileged_security_context: bool = False,
        user_name: Optional[str] = None,
        user_email: Optional[str] = None,
        labels: Optional[dict] = None,
        annotations: Optional[dict] = None,
        namespace: Optional[str] = None,
        image_pull_secret: Optional[str] = None,
    ):
        # Validate gpu_limit first
        assert (
            gpu_limit is not None
        ), f"gpu_limit must be set to a value between 1 and {MAX_GPU}, not {gpu_limit}"
        assert (
            0 < gpu_limit <= MAX_GPU
        ), f"gpu_limit must be between 1 and {MAX_GPU}, got {gpu_limit}"

        self.name = name
        self.image = image
        self.command = command
        self.args = args
        self.gpu_limit = gpu_limit
        self.gpu_type = gpu_type
        self.gpu_product = gpu_product

        self.cpu_request = cpu_request if cpu_request else 12 * gpu_limit
        self.ram_request = ram_request if ram_request else f"{80 * gpu_limit}G"
        assert (
            int(self.cpu_request) <= MAX_CPU
        ), f"cpu_request must be less than {MAX_CPU}"

        # Safe calculation for shm_size with fallback
        self.shm_size = (
            shm_size
            if shm_size is not None
            else ram_request
            if ram_request is not None
            else f"{max(1, MAX_RAM // gpu_limit)}G"  # Ensure minimum 1G and avoid division by zero
        )

        self.env_vars = env_vars
        self.secret_env_vars = secret_env_vars

        self.storage_request = storage_request
        self.backoff_limit = backoff_limit
        self.restart_policy = restart_policy
        self.image_pull_secret = image_pull_secret

        self.volume_mounts = volume_mounts
        self.job_deadlineseconds = job_deadlineseconds
        self.privileged_security_context = privileged_security_context

        self.user_name = user_name or os.environ.get("USER", "unknown")
        self.user_email = user_email  # This is now a required field.
        self.kueue_queue_name = kueue_queue_name

        self.labels = {
            "eidf/user": self.user_name,
            "kueue.x-k8s.io/queue-name": self.kueue_queue_name,
        }

        if labels is not None:
            self.labels.update(labels)

        self.annotations = {"eidf/user": self.user_name}
        if user_email is not None:
            self.annotations["eidf/email"] = user_email

        if annotations is not None:
            self.annotations.update(annotations)

        self.user_info = fetch_user_info()
        self.annotations.update(self.user_info)
        logger.info(f"labels {self.labels}")
        logger.info(f"annotations {self.annotations}")

        self.namespace = namespace

    def _add_shm_size(self, container: dict):
        """Adds shared memory volume if shm_size is set."""
        if self.shm_size:
            container["volumeMounts"].append({"name": "dshm", "mountPath": "/dev/shm"})
        return container

    def _add_env_vars(self, container: dict):
        """Adds secret and normal environment variables to the
        container."""
        # Ensure that the POD_NAME environment variable is set
        container["env"] = [
            {
                "name": "POD_NAME",
                "valueFrom": {"fieldRef": {"fieldPath": "metadata.name"}},
            }
        ]
        # Add the environment variables
        if self.env_vars:
            for key, value in self.env_vars.items():
                container["env"].append({"name": key, "value": value})

        # pass kubernetes secrets as environment variables
        if self.secret_env_vars:
            for key, secret_name in self.secret_env_vars.items():
                container["env"].append(
                    {
                        "name": key,
                        "valueFrom": {
                            "secretKeyRef": {
                                "name": secret_name,
                                "key": key,
                            }
                        },
                    }
                )

        return container

    def _add_volume_mounts(self, container: dict):
        """Adds volume mounts to the container."""
        if self.volume_mounts:
            for mount_name, mount_data in self.volume_mounts.items():
                container["volumeMounts"].append(
                    {
                        "name": mount_name,
                        "mountPath": mount_data["mountPath"],
                    }
                )

        return container

    def _add_privileged_security_context(self, container: dict):
        """Adds privileged security context to the container."""
        if self.privileged_security_context:
            container["securityContext"] = {
                "privileged": True,
            }

        return container

    def generate_yaml(self):
        container = {
            "name": self.name,
            "image": self.image,
            "imagePullPolicy": "Always",
            "volumeMounts": [],
            "resources": {
                "requests": {},
                "limits": {},
            },
        }

        if self.command is not None:
            container["command"] = self.command

        if self.args is not None:
            container["args"] = self.args

        if not (
            self.gpu_type is None or self.gpu_limit is None or self.gpu_product is None
        ):
            container["resources"] = {"limits": {f"{self.gpu_type}": self.gpu_limit}}

        container = self._add_shm_size(container)
        container = self._add_env_vars(container)
        container = self._add_volume_mounts(container)
        container = self._add_privileged_security_context(container)

        if (
            self.cpu_request is not None
            or self.ram_request is not None
            or self.storage_request is not None
        ):
            if "resources" not in container:
                container["resources"] = {"requests": {}}

            if "requests" not in container["resources"]:
                container["resources"]["requests"] = {}

        if self.cpu_request is not None:
            container["resources"]["requests"]["cpu"] = self.cpu_request
            container["resources"]["limits"]["cpu"] = self.cpu_request

        if self.ram_request is not None:
            container["resources"]["requests"]["memory"] = self.ram_request
            container["resources"]["limits"]["memory"] = self.ram_request

        if self.storage_request is not None:
            container["resources"]["requests"]["storage"] = self.storage_request

        if self.gpu_type is not None and self.gpu_limit is not None:
            container["resources"]["limits"][f"{self.gpu_type}"] = self.gpu_limit

        job = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": self.name,
                "labels": self.labels,  # Add labels here
                "annotations": self.annotations,  # Add metadata here
            },
            "spec": {
                "template": {
                    "metadata": {
                        "labels": self.labels,  # Add labels to Pod template as well
                        "annotations": self.annotations,  # Add metadata to Pod template as well
                    },
                    "spec": {
                        "containers": [container],
                        "restartPolicy": self.restart_policy,
                        "volumes": [],
                    },
                },
                "backoffLimit": self.backoff_limit,
            },
        }

        if self.image_pull_secret:
            job["spec"]["imagePullSecrets"] = {"name": self.image_pull_secret}

        if self.job_deadlineseconds:
            job["spec"]["activeDeadlineSeconds"] = self.job_deadlineseconds

        if self.namespace:
            job["metadata"]["namespace"] = self.namespace

        if not (
            self.gpu_type is None or self.gpu_limit is None or self.gpu_product is None
        ):
            job["spec"]["template"]["spec"]["nodeSelector"] = {
                f"{self.gpu_type}.product": self.gpu_product
            }
        # Add shared memory volume if shm_size is set
        if self.shm_size:
            job["spec"]["template"]["spec"]["volumes"].append(
                {
                    "name": "dshm",
                    "emptyDir": {
                        "medium": "Memory",
                        "sizeLimit": self.shm_size,
                    },
                }
            )

        # Add volumes for the volume mounts
        if self.volume_mounts:
            for mount_name, mount_data in self.volume_mounts.items():
                volume = {"name": mount_name}

                if "pvc" in mount_data:
                    volume["persistentVolumeClaim"] = {"claimName": mount_data["pvc"]}
                elif "emptyDir" in mount_data:
                    volume["emptyDir"] = {}
                # Add more volume types here if needed
                job["spec"]["template"]["spec"]["volumes"].append(volume)

        return yaml.dump(job)

    def run(self):
        config.load_kube_config()

        job_yaml = self.generate_yaml()

        # Save the generated YAML to a temporary file
        with open("temp_job.yaml", "w") as temp_file:
            temp_file.write(job_yaml)

        # Run the kubectl command with --validate=False
        cmd = ["kubectl", "apply", "-f", "temp_job.yaml"]

        try:
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            # Remove the temporary file
            os.remove("temp_job.yaml")
            return result.returncode
        except subprocess.CalledProcessError as e:
            logger.info(
                f"Command '{' '.join(cmd)}' failed with return code {e.returncode}."
            )
            logger.info(f"Stdout:\n{e.stdout}")
            logger.info(f"Stderr:\n{e.stderr}")
            # Remove the temporary file
            os.remove("temp_job.yaml")
            return e.returncode  # return the exit code
        except Exception:
            logger.exception(
                f"An unexpected error occurred while running '{' '.join(cmd)}'."
            )  # This logs the traceback too
            # Remove the temporary file
            os.remove("temp_job.yaml")
            return 1  # return the exit code


def check_if_completed(job_name: str, namespace: str = "informatics") -> bool:
    # Load the kube config
    config.load_kube_config()

    # Create an instance of the API class
    api = client.BatchV1Api()

    job_exists = False
    is_completed = True

    # Check if the job exists in the specified namespace
    jobs = api.list_namespaced_job(namespace)
    if job_name in {job.metadata.name for job in jobs.items}:
        job_exists = True

    if job_exists is True:
        job = api.read_namespaced_job(job_name, namespace)
        is_completed = False

        # Check the status conditions
        if job.status.conditions:
            for condition in job.status.conditions:
                if condition.type == "Complete" and condition.status == "True":
                    is_completed = True
                elif condition.type == "Failed" and condition.status == "True":
                    logger.error(f"Job {job_name} has failed.")
        else:
            logger.info(f"Job {job_name} still running or status is unknown.")

        if is_completed:
            api_res = api.delete_namespaced_job(
                name=job_name,
                namespace=namespace,
                body=client.V1DeleteOptions(propagation_policy="Foreground"),
            )
            logger.info(f"Job '{job_name}' deleted. Status: {api_res.status}")
    return is_completed


def send_message_command(env_vars: dict) -> str:
    """
    Send a message to Slack when the job starts if the SLACK_WEBHOOK environment variable is set.
    """
    if "SLACK_WEBHOOK" not in env_vars:
        logger.debug("SLACK_WEBHOOK not found in env_vars.")
        return ""
    return (
        """apt-get update && apt-get install -y curl;"""  # Install the curl command
        + """curl -X POST -H 'Content-type: application/json' --data '{"text":"Job started in '"$POD_NAME"'"}' $SLACK_WEBHOOK ;"""
    )


def get_env_vars(
    local_env_vars: list[str],
    load_dotenv: bool = False,
) -> dict[str, str]:
    """Get environment variables from local environment and secrets."""

    if load_dotenv:
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except Exception as e:
            logger.warning(f"Error loading .env file: {e}")

    env_vars = {}
    for var_name in local_env_vars:
        try:
            env_vars[var_name] = os.environ[var_name]
        except KeyError:
            logger.warning(
                f"Environment variable {var_name} not found in local environment"
            )
    return env_vars


def get_secret_env_vars(
    secrets_names: list[str],
    namespace: str = "informatics",
) -> dict[str, str]:
    """
    Get secret environment variables from Kubernetes secrets
    """
    secrets_env_vars = {}
    for secret_name in secrets_names:
        try:
            v1 = client.CoreV1Api()
            secret = v1.read_namespaced_secret(name=secret_name, namespace=namespace)
            for key in secret.data.keys():
                if key in secrets_env_vars:
                    logger.warning(f"Key {key} already set in env_vars.")
                secrets_env_vars[key] = secret_name
        except Exception as e:
            logger.warning(f"Error reading secret {secret_name}: {e}")


@app.command()
def launch(
    email: str = typer.Option(..., help="User email"),
    job_name: str = typer.Option(..., help="Name of the Kubernetes job"),
    docker_image: str = typer.Option(
        "nvcr.io/nvidia/cuda:12.0.0-devel-ubuntu22.04", help="Docker image"
    ),
    namespace: str = typer.Option("informatics", help="Kubernetes namespace"),
    queue_name: str = typer.Option("informatics-user-queue", help="Kueue queue name"),
    interactive: bool = typer.Option(False, help="Run in interactive mode"),
    command: str = typer.Option(..., help="Command to run in the container"),
    cpu_request: str = typer.Option("1", help="CPU request"),
    ram_request: str = typer.Option("8Gi", help="RAM request"),
    gpu_limit: int = typer.Option(1, help="GPU limit"),
    gpu_product: str = typer.Option("NVIDIA-A100-SXM4-40GB", help="GPU product"),
    secrets_env_vars: list[str] = typer.Option(
        [],  # Use empty list as default instead of None
        help="List of secret environment variables to export to the container",
    ),
    local_env_vars: list[str] = typer.Option(
        [],  # Use empty list as default instead of None
        help="List of local environment variables to export to the container",
    ),
    load_dotenv: bool = typer.Option(
        True, help="Load environment variables from .env file"
    ),
    nfs_server: str = typer.Option("10.24.1.255", help="NFS server"),
    dry_run: bool = typer.Option(False, help="Dry run"),
):
    """Launch a Kubernetes job with the specified configuration."""

    is_completed = check_if_completed(job_name, namespace=namespace)

    if gpu_product not in GPU_PRODUCTS:
        logger.warning(f"GPU product {gpu_product} likely supported.")

    if is_completed is True:
        logger.info(f"Job '{job_name}' is completed. Launching a new job.")

        if interactive:
            cmd = "while true; do sleep 60; done;"
        else:
            cmd = command
            logger.info(f"Command: {cmd}")

        # Get local environment variables
        env_vars_dict = get_env_vars(
            local_env_vars=local_env_vars,
            load_dotenv=load_dotenv,
        )
        secrets_env_vars_dict = get_secret_env_vars(
            secrets_names=secrets_env_vars,
            namespace=namespace,
        )

        logger.info(f"Creating job for: {cmd}")
        job = KubernetesJob(
            name=job_name,
            cpu_request=cpu_request,
            ram_request=ram_request,
            image=docker_image,
            gpu_type="nvidia.com/gpu",
            gpu_limit=gpu_limit,
            gpu_product=gpu_product,
            backoff_limit=0,
            command=["/bin/bash", "-c", "--"],
            args=[send_message_command(env_vars_dict) + cmd],
            env_vars=env_vars_dict,
            secret_env_vars=secrets_env_vars_dict,
            user_email=email,
            namespace=namespace,
            kueue_queue_name=queue_name,
            volume_mounts={
                "nfs": {"mountPath": "/nfs", "server": nfs_server, "path": "/"}
            },
        )
        job_yaml = job.generate_yaml()
        logger.info(job_yaml)
        # Run the Job on the Kubernetes cluster
        if not dry_run:
            job.run()
    else:
        logger.info(f"Job '{job_name}' is still running.")


def cli():
    """Entry point for the application"""
    app()


if __name__ == "__main__":
    cli()
