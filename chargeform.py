#Plots the waveforms and outputs the times for event with ~0 charge
import h5py
import numpy as np
import matplotlib.pyplot as plt
from zmq_client import adc_to_voltage

print "start program"

def get_times(y, fraction=0.4):
    """
    Returns pulse times in `y` by looking for the pulse
    to cross a constant fraction `fraction` of the pulse height in each
    waveform. `y` should be a 2 dimensional array with shape (N,M) where
    N is the number of waveforms, and M is the number of samples per
    waveform.
    """
    # samples below threshold
    mask1 = y > np.min(y,axis=-1)[:,np.newaxis]*fraction
    # samples before the minimum
    mask2 = np.arange(y.shape[1]) < np.argmin(y,axis=-1)[:,np.newaxis]

    # right side of threshold crossing
    r = y.shape[1] - np.argmax((mask1 & mask2)[:,::-1], axis=-1)
    r[r == 0] = 1
    r[r == y.shape[1]] = y.shape[1] - 1
    l = r - 1

    yl = y[np.arange(y.shape[0]),l]
    yr = y[np.arange(y.shape[0]),r]

    return (np.min(y,axis=-1)*fraction - yl)/(yr-yl) + l

def find_charge(v):
    area = np.trapz(v, axis=-1)
    charge = -adc_to_voltage(area)*1e3/2/50.0
    return charge

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', dest='output', default='low_q_time.txt')
    parser.add_argument('filenames', nargs='+', help='input files')
    args = parser.parse_args()

    g = []
    other = []
    for filename in args.filenames:
        with h5py.File(filename) as f:
            for i in range(100000):
                dset = f['c2'][i]
                if find_charge(dset) < .01:
		    g.append(dset)
                   # h.append(get_times(dset, -10))
                else:
                    other.append(dset)

    h = get_times(g)
 
    if args.output:
        np.savetext(args.output, h, header='time')

    plt.figure()
    plt.plot(g)
    plt.title('Channel 2')

    plt.show()


