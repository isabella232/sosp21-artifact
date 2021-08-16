/* Digivice Server

The digivice server performs the following functionality:
   - a device driver: translate device model commands to vendor opcodes
   - a device server: expose REST endpoints per device
   - a kome client: report device status to kome apiserver TODO: decouple by dumping to redis
..for each device.
*/


const fs = require("fs");
const path = require("path");
const https = require("https");
const express = require("express");
const bodyParser = require("body-parser");


// Server configs
const __config_dir = path.resolve(__dirname, "..", "..");
const TYPE_GET = 0;
const TYPE_POST = 1;
let app = express();
let port = 8803;


// Provider APIs
const TuyAPI = require("tuyapi");
// ..


// Device metadata and credentials
const devices = JSON.parse(fs.readFileSync(
    path.resolve(__config_dir, "device.json"), "utf8")
);


// Device opcode translators
const deviceOps = require(path.resolve("deviceOp.ts")).allOps;


// Kome client
const kome = require(path.resolve("kome.ts"));


// Redis client
// let redis = require('redis').createClient();
// redis.on('connect', function () {
//     console.log("dgv: redis connected");
// });


// connMgr caches connection to device
let connMgr: any = new Map();
connMgr.discover = function (devices) {
    for (let d in devices) {
        let p = devices[d]["provider"];

        // demux provider
        switch (p) {
            case "tuya":
                // TODO: add timeout, discovery protocol etc.
                // TODO: dynamic kome informer addition
                // TODO: pass kome informer
                this.set(d, connTuya(d, null));
                break;
            default:
                console.log("dgv: unknown provider", p);
                break;
        }
    }

    console.log("dgv: runtime connected to devices:", this)
};
connMgr.discover(devices);


/* Device driver: command-opcodes translation

Example metadata:
{
  "kome-plug-0": {
    "id": "x",
    "key": "x",
    "kind": "plug",
    "provider": "tuya",
},

Example spec:
{
   "power": "on",
}

Example device op: {
    "power": {
        "toOp": function(src) {
            return {
                dps: 1,
                set: {
                    "on": true,
                    "off": false,
                }[src["power"]],
            }
        },
        "fromOp": function(src) {
            return {
                "power": src["dps"]["1"],
            }
        },
    },
}

Fields are customized according to provider and
device types.

Each dev object should have .get() and .set()
*/

// transAndSet invokes the toOp method in dev's opMap
// to translate device commands to provider-specific
// opcodes and then use them to set the dev;
//
// toOp should return a single object (e.g., a dict)
// that can be directly sent to the dev;
function transAndSet(dev, spec, opMap, options) {
    let opcodes = options;
    opcodes.data = {};

    for (let s in spec) {
        let ops = opMap[s]["toOp"](spec);
        for (let o in ops) {
            opcodes.data[o] = ops[o];
        }
    }

    // console.log("debug: set to", opcodes);
    return Promise.resolve(dev.set(opcodes));
}


// getAndTrans fetches states from the dev and invokes
// the fromOp() method in dev's opMap to translate the
// provider-specific opcodes to device status;
function getAndTrans(dev, opMap, options) {
    return dev.get(options).then(rawStatus => {
            return Promise.resolve(transFromRaw(rawStatus, opMap));
        }
    );
}


// transFromRaw does the actual opcode-state translation
function transFromRaw(raw, opMap) {
    let status = {};
    for (let op in opMap) {
        status[op] = opMap[op]["fromOp"](raw)
    }
    return status;
}


// isEmpty decides whether an object is considered empty
function isEmpty(s) {
    return s === null || Object.keys(s).length === 0
}


