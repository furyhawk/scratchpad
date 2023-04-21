# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved


from omegaconf import DictConfig

import hydra

from controller import runner


@hydra.main(version_base=None, config_path=".", config_name="config")
def main(cfg: DictConfig) -> None:
    runner(cfg)


if __name__ == "__main__":
    main()
