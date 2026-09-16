import json
import numpy as np
import itertools

class ReadDataCard():
    """
    Gives all the data necessary to compute the NLL.
    This, no one but me should have to care about for now.
    The nominal measurements and predictions, the corresponding nuisance parameters and all SMEFT operator contributions.
    This code is far from optimized. Should be fine though, since it really is used once at the beginning to get the data.
    Currently the order of observation and prediction is required to be the same, I should change that. 
    """
    def __init__(self, str):
        with open(str, "r") as read_file:
            datain = json.load(read_file)

        self._identifiers = []
        self._names = []

        self._bins = {}
        self._bin_width = {}
        self._luminosity = {}
        self._decaymode = {}
        self._subids = {}

        self._measurements = {}
        self._backgrounds = {}
        self._predictions  = {}
        self._meas_modifiers = {}
        self._bkg_modifiers = {}
        self._theo_modifiers = {}
        self._wilsons = {}
        # PATCHED-2: optional published within-observable bin-to-bin correlation
        self._bin_corr = {}
        
        for observation, prediction in zip(datain['observations'], datain['predictions']):
            nbins = len(observation['Meas']['data'])
            obs_id = observation['ID']
            self._identifiers.append(obs_id)
            self._names.append(observation['name'])
            sub_ids = []

            for i in range(nbins):
                cid = f"{obs_id}^_^{i+1}"
                sub_ids.append(cid)
                self._bin_width[cid] = observation.get('bin_widths', [1.0])[i]
                self._luminosity[cid] = observation.get('Luminosity', [1.0])[0]
                self._decaymode[cid] = observation.get('Decay', [1.0])
                self._bins[cid] = i
                self._measurements[cid] = observation['Meas']['data'][i]
                self._backgrounds[cid] = observation['Bkg']['data'][i]
                self._predictions[cid] = prediction['data'][i]
                self._meas_modifiers[cid] = observation['Meas']['modifiers']
                self._bkg_modifiers[cid] = observation['Bkg']['modifiers']
                self._theo_modifiers[cid] = observation['modifiers']
                self._wilsons[cid] = prediction['modifiers']

            # PATCHED-2: optional published within-observable bin-to-bin CORRELATION
            # matrix (unit diagonal), n_bins x n_bins, row-major. Same optional-key
            # idiom as bin_widths / Luminosity / Decay above.
            self._bin_corr[obs_id] = observation.get('bin_correlation', None)

            self._subids[obs_id] = sub_ids        
        self.max_decay = max([len(s) for s in self._decaymode.values()])

        # This part can probably be done better
        self._all_modifiers = {}
        for modifiers in [self._meas_modifiers, self._bkg_modifiers]:
            for key, value in modifiers.items():
                self._all_modifiers.setdefault(key, []).extend(value)  

    @property
    def identifiers(self):
        return self._identifiers

    @property
    def names(self):
        return self._names

    @property
    def all_identifiers(self):
        all_ids = [sub_id for id in self._identifiers for sub_id in self._subids[id]]
        return all_ids

    @property
    def measurements(self):
        return self._measurements
    
    @property
    def decay(self):
        return self._decaymode

    @property
    def luminosity(self):
        return self._luminosity

    @property
    def backgrounds(self):
        return self._backgrounds

    @property
    def nchannels(self):
        return len(self._measurements)
    
    @property
    def ndata(self):
        return len(self.all_identifiers)
        
    def get_bin_width(self, ID):
        width = self._bin_width[ID]
        return width

    def nuis_order_and_types(self):
        all_nuis = self.all_mods(self._all_modifiers)
        nuis_order = {np: i for i, (np, _) in enumerate(all_nuis.items())}
        nuis_types = all_nuis
        return nuis_order, nuis_types
    
    @property
    def nuis_order(self):
        return self.nuis_order_and_types()[0]

    @property
    def nuis_types(self):
        return self.nuis_order_and_types()[1]

    @property
    def WC_order(self):
        all_WCs = self.all_mods(self._wilsons)
        wc_order = {wc: i for i, wc in enumerate(all_WCs)}
        return wc_order

    def higgs_names(self):
        higgs_names = ["csgf", "csvbf", "cswh", "cszh", "cstth", "csTEVgf", "csTEVvbf", "csTEVwh", "csTEVzh", "csTEVtth", "cs7gf", "cs7vbf", "cs7wh", "cs7zh", "cs7tth", "cs8gf", "cs8vbf", "cs8wh", "cs8zh", "cs8tth", "cs13gf", "cs13vbf", "cs13wh", "cs13zh", "cs13tth", "cs13bbh", "cs14gf", "cs14vbf", "cs14wh", "cs14zh", "cs14tth", "cs14bbh", "cs27gf", "cs27vbf", "cs27wh", "cs27zh", "cs27tth", "cssiggf", "cssigvbf", "cssigwh", "cssigzh", "cssigtth"]
        all_names = self.all_mods(self._wilsons)
        higgs_names = [name for name in all_names if name in higgs_names]
        return higgs_names

    def get_bin(self, ID):
        nbins = self._bins[ID]
        return nbins

    @staticmethod
    def _mod_key(m):
        return f"{m.get('type')}{m.get('label','')}{m.get('energy', '')}{m.get('name')}"

    def _obs_bkg_frac(self, ID):
        return self.get_obs(ID) / 100, self.get_bkg(ID) / 100

    def _get_data(self, ID , type):
        data = {}
        bin_index = self.get_bin(ID)
        modifiers = type[ID]
        if type == self._all_modifiers:
            data = {self._mod_key(m): m.get('data')[bin_index] for m in modifiers}
        elif type == self._wilsons:
            if len(self._decaymode[ID]) > 1:
                data = {m.get('name'): m.get('data') if len(m.get('data')) > 1 else m.get('data')[0] for m in modifiers}
            else:
                data = {m.get('name'): m.get('data')[bin_index] for m in modifiers}
        return data

    def WC_data(self):
        WC_data = {}
        for id in self.all_identifiers:
            bin = self.get_bin(id)
            WC_data[id] = {m['name']: m['data'][bin] for m in self._wilsons[id]}
        return WC_data

    def float_to_list(self, val, n_decays=1):
        if isinstance(val, list):
            if len(val) < n_decays:
                val.extend([0.0] * (n_decays - len(val)))
                return val
            else:
                return val
        else:
            return [val] * n_decays
    
    def _get_wilsons(self, type, ID):
        all_WCs = self.all_mods(self._wilsons)
        sub_WCs = {wc: type for wc, value in all_WCs.items() if value == type}
        order = {wc: i for i, wc in enumerate(sub_WCs)}
        wilson_data = [0] * len(sub_WCs)
        wilson_types = [0] * len(sub_WCs)
        wc_data = self._get_data(ID, self._wilsons)
        n_decays = max(len(self.float_to_list(wc_data.get(wc, 0.0))) for wc in order)
        for wc, index in order.items():
            wilson_types[index] = sub_WCs[wc]
            data = self.float_to_list(wc_data.get(wc, 0.0), n_decays)
            wilson_data[index] = data

        return wilson_data, wilson_types
    
        
    def get_nuis_types(self, ID):
        return self._get_nuisances(ID)[1]
        
    def theo_unc(self, ID):
        bin_index = self.get_bin(ID)
        obs_data, obs_bkg = self._obs_bkg_frac(ID)
        if (obs_data == 0) & (obs_bkg == 0):
            theo_unc = [self.mod_value(m, bin_index) for m in self._theo_modifiers[ID]]
        else:
            theo_unc = [self.mod_value(m, bin_index) * (obs_data - obs_bkg)
                        for m in self._theo_modifiers[ID]]
        return theo_unc
    
    @staticmethod
    def mod_value(m, bin_index):
        """PATCHED-3: unified per-bin modifier lookup.

        Two accepted forms:
          bin-scalar : {"bin": 3, "data": 0.42}   (or "data": [0.42])
          array      : {"data": [v0, v1, ..., vn-1]}      -- positional, as before

        The array branch keeps the historical out-of-range -> 0.0 behaviour so
        existing datacards read identically. The bin-scalar branch validates its
        index, because a wrong `bin` would otherwise contribute silently nothing.
        """
        if 'bin' in m:
            b = m['bin']
            if not isinstance(b, int) or b < 0:
                raise ValueError(
                    f"modifier {m.get('name')!r} has invalid bin={b!r}; "
                    f"expected a non-negative integer")
            d = m.get('data', 0.0)
            if isinstance(d, (list, tuple)):
                if len(d) != 1:
                    raise ValueError(
                        f"modifier {m.get('name')!r} declares bin={b} so data must be "
                        f"a scalar or a length-1 list, got length {len(d)}")
                d = d[0]
            return float(d) if b == bin_index else 0.0
        d = m.get('data', [0.0])
        if not isinstance(d, (list, tuple)):
            raise ValueError(
                f"modifier {m.get('name')!r} has scalar data but no 'bin' key; "
                f"add \"bin\": <index> or give a full-length array")
        return d[bin_index] if bin_index < len(d) else 0.0

    def poiss_unc(self, ID):
        bin_index = self.get_bin(ID)
        poiss_unc = [self.mod_value(m, bin_index)
                     for m in self._all_modifiers[ID] if m['type'] == 'pois']
        return poiss_unc

    def stat_unc(self, ID):

        data_mod = self._meas_modifiers
        bkg_mod = self._bkg_modifiers
        bin_index = self.get_bin(ID)
        obs_data, obs_bkg = self._obs_bkg_frac(ID)

        if (obs_data == 0) & (obs_bkg == 0):
            stat_unc = [self.mod_value(m, bin_index) for m in data_mod[ID] if m['type'] == 'stat']
            stat_unc += [self.mod_value(b, bin_index) for b in bkg_mod[ID] if b['type'] == 'stat']
        else:
            stat_unc = [self.mod_value(m, bin_index) * obs_data for m in data_mod[ID] if m['type'] == 'stat']
            stat_unc += [self.mod_value(b, bin_index) * obs_bkg for b in bkg_mod[ID] if b['type'] == 'stat']

        return stat_unc