// Tuya device provider
// connTuya establishes a connection to a tuya device and
// returns the connection object.
function connTuya(name, timeout) {
    let metadata = devices[name];

    const dev = new TuyAPI({
        id: metadata.id,
        key: metadata.key,
    });


    // find device on network
    function findAndConnect() {
        dev.find().then(() => {
            dev.connect();
        }).catch((error) => {
            console.log("tuya: unable to connect to " +
                "device %s due to %s", name, error.message)
        });
    }

    findAndConnect();


    // Event handlers
    // handle data
    dev.on("data", data => {
        data = transFromRaw(data, deviceOps.tuya[metadata.kind]);
        // TODO: compare with local states and then decide whether to update
        console.log("debug:", data);
        kome.updateDeviceStatus(name, data);

        // write to redis
        // redis.set(name, JSON.stringify(data));
        // redis.get(name, function (obj) {
        //     console.log(JSON.parse(obj));
        // });
        console.log("tuya: receive %s from device %s", data, name);
    });


    // handle connect
    dev.status = {
        "connected": false,
    };
    dev.on("connected", () => {
        dev.status["connected"] = true;
        console.log("tuya: connected to device %s", name);
    });


    // handle disconnect
    dev.on("disconnected", () => {
        dev.status["connected"] = false;
        console.log("tuya: disconnected from device %s", name);

        // TODO: improve reconnect method
        findAndConnect()
    });


    // handle error
    dev.on("error", error => {
        console.log("tuya: error:", error);
    });


    // disconnect on timeout
    if (timeout !== null) {
        setTimeout(() => {
            dev.disconnect();
        }, timeout);
    }

    console.log("tuya: connected to device %s", name);
    return dev
}


function handleTuya(name, spec) {
    console.log("dgv: request to tuya device %s..", name);

    let dev = connMgr.get(name),
        metadata = devices[name];

    let opMap = deviceOps.tuya[metadata.kind];

    // TODO: use explicit GET/POST demux
    let reqType = isEmpty(spec) ? TYPE_GET : TYPE_POST;

    switch (reqType) {
        case TYPE_GET:
            // tuyapi returns only the first status object
            // by default; use the options to force it
            // return all status objects
            return getAndTrans(dev, opMap, {schema: true});
        case TYPE_POST:
            return transAndSet(dev, spec, opMap, {multiple: true});
    }
}


// Ring device provider
import 'dotenv/config'
import {RingApi, RingDeviceType} from 'ring-client-api'

async function ring() {
    const {env} = process,
        ringApi = new RingApi({
            // Replace with your refresh token
            refreshToken: env.RING_REFRESH_TOKEN!,
        }),
        locations = await ringApi.getLocations(),
        location = locations[0];
    // Locations API
    location.onConnected.subscribe((connected) => {
        const state = connected ? 'Connected' : 'Connecting';
        console.log(`${state} to location ${location.name} - ${location.id}`)
    });

    location.onDeviceDataUpdate.subscribe(data => {
        console.log("loc");
        console.log("location device update:", data)
    });

    // TODO: demux device types
    const devices = await location.getDevices();
    const motionSensor = devices.find(device => device.data.deviceType === RingDeviceType.MotionSensor);
    console.log(motionSensor.data);
    motionSensor.onData.subscribe(data => {
        console.log("data!");
        // TODO: read the motion sensor
        // TODO: get motion sensor id
        // console.log(data.motionStatus);
    })


}

ring();

// Sim device provider
// TODO:


/* Device server */
app.use(bodyParser.json());


app.get("/", function (req, res) {
    res.send("dgv server")
});


app.get("/ping/:msg", function (req, res) {
    res.send("pong " + req.params.msg);
});


app.get("/dgv/:name", function (req, res) {
    routeToProvider(req, res)
});


app.post("/dgv/:name", function (req, res) {
    routeToProvider(req, res)
});


// Device request routing
function routeToProvider(req, res) {
    let d = req.params.name,
        spec = req.body;
    let p = devices[d]["provider"];

    // demux provider
    switch (p) {
        case "tuya":
            handleTuya(d, spec).then(r => {
                res.send(r);
            });
            break;
        case "sim":
            break;
        default:
            res.send("dgv handler: unknown device", d);
            break;
    }
}

// Server instance
https.createServer({
    key: fs.readFileSync("server.key"),
    cert: fs.readFileSync("server.cert")
}, app)
    .listen(port, function () {
        console.log("dgv listening on https://localhost:%s", port)
    });