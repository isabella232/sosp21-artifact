## SOSP'21 Artifact

This artifact lays out the source code and experiment setup for the ACM SOSP 2021 conference paper: *"dSpace: Composable Abstractions for Smart Spaces".*

#### Content
- [QuickStart](#quickstart)
- [dSpace setup](#dspace-setup)
- [Digi development](#digi-development)
- [Run-time operations](#run-time-operations)
- [Benchmark](#benchmark) 

### QuickStart

Here is the TLDR for setting up dSpace components and building, composing, and customizing digis. The rest details are described in the following sections.

**Installations:**
- Kubernetes: install [minikube](https://minikube.sigs.k8s.io/docs/start/), [kubectl](https://kubernetes.io/docs/tasks/tools/), [helm](https://helm.sh/), and [kubectl-neat](https://github.com/silveryfu/kubectl-neat).
- dSpace: clone this repo under your GOPATH and rename the directory to dspace, i.e., change from `$GOPATH/src/digi.dev/sosp21-artifact/` to `$GOPATH/src/digi.dev/dspace/`. Then, build the dSpace command line dq with `make dq` and install digi library: `cd ./runtime/driver/digi/; pip install -e .`

**Start the runtime:**
- Run minikube with `minikube start`.
- Run dSpace controllers: `cd ./runtime/sync; make run; cd ../policy; make run`.

**Build a digi:**
- `cd ./mocks` -- all the commands below assume they are run under `./mocks` (or it can be any directory that contains the `Makefile` in it). Update the `REPO` parameter in the Makefile to your own container hub repository (e.g., dockerhub).
  ```Makefile
  ifndef REPO
  override REPO = YOUR_DOCKERHUB_ACCOUNT
  endif
  ```
  
- Create a directory and a digi schema model.yaml in it. The name of the directory must match the digi's kind. An example ./tv/model.yaml for a digi schema `TV`:
  ```yaml
  group: digi.dev
  version: v1
  kind: TV
  control:
    power: string
  ```
  
- Run `make gen KIND=TV` to generate its configuration files and scripts (they are packaged as the digi image). 

- Edit the `./tv/deploy/cr.yaml` to update the power's intent; e.g.,

  ```yaml
	spec:
  control:
    power:
      intent: "off"
  ```

- Edit the `./tv/driver/handler.py` to add driver logic/policies. An intro to digi driver programming can be found in the [tutorial notebook](https://github.com/digi-project/sosp21-artifact/blob/master/tutorial/tutorial-key.ipynb). For now, we can just leave the template handler.py unchanged (the digi will do nothing upon reconciliation). 

- Run `dq build tv` to build the digi image. It might take a while (constructing the driver's docker image), followed by `dq push tv`to push the image to a remote docker repo. You can configure minikube and docker runtime to use local container registry (see [here](https://stackoverflow.com/questions/42564058/how-to-use-local-docker-images-with-minikube)).

**Run the digi:**
- Run `dq run tv t1` to run a digi `t1` of kind TV.
- `kubectl get tvs` and `kubectl edit tvs t1` to edit the intent (i.e., `control.power.intent`) of the tv.
- `dq stop tv t1` to stop the digi.
You can also pick a digi from the mock digis /mocks (ones that do not need physical devices to run and test). E.g., `dq run lamp l1`. 

**Compose digis:**
- Start the mock lamp and room in /mocks with `dq run lamp l1` and `dq run room r1`
- Mount the lamp to room with `dq mount l1 r1`
- Use `kubectl edit rooms r1` to update the brightness of the room.

**Customize policies:**
- Create composition policies: see example [yield policy](https://github.com/digi-project/sosp21-artifact/blob/master/runtime/policy/deploy/mocks/crs/mock_yield.yaml).
- Create on-model policies: see L48 in [tutorial notebook](https://github.com/digi-project/sosp21-artifact/blob/master/tutorial/tutorial-key.ipynb).

> Note: we provide a prebuilt jupyter notebook to walk through the above steps. The notebook can be found and set up using the AWS VM image ami-0619512862a004fdf. We may have a few live notebook instances around, feel free to contact silvery@eecs.berkeley.edu to obtain access to them.

### dSpace Setup

**Kubernetes.** dSpace's runtime consists of controllers and application digis that run as k8s pods and interact with the k8s apiserver. Any major k8s distributions should run dSpace and most k8s tooling applicable to it. The first step of replicating the artifact is to set up a k8s cluster. To do so, install [minikube](https://minikube.sigs.k8s.io/docs/start/), package manager [helm](https://helm.sh/), the command line [kubectl](https://kubernetes.io/docs/tasks/tools/), and optionally [kubectl-neat](https://github.com/silveryfu/kubectl-neat) to reduce the output verbosity from kubectl.

**dSpace controllers.** Two dSpace controllers are used in this artifact: the [syncer](https://github.com/digi-project/sosp21-artifact/tree/master/runtime/sync) and [policer](dspace/runtime/policy). Use the Makefile (`make run`) in their directory to run the controllers. They will be deployed using the prebuilt docker images. The `mounter` dSpace controller will run as part of the example digis (see [mock digis](#digi-development)).  

**Digi library in Python.** Install the dev release from the repo `cd ./runtime/driver/digi/; pip install -e .` Or from PyPI: `pip install digi=0.1.6`. The library is used in [digi development](#digi-development).

**dSpace CLI (dq).** Run `make dq` to install the dev release with the /Makefile in this repo. The dSpace command line includes APIs for composition, digi aliasing, and image management etc. It is to be used  jointly with `kubectl` at running time (see [run-time operation](#runtime-operations)).

Other code / documents that can be useful for this artifact are the device stubs and the tutorial notebook which we will cover in what follows. 

> Note: to build the dSpace controllers and dq that are Go source, you may need to pull / copy / link this repo under the $GOPATH/src/digi.dev/dspace. That is, create the directories digi.dev/dspace under $GOPATH and copy the content of this repo there and run the `make` commands in that repo.

### Digi Development

**Digi:** The basic building block in dSpace is called *digi*. Each digi has a *model* and a *driver*. A model consists of attribute-value pairs organized in a document (JSON) following a predefined *schema*. The model describes the desired and the current states of the digi; and the goal of the digi's driver is to take actions that reconcile the current states to the desired states.

**Programming driver:** Each digi's driver can only access its own model (think of it as the digi's "world view"). Programming a digi is conceptually very simple - manipulating the digi's model/world view (essentially a JSON document) plus any other actions to affect the external world (e.g., send a signal to a physical plug, invoke a web API, send a text messages to your phone etc.). The dSpace's runtime will handle the rest, e.g., syncing states between digis' world views when they are composed.

Example `Room` digivice:
```python
from digi import on
from digi.view import TypeView, DotView

# invoked upon mount or control attributes changes
@on.mount
@on.control
def handle_brightness(model):  
    # chained transformation of model
    with TypeView(model) as tv, DotView(tv) as dv: 
      
        # control attribute for room brightness 
        rb = dv.room.control.brightness        
        
        # if no lamps brightness status set to 0
        rb.status = 0
        if "lamps" not in dv:
            return
          
        # count active lamps
        active_lamps = [l for _, l in dv.lamps.items() 
                    if l.control.power.status == "on"]
        
        # iterate and set active lamp brightness
        for lamp in active_lamps:
            # room brightness is the sum of all lamps
            room_brightness.status += \
            lamp.control.brightness.status 
            
            # divide intended brightness across lamps
            lamp.control.brightness.intent = \
            room_brightness.intent / len(active_lamps)
            
    # At the closing of the "with" clause, changes on 
    # DotView will be applied to the TypeView and then 
    # to the model.

if __name__ == '__main__':
    digi.run()
```

### Run-time Operations

**Build and run:** After defining the digi's schema and programing its driver, developers can build a *digi image* and push it to a digi repository for distribution. Users can then pull the digi image, run it on dSpace, and interact with the digi by updating its model, e.g., specifying its desired states.

To create, build, push, run, and compose digis, refer to the [QuickStart](#quickstart).

#### Using Dq

```bash
$ dq

Command-line dSpace manager.

Usage:
  dq [command]

Available Commands:
  alias       Create a digi alias
  build       Build a digi image
  help        Help about any command
  image       List available digi images
  log         Print log of a digi driver
  mount       Mount a digivice to another digivice
  pipe        Pipe a digilake's input.x to another's output.y
  pull        Pull a digi image
  push        Push a digi image
  rmi         Remove a digi image
  run         Run a digi given kind and name
  stop        Stop a digi given kind and name

Flags:
  -h, --help    help for dq
  -q, --quiet   Hide output

Use "dq [command] --help" for more information about a command.
```

> Note: the dq command line in this artifact relies on the /mocks/Makefile to function properly. When you try to run / build / compose / ... digis, make sure you run dq in the directory /mocks.

**Mock digis.** `/mocks` contains example digis that cover some of the scenarios at S6.2 that can be run/tested *without* actual physical devices.

**Device stubs.** `/stub` includes examples on interacting with physical devices and data frameworks, e.g., tuyapi, lifx, object recognition on video stream etc.

### Benchmark

Below are instructions to replicate the setup and results in "S6.5 Performance Benchmarks" in the paper. The scripts used in this setup can be found in [/benchmarks](https://github.com/digi-project/sosp21-artifact/blob/master/benchmarks/Makefile).

#### Local setup
```
     PHY        |     DSPACE     |      PHY
human input --> | room -- lamp --|-- lifx lamp -> actuate
                |      \_ cam  --|-- wyze cam  <- signal
    observe <-- |          |     |                              
                |      \_ scene  |                            
   [on-prem]    |    [on-prem]   |   [on-prem]
```
* Send a single request updating the room's `control.brightness.intent`
* Repeat it `K=3` times and collect metrics (below)
* Runtime (apiserver, etcd, digis) and the cli are run locally on the same machine

#### Metrics

* E2E latency (`E2E`): time between client send a request to update an intent until the client sees the status is set equal to the intent
* Request latency (`RT`): time to complete and respond to a client request
* Time-to-fulfillment (`TTF`): time it takes to full-fill/reconcile an intent
* Forward propagation time (`FPT`): time for intent to reach the device
* Backward propagation time (`BPT`): time for status to reach the root digi
* Device actuation time (`DT`): time for the device to actuate according to the set-point

> `TTF = FPT + BPT + DT`

To measure:
* `E2E`: measured at the CLI, the elapsed time between the request submission to the status update (both at the parent)
* `RT`: measured at the CLI, the elapsed time between the request submission to receiving the response
* `FPT`: measured with the timestamps at the root (when the intent is written) and the leaf digi (after setting the device's setpoint)
* `BPT`: measure the timestamps at the leaf (when the status update is received at the device) and the root digi (after setting the root's status)
* `DT`: measure at the leaf digi for the elapsed time between setting the device setpoint and receiving its status update

#### Remote setup
```
     PHY        |     DSPACE     |      PHY
human input --> | room -- lamp --|-- lifx lamp -> actuate
                |      \_ cam  --|-- wyze cam  <- signal
    observe <-- |          |     |                              
                |      \_ scene  |                            
   [on-prem]    |     [cloud]    |   [on-prem]
```
* Same as the local setup except the runtime components run in the cloud

#### Metrics

* Same as in the local setup; plus:
* Network latency (in-band or out-of-band/ping measurements)
* Bandwidth consumption (total bytes), measured at the network interface on the cloud machine

#### Hybrid setup
```
     PHY        |      DSPACE       |      PHY
human input --> | room -- lamp ---- |-- lifx lamp -> actuate
                |     \   _ _ _ _ _ |
                |      \_|__ cam  --|-- wyze cam  <- signal
    observe <-- |        |    |     |                              
                |      \_|__ scene  |                            
   [on-prem]    |[cloud] | [on-prem]|   [on-prem]
```
* Same as the remote setup except the cam and scene digis are run on-prem.
* The hybrid setup requires running a k8s cluster spanning two regions (on-prem and on-cloud) and can be done by registering your local node as a k8s worker to a master running in the cloud (e.g., using [kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/)).

#### Metrics
* ditto


> Contact silvery@eecs.berkeley.edu if you have questions and suggestions.
