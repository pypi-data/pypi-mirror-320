
import pickle
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate as sip
from astropy.io import fits

from pandeia.engine.calc_utils import (
    build_default_calc,
)
from pandeia.engine.instrument_factory import InstrumentFactory
from pandeia.engine.perform_calculation import perform_calculation

from gen_tso.pandeia_io import get_configs
import gen_tso.pandeia_io as jwst
from gen_tso.utils import ROOT


def get_throughputs(calc, filter_name):
    wl = np.arange(0.5, 15.001, 0.0002)
    qe = {}
    calculation = calc.calc
    if calc.mode == 'bots':
        disperser, filter = filter_name.split('/')
        calculation['configuration']['instrument']['disperser'] = disperser
    else:
        filter = filter_name
    calculation['configuration']['instrument']['filter'] = filter
    inst = InstrumentFactory(
        config=calculation['configuration'], webapp=True,
    )
    qe[filter_name] = inst.get_total_eff(wl)
    return wl, qe


def mask_througput(wl_arr, qe, wl_response, response, thin=50, threshold=1e-3):
    """
    i = 6
    norm = np.amax(fluxes[i]) / np.amax(qe[filters[i]])
    wl_mask, qe_mask = masked_througput(wl_arr, qe[filters[i]], wl[i], fluxes[i]/norm)
    """
    # resample fluxes into wl_arr
    interp_resp = sip.interp1d(
        wl_response, response, bounds_error=False, fill_value=0.0,
    )
    # mask fluxes
    resp_mask = interp_resp(wl_arr) > threshold
    masked_response = qe * resp_mask

    # add margin of 1 before and after the mask edges
    edges = np.where(np.ediff1d(resp_mask*1))[0]

    # decimate
    mask = np.zeros(len(wl_arr), bool)
    mask[::thin] = True
    mask &= resp_mask
    mask[edges] = True
    mask[edges+1] = True
    return wl_arr[mask], masked_response[mask]


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def acquisition_throughputs():
    #insts = get_configs(obs_type='spectroscopy')
    insts = get_configs(obs_type='acquisition')

    inst = insts[3]
    instrument = inst['instrument'].lower()
    mode = inst['mode']
    telescope = 'jwst'
    calculation = build_default_calc(telescope, instrument, mode)

    throughputs = {}
    qe = {}
    #if instrument == 'niriss':
    #    filters = ['imager', 'nrm']
    #    key = 'aperture'
    #else:
    filters = list(inst['filters'])
    key = 'filter'
    if instrument == 'miri':
        wl = np.arange(4.5, 28.001, 0.0002)
    else:
        wl = np.arange(0.5, 15.001, 0.0002)
    for filter in filters:
        calculation['configuration']['instrument'][key] = filter
        ins = InstrumentFactory(
            config=calculation['configuration'], webapp=True,
        )
        qe[filter] = ins.get_total_eff(wl)

        threshold = 1e-5 if filter=='fnd' else 1e-3
        wl_mask, qe_mask = mask_througput(
            wl, qe[filter], wl, qe[filter], thin=50, threshold=threshold,
        )
        throughputs[filter] = {'wl': wl_mask, 'response': qe_mask}

    all_throughputs = {}
    for subarray in list(inst['subarrays']):
        all_throughputs[subarray] = throughputs
    t_file = f'../data/throughputs/throughputs_{instrument}_{mode}.pickle'
    with open(t_file, 'wb') as handle:
        pickle.dump(all_throughputs, handle, protocol=pickle.HIGHEST_PROTOCOL)

    plt.figure(0)
    plt.clf()
    for filter, throughput in throughputs.items():
        plt.plot(throughput['wl'], throughput['response'], label=filter)
    plt.ylim(0, 1)
    plt.legend(loc='best')



def generate_all_nirspec_throughputs():
    insts = get_configs(obs_type='spectroscopy')

    inst = insts[2]
    instrument = inst['instrument'].lower()
    mode = inst['mode']
    telescope = 'jwst'
    calculation = build_default_calc(telescope, instrument, mode)

    readout = 'nrsrapid'

    #calc = jwst.Calculation(instrument, mode)
    scene = jwst.make_scene(
        sed_type='flat', sed_model='flam',
        norm_band='2mass,ks', norm_magnitude=15.0,
    )
    filters = inst.get_configs('filters')
    subarrays = inst.get_configs('subarrays')

    nint = 1
    ngroup = 2

    throughputs = {}
    for subarray in subarrays:
        throughputs[subarray] = {}
        for grating in filters:
            disperser, filter = grating.split('/')
            print(subarray, disperser, filter)
            try:
                calc.perform_calculation(
                    nint, ngroup, filter, readout, subarray, disperser,
                )
            except:
                print(
                    f'Pandeia failed for: {instrument}, {mode}, '
                    f'{subarray}, {disperser}, {filter}'
                )
                continue
            wave, flux = calc.report['1d']['extracted_flux']
            wl_arr, qe = get_throughputs(calc, grating)

            norm = np.amax(flux) / np.amax(qe[grating])
            wl_mask, qe_mask = mask_througput(
                wl_arr, qe[grating], wave, flux/norm, thin=50,
            )
            throughputs[subarray][grating] = {'wl': wl_mask, 'response': qe_mask}

    t_file = f'../data/throughputs/throughputs_{instrument}_{mode}.pickle'
    with open(t_file, 'wb') as handle:
        pickle.dump(throughputs, handle, protocol=pickle.HIGHEST_PROTOCOL)


