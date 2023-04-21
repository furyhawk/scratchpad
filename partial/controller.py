from hydra.utils import instantiate


def runner(cfg):
    print(cfg)
    store = instantiate(cfg.store)
    print(store)
