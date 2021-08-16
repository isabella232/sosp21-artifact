from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()


def update_status(gvr: dict, status):
    api = client.CustomObjectsApi()

    try:
        api.patch_namespaced_custom_object_status(group=gvr["group"],
                                                  version=gvr["version"],
                                                  namespace=gvr["namespace"],
                                                  name=gvr["name"],
                                                  plural=gvr["plural"],
                                                  body={
                                                      "apiVersion": "kome.io/v1",
                                                      "kind": gvr["plural"],
                                                      "metadata": {
                                                          "name": gvr["name"],
                                                          "namespace": gvr["namespace"],
                                                      },
                                                      "status": status,
                                                  },
                                                  )
    except ApiException as e:
        print(f"k8s: unable to update resource {gvr}:", e)


if __name__ == '__main__':
    update_status({
        "group": "kome.io",
        "version": "v1",
        "name": "kome-lamp-0",
        "namespace": "default",
        "plural": "lamps",
    }, {
        "power": "off",
        "brightness": "0.1",
    })