def generate_all_nircam_throughputs():
    dets = jwst.generate_all_instruments()
    scene = jwst.make_scene(
        sed_type='flat', sed_model='flam',
        norm_band='2mass,ks', norm_magnitude=15.0,
    )

    # LW Grism Time Series
    det = dets[2]
    instrument = 'nircam'
    mode = 'lw_tsgrism'
    pando = jwst.PandeiaCalculation(instrument, mode)
    pando.calc['scene'][0] = scene
    calculation = pando.calc
    filters = pando.get_configs('filters')
    subarrays = pando.get_configs('subarrays')
    ngroup = 2
    nint = 1

    throughputs = {}
    for subarray in subarrays:
        throughputs[subarray] = {}
        for filter in filters:
            print(subarray, filter)
            try:
                pando.perform_calculation(
                    nint, ngroup, filter=filter, subarray=subarray,
                )
            except:
                print(
                    f'Pandeia failed for: {instrument}, {mode}, '
                    f'{subarray}, {filter}'
                )
                continue
            wave, flux = pando.report['1d']['extracted_flux']
            wl_arr, qe = get_throughputs(pando, filter)

            norm = np.amax(flux) / np.amax(qe[filter])
            wl_mask, qe_mask = mask_througput(
                wl_arr, qe[filter], wave, flux/norm, thin=50,
            )
            throughputs[subarray][filter] = {'wl': wl_mask, 'response': qe_mask}

    t_file = f'{ROOT}data/throughputs/throughputs_{instrument}_{mode}.pickle'
    with open(t_file, 'wb') as handle:
        pickle.dump(throughputs, handle, protocol=pickle.HIGHEST_PROTOCOL)


    # SW Grism Time Series
    det = dets[3]
    instrument = 'nircam'
    mode = 'sw_tsgrism'
    pando = jwst.PandeiaCalculation(instrument, mode)
    calculation = pando.calc
    apertures = list(det.apertures)
    filters = pando.get_configs('filters')
    subarrays = pando.get_configs('subarrays')
    disperser = calculation['configuration']['instrument']['disperser']
    readout = calculation['configuration']['detector']['readout_pattern']
    ngroup = 2
    nint = 1

    throughputs = {}
    aperture = apertures[3]
    for subarray in subarrays:
        throughputs[subarray] = {}
        for filter in filters:
            print(aperture, disperser, filter, subarray)
            try:
                pando.perform_calculation(
                    ngroup, nint, filter=filter, subarray=subarray,
                )
            except:
                print(
                    f'Pandeia failed for: {instrument}, {mode}, '
                    f'{subarray}, {disperser}, {filter}'
                )
                continue
            wave, flux = pando.report['1d']['extracted_flux']
            wl_arr, qe = get_throughputs(pando, filter)

            norm = np.amax(flux) / np.amax(qe[filter])
            wl_mask, qe_mask = mask_througput(
                wl_arr, qe[filter], wave, flux/norm, thin=50,
            )
            throughputs[subarray][filter] = {'wl': wl_mask, 'response': qe_mask}

    t_file = f'{ROOT}data/throughputs/throughputs_{instrument}_{mode}.pickle'
    with open(t_file, 'wb') as handle:
        pickle.dump(throughputs, handle, protocol=pickle.HIGHEST_PROTOCOL)


def generate_all_miri_throughputs():
    instrument = 'miri'
    mode = 'lrsslitless'
    readout = 'fastr1'
    disperser = 'p750'

    calc = jwst.Calculation(instrument, mode)
    calc.set_scene(
        sed_type='flat', sed_model='flam',
        norm_band='2mass,ks', norm_magnitude=15.0,
    )
    filters = calc.get_configs('filters')
    subarrays = calc.get_configs('subarrays')

    nint = 1
    ngroup = 2

    throughputs = {}
    for subarray in subarrays:
        filter = 'None'
        throughputs[subarray] = {}
        calc.perform_calculation(
            nint, ngroup, filter, readout, subarray, disperser,
        )
        wave, flux = calc.report['1d']['extracted_flux']
        wl_arr, qe = get_throughputs(calc, filter)

        norm = np.amax(flux) / np.amax(qe[filter])
        wl_mask, qe_mask = mask_througput(
            wl_arr, qe[filter], wave, flux/norm, thin=250,
        )
        throughputs[subarray][str(filter)] = {'wl': wl_mask, 'response': qe_mask}

    t_file = f'../data/throughputs/throughputs_{instrument}_{mode}.pickle'
    with open(t_file, 'wb') as handle:
        pickle.dump(throughputs, handle, protocol=pickle.HIGHEST_PROTOCOL)


