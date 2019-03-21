import ConfigSpace as CS
from .distribution import load_dist_dict


class Sampler:
    def __init__(self, validator, **kwargs):
        self.hps = {}
        for k, v in kwargs.items():
            if k in validator.parameters_:
                self.hps[k] = v
            else:
                ValueError("{} is an invalid key".format(k))
        self.validator = validator
        self._generate_config_space()

    def to_dict(self):
        output = {}
        for k, v in self.hps.items():
            output[k] = v.to_dict()
        return output

    def from_dict(self, p_dict):
        for k, v in p_dict.items():
            self.hps[k] = load_dist_dict(v)
        self._generate_config_space()

    def _generate_config_space(self):
        cs = CS.ConfigurationSpace()
        for name, dist in self.hps.items():
            dist.add_to_config_space(name, cs)
        self.config_space = cs

    def sample(self, size=1):
        configs = self.config_space.sample_configuration(size)
        if size == 1:
            configs = [configs]
        output = []
        for config in configs:
            config_dict = config.get_dictionary()
            for name, dist in self.hps.items():
                dist.post_process(name, config_dict)
            output.append(config_dict)
        return output
