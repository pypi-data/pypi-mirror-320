from asyncio import sleep
from datetime import datetime
from glob import glob
from os.path import join
from typing import List

from params_proto import ParamsProto, Flag
from termcolor import colored
from vuer.events import ClientEvent
from vuer.schemas import Box, span, Html, group

from vuer_envs.scripts.util.working_directory_context_manager import WorkDir


class Params(ParamsProto, cli_parse=False):
    """Script for collecting virtual reality demos.

    - [x] install collect_demo.py as a cli
    - [x] write params-proto for setting the work dir etc
    - [x] load an example scene (UR5)
    - [ ] add logic to glob and find all files in the directory
    - ask Yajjy to make a scene with a UR5 and a table
    - add ml-logger prefix/dir structure.
    - document in the docs / Notion page.
    """

    demo_prefix: str = f"lucidxr/lucidxr/datasets/lucidxr/poc/demos/ability/{datetime.now().strftime('%Y/%m/%d/%H.%M.%S')}/"

    wd: str = "."
    vuer_port = 8012

    scene_folder: str = ""
    scene_name: str = "scene"
    scene_file: str = join("{scene_folder}", "{scene_name}.mjcf.xml")

    asset_prefix: str = "http://localhost:{vuer_port}/static"
    assets: List[str] = None
    asset_paths: List[str] = None

    src: str = "{asset_prefix}/{scene_file}"
    src_path: str = "{wd}/{scene_file}"

    verbose = Flag(help="Print out the assets that are being loaded.")

    def __post_init__(self):
        for k, v in self.__dict__.items():
            if isinstance(v, str):
                value = v.format(**self.__dict__)
                setattr(self, k, value)

                if self.verbose:
                    print(f"{colored(k, 'cyan')}:\t{colored(value, 'yellow')}")

        with WorkDir(join(self.wd, self.scene_folder)):
            self.assets = glob("**/*.*", recursive=True)
            self.asset_paths = [join(self.asset_prefix, self.scene_folder, asset) for asset in self.assets]

        if self.verbose:
            print("Assets:")
            print(*self.assets, sep="\n")
            print("Asset Paths:")
            print(*self.asset_paths, sep="\n")


def main():
    args = Params()

    from vuer import Vuer, VuerSession
    from vuer.schemas import MuJoCo
    from ml_logger import logger

    logger.configure(args.demo_prefix)
    logger.job_started()
    print(logger.get_dash_url())

    vuer = Vuer(static_root=args.wd, port=args.vuer_port)

    box_state = "#23aaff"
    box_other = "#ff2323"

    @vuer.add_handler("ON_CLICK")
    async def on_click(event: ClientEvent, proxy: VuerSession):
        nonlocal box_state, box_other

        key = event.value["key"]
        print(f"Clicked: {key}")
        box_state, box_other = box_other, box_state
        print("State:", box_state)

    @vuer.add_handler("CAMERA_MOVE")
    async def on_mujoco_frame(event: ClientEvent, proxy: VuerSession):
        camera = event.value["camera"]

        logger.log(
            ts=event.ts,
            camera_matrix=camera["matrix"],
            flush=True,
            silent=True,
        )

    @vuer.add_handler("ON_MUJOCO_FRAME")
    async def on_mujoco_frame(event: ClientEvent, proxy: VuerSession):
        frame = event.value["keyFrame"]

        logger.log(
            ts=event.ts,
            **frame,
            flush=True,
            silent=True,
        )

    with WorkDir(args.wd):

        @vuer.spawn(start=True)
        async def main(proxy: VuerSession):
            # todo: add a ContribLoader to load the MuJoCo plugin.
            proxy.upsert @ MuJoCo(key="default-sim", src=args.src, assets=args.asset_paths)
            while True:
                proxy.upsert @ group(
                    Html(
                        span("Click Me!!"),
                        key="ctnr",
                        style={"width": 700, "fontSize": 20},
                    ),
                    Box(
                        args=[0.1, 0.1, 0.1],
                        key="demo-button",
                        material={"color": box_state},
                    ),
                    key="button-group-1",
                    position=[0, 0.5, 0],
                )

                await sleep(0.016)

    logger.job_completed()


if __name__ == "__main__":
    # Params.wd = "/Users/yajvanravan/Library/CloudStorage/GoogleDrive-yravan@mit.edu/.shortcut-targets-by-id/1UQnuWv4ICaE50w_nPTTNeZ1_YtRsswuX/lucidxr-assets/development/robots"
    Params.wd = "/Users/ge/Library/CloudStorage/GoogleDrive-ge.ike.yang@gmail.com/My Drive/lucidxr-assets/development/robots"
    Params.scene_name = "scene"
    Params.scene_folder = "universal_robots_ur5e"

    args = Params()

    main()