# IMPORTANT NOTE: The way the code is written right now, the order of the nuisances is important, should fix. (Poisson, syst, stat)
    def syst_unc(self, ID):
        
        order, types = self.nuis_order_and_types()
        data_mod = self._meas_modifiers
        bkg_mod = self._bkg_modifiers
        bin_index = self.get_bin(ID)
        obs_data, obs_bkg = self._obs_bkg_frac(ID)

        if ID not in data_mod or ID not in bkg_mod:
            raise KeyError(f"ID {ID} not found in data_mod or bkg_mod")

        data = {}
        for m, b in itertools.zip_longest(data_mod[ID], bkg_mod[ID], fillvalue=None):                
            if m is None:
                m = {'data': [0.0], 'type': b.get('type', ''), 'label': b.get('label', ''), 'energy': b.get('energy', ''), 'name': b.get('name', '')}
            if b is None:
                b = {'data': [0.0], 'type': m.get('type', ''), 'label': m.get('label', ''), 'energy': m.get('energy', ''), 'name': m.get('name', '')}
            if m["type"] == "syst":
                key = self._mod_key(m)
                m_data = self.mod_value(m, bin_index)
                b_data = self.mod_value(b, bin_index)
                if (obs_data == 0) & (obs_bkg == 0):
                    data[key] = m_data
                else:
                    data[key] = np.sqrt((m_data * obs_data) ** 2 + (b_data * obs_bkg) ** 2 - 2 * 0.99 * (m_data * obs_data) * (b_data * obs_bkg))

        all_nuis = self.all_mods(self._all_modifiers)
        nuis_data = [0.0] * len(all_nuis)
        for nuisance in all_nuis:
            nuis_index = order.get(nuisance, None)
            if nuis_index is not None:
                nuis_data[nuis_index] = data.get(nuisance, 0.0)
        return nuis_data

    def all_mods(self, type):
        if type == self._all_modifiers:
            all_mods = {self._mod_key(m): m.get('type') for id in self.all_identifiers for m in type.get(id)}
        elif type == self._wilsons:
            all_mods = {m.get('name'): m.get('type', 'WC') for id in self.all_identifiers for m in type.get(id)}
        return dict(sorted(all_mods.items()))

    def get_WC_data(self, type, ID):
        return self._get_wilsons(type, ID)[0]
    
    def get_WC_types(self, type, ID):
        return self._get_wilsons(type, ID)[1]

    def get_obs(self, ID):
        return self._measurements[ID]
    
    def get_bkg(self, ID):
        return self._backgrounds[ID]

    def get_pred(self, ID):
        return self._predictions[ID]

    def bin_correlation(self, ID):
        """PATCHED-2: published within-observable correlation matrix, or None."""
        return self._bin_corr.get(ID, None)

    def get_subids(self, ID):
        return self._subids[ID]

    @property
    def get_data_WCs(self):
        all_WCs = self.all_mods(self._wilsons)
        sub_WCs = {wc: type for wc, value in all_WCs.items() if value == "WC"}
        return sub_WCs
        