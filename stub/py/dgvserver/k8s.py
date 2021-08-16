from kubernetes import client, config

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()


def update_status(dev, status):
    api = client.CustomObjectsApi()

    my_resource = {
        "apiVersion": "kome.io/v1",
        "kind": "",
        "metadata": {"name": "XXX"},
        "status": {
        }
    }
    # api_response = api_instance.patch_namespaced_custom_object_status(group, version, namespace, plural, name, body, dry_run=dry_run, field_manager=field_manager, force=force)
