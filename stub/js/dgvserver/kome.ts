/* Integrations with kome apiserver */


const fs = require("fs");
const path = require("path");
const __config_dir = path.resolve(__dirname, "..", "..");


// Kome apiserver
import * as k8s from "@kubernetes/client-node"

const kc = new k8s.KubeConfig();
kc.loadFromDefault();
console.log("kome apiserver:", kc);


// Device metadata and credentials
const devices = JSON.parse(fs.readFileSync(
    path.resolve(__config_dir, "device.json"), "utf8")
);


// Kome client
// TODO: configurable KomeV1 parameters
const komeAPIPath = "/apis/kome.io/v1/namespaces/default";


function apiEndpoint(name) {
    let dev = devices[name];
    return [komeAPIPath, dev["kind"] + "s", name].join("/")
}


function isNull(v) {
    return !v
}


function updateDeviceStatus(name, status) {
    const dev = devices[name];
    const k8sApi = kc.makeApiClient(k8s.CustomObjectsApi);

    // TODO: configurable KomeV1 parameters
    // Check for resource version first
    k8sApi.getNamespacedCustomObjectStatus(
        "kome.io",
        "v1",
        "default",
        dev["kind"] + "s",
        name).then(r => {

        let rv = r.body["metadata"]["resourceVersion"];
        for (let s in r.body["status"]) {
            // if the given status has null field, replace it with existing value
            if (isNull(status[s])) {
                status[s] = r.body["status"][s]
            }
        }

        k8sApi.replaceNamespacedCustomObjectStatus(
            "kome.io",
            "v1",
            "default",
            dev["kind"] + "s",
            name,
            {
                "apiVersion": "kome.io/v1",
                "kind": dev["kind"],
                "metadata": {
                    "name": name,
                    "namespace": "default",
                    "resourceVersion": rv,
                },
                "status": status,
            },
        ).then(r => {
            console.log("dgv, kome client: update status of", name)
        }).catch(e => {
                console.log("kome: unable to patch:", e);
            }
        );
    });
}

module.exports = {updateDeviceStatus};