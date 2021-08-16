// Common tuya opcodes
let tuyaOps = {
    "power": {
        "toOp": (src) => {
            return {
                "1": {
                    "on": true,
                    "off": false,
                }[src["power"]],
            }
        },

        "fromOp": (src) => {
            return {
                true: "on",
                false: "off",
            }[src["dps"]["1"]]
        },
    },

    "brightness": {
        "toOp": (src) => {
            return {
                // convert and normalize percentage
                "2": (src["brightness"] * 255) | 0,
            }
        },

        "fromOp": (src) => {
            return (Math.round(src["dps"]["2"] * 100.0 / 255) / 100).toString()
        },
    },
};


let allOps = {
    "tuya": {
        // TODO: use device model
        "plug": {
            "power": tuyaOps["power"],
        },

        "lamp": {
            "power": tuyaOps["power"],
            "brightness": tuyaOps["brightness"],
        },
    },

    "vid2scene": {
        // TODO:
    },

    "sim": {
        // TODO:
    },
};

module.exports = {allOps};