def generate_all_niriss_throughputs():
    instrument = 'niriss'
    mode = 'soss'
    readout = 'nisrapid'

    calc = jwst.Calculation(instrument, mode)
    disperser = calc.get_configs('dispersers')[0]
    calc.set_scene(
        sed_type='flat', sed_model='flam',
        norm_band='2mass,ks', norm_magnitude=15.0,
    )
    filters = calc.get_configs('filters')
    subarrays = calc.get_configs('subarrays')

    nint = 1
    ngroup = 2

    # Could not generate the throughputs from pandeia
    # For the moment will use this digitized version from the jdocs
    wl, through = np.loadtxt(
        '../data/soss_GR700XD_throughput_etcv2.0_digitized.txt', unpack=True,
    )
    wl_o1 = wl[0:250]
    through_o1 = through[0:250]
    # Only for filter=clear, subarray=substrip256 v full
    wl_o2 = wl[250:]
    through_o2 = through[250:]

    fd = fits.getdata('../etc_files/wb_soss_o2/lineplot/lineplot_extracted_flux.fits')
    wave = fd['WAVELENGTH']
    flux = fd['extracted_flux']

    norm = np.amax(flux) / np.amax(through_o2)
    wl_mask_o2, qe_mask_o2 = mask_througput(
        wl_o2, through_o2, wave, flux/norm, thin=1,
    )

    plt.clf()
    plt.plot(wl_o2, through_o2, dashes=(8,2), lw=1.5, color='k')
    plt.plot(wl_mask, qe_mask, color='r', lw=1.75, alpha=0.75)


    throughputs = {}
    tmp_through = {}
    for subarray in subarrays:
        throughputs[subarray] = {}
        for filter in filters:
            print(subarray, disperser, filter)
            try:
                calc.perform_calculation(
                    nint, ngroup, filter, readout, subarray, disperser,
                )
            except:
                print(
                    f'Pandeia failed for: {instrument}, {mode}, '
                    f'{subarray}, {disperser}, {filter}'
                )
                continue

            wave, flux = calc.report['1d']['extracted_flux']
            #wl_arr, qe = get_throughputs(calc, [filter])
            tmp_through[filter] = {'wl': wave, 'flux': flux}
            if filter == 'clear':
                qe = np.copy(through_o1)
            elif filter == 'f277w':
                wl_min = np.amin(tmp_through['f277w']['wl'])
                wl_mask = tmp_through['clear']['wl']>= wl_min
                scale = (
                    tmp_through['f277w']['flux'] /
                    tmp_through['clear']['flux'][wl_mask]
                )
                interp_qe = sip.interp1d(
                    wave, scale, bounds_error=False, fill_value=0.0,
                )
                qe = through_o1 * interp_qe(wl_o1)

            norm = np.amax(flux) / np.amax(qe)
            wl_mask, qe_mask = mask_througput(
                wl_o1, qe, wave, flux/norm, thin=1,
            )
            throughputs[subarray][filter] = {'wl': wl_mask, 'response': qe_mask}

    # Add order 2
    filter = 'clear'
    for subarray in subarrays:
        if subarray == 'substrip96':
            continue
        print(subarray)
        throughputs[subarray][filter]['order2'] = {
            'wl': wl_mask_o2, 'response': qe_mask_o2,
        }

    t_file = f'../data/throughputs/throughputs_{instrument}_{mode}.pickle'
    with open(t_file, 'wb') as handle:
        pickle.dump(throughputs, handle, protocol=pickle.HIGHEST_PROTOCOL)


# compare

t_file = '../data/throughputs/throughputs_miri_lrsslitless.pickle'
t_file = f'{ROOT}data/throughputs/throughputs_nircam_lw_tsgrism.pickle'
t_file = '../data/throughputs/throughputs_nirspec_bots.pickle'
t_file = '../data/throughputs/throughputs_niriss_soss.pickle'

with open(t_file, 'rb') as handle:
    data = pickle.load(handle)

subarrays = list(data.keys())
filters = list(data[subarrays[0]].keys())

#filter = filters[0]
plt.figure(2)
plt.clf()
for i,subarray in enumerate(subarrays):
    for filter in filters:
        wl = data[subarray][filter]['wl']
        response = data[subarray][filter]['response'] * (1+i*0.03)
        plt.plot(wl, response, lw=1.5, label=subarray + ' / ' + filter)
#plt.xlim(0.9*np.amin(wl_mask), 1.1*np.amax(wl_mask))
#plt.legend(loc='best')
plt.ylim(bottom=0.0)
plt.title(filter)
plt.xlabel('wavelength')
plt.ylabel('throughput')
plt.tight_layout()





